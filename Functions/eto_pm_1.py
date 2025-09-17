import math
from typing import Optional, Tuple
from datetime import datetime
import pandas as pd

def _solar_elevation_deg(
    ts: datetime, latitude_deg: float, longitude_deg: float, tz_offset_hours: float
) -> float:
    """
    NOAA-style approximate solar position:
    Returns solar elevation angle (degrees). > 0 => sun above horizon.
    ts should be a naive local time matching tz_offset_hours, or timezone-aware in its proper zone.
    """
    # Ensure we have naive UTC-ish components. We'll use local wall-clock but correct with tz offset.
    # Day of year:
    J = ts.timetuple().tm_yday
    # Fractional hour (local clock)
    fractional_hour = ts.hour + ts.minute/60 + ts.second/3600

    # Fractional year in radians
    gamma = 2.0 * math.pi / 365.0 * (J - 1 + (fractional_hour - 12.0) / 24.0)

    # Equation of time (minutes)
    eqtime = 229.18 * (
        0.000075
        + 0.001868 * math.cos(gamma)
        - 0.032077 * math.sin(gamma)
        - 0.014615 * math.cos(2 * gamma)
        - 0.040849 * math.sin(2 * gamma)
    )

    # Solar declination (radians)
    decl = (
        0.006918
        - 0.399912 * math.cos(gamma)
        + 0.070257 * math.sin(gamma)
        - 0.006758 * math.cos(2 * gamma)
        + 0.000907 * math.sin(2 * gamma)
        - 0.002697 * math.cos(3 * gamma)
        + 0.00148  * math.sin(3 * gamma)
    )

    # Time offset (minutes) to get true solar time
    time_offset = eqtime + 4.0 * longitude_deg - 60.0 * tz_offset_hours
    # True solar time (minutes)
    tst = fractional_hour * 60.0 + time_offset
    # Hour angle (degrees)
    ha = (tst / 4.0) - 180.0
    # Radians
    ha_rad = math.radians(ha)
    lat_rad = math.radians(latitude_deg)

    # Solar zenith angle
    cos_zenith = (
        math.sin(lat_rad) * math.sin(decl) +
        math.cos(lat_rad) * math.cos(decl) * math.cos(ha_rad)
    )
    # Clamp numeric noise
    cos_zenith = max(-1.0, min(1.0, cos_zenith))
    zenith_rad = math.acos(cos_zenith)
    elevation_deg = 90.0 - math.degrees(zenith_rad)
    return elevation_deg

def _infer_daytime(
    Rn_MJ_m2_h: float,
    timestamp: Optional[datetime] = None,
    latitude_deg: Optional[float] = None,
    longitude_deg: Optional[float] = None,
    tz_offset_hours: Optional[float] = None,
    daytime_hours: Tuple[int, int] = (6, 20),
) -> bool:
    """
    Tiered logic:
      1) If Rn > 0 => daytime.
      2) Else, if timestamp is provided:
         2a) If latitude/longitude/tz provided -> use solar elevation > 0
         2b) Else -> simple hour window (default 06:00–20:00)
      3) Else => night.
    """
    if Rn_MJ_m2_h > 0.0:
        return True

    if timestamp is None:
        return False

    if (latitude_deg is not None) and (longitude_deg is not None) and (tz_offset_hours is not None):
        try:
            elev = _solar_elevation_deg(timestamp, latitude_deg, longitude_deg, tz_offset_hours)
            return elev > 0.0
        except Exception:
            # Fallback to hour window if anything goes wrong
            pass

    start_h, end_h = daytime_hours
    hour = timestamp.hour
    return (start_h <= hour < end_h)


def eto_hourly_fao56_asce_row(
    Rn_MJ_m2_h: float,
    T_C: float,
    u2: float,
    es: float,
    ea: float,
    delta: float,
    gamma: float,
    reference: str = "short",
    is_daytime: Optional[bool] = None,
    *,
    # NEW optional args for time-based double-check:
    timestamp: Optional[datetime] = None,
    latitude_deg: Optional[float] = None,
    longitude_deg: Optional[float] = None,
    tz_offset_hours: Optional[float] = None,
    daytime_hours: Tuple[int, int] = (6, 20),
) -> float:
    """
    Hourly FAO-56 / ASCE Penman-Monteith with robust day/night detection.

    Day/night detection:
      - Primary: Rn_MJ_m2_h > 0 -> day
      - Secondary: if Rn <= 0 and timestamp provided:
            * If lat/lon/tz provided: solar elevation > 0 -> day
            * Else: hour in daytime_hours -> day
      - You can still override all of this by passing is_daytime explicitly.

    Returns ET0 in mm h-1.
    """
    if is_daytime is None:
        is_daytime = _infer_daytime(
            Rn_MJ_m2_h,
            timestamp=timestamp,
            latitude_deg=latitude_deg,
            longitude_deg=longitude_deg,
            tz_offset_hours=tz_offset_hours,
            daytime_hours=daytime_hours,
        )

    # ASCE Table 8-1 coefficients
    if reference == "short":
        if is_daytime:
            Cn, Cd, G_over_Rn = 37.0, 0.24, 0.10
        else:
            Cn, Cd, G_over_Rn = 37.0, 0.96, 0.50
    else:  # "tall"
        if is_daytime:
            Cn, Cd, G_over_Rn = 66.0, 0.25, 0.04
        else:
            Cn, Cd, G_over_Rn = 66.0, 1.70, 0.20

    G = G_over_Rn * Rn_MJ_m2_h  # MJ m-2 h-1

    # FAO-56/ASCE structure (0.408 converts MJ m-2 -> mm)
    num_rad  = 0.408 * delta * (Rn_MJ_m2_h - G)
    num_aero = gamma * (Cn / (T_C + 273.0)) * u2 * (es - ea)
    den      = delta + gamma * (1.0 + Cd * u2)

    et0 = (num_rad + num_aero) / den
    return max(0.0, et0)

def compute_eto_hourly_and_daily(
    df: pd.DataFrame,
    reference="short",
    latitude_deg: float = None,
    longitude_deg: float = None,
    tz_offset_hours: float = None,
    daytime_hours: tuple = (6, 20)
):
    """
    Computes hourly and daily ETo using FAO-56/ASCE method with smart day/night detection.
    Assumes index is datetime and that columns contain Rn, T_C, U2, es, ea, delta, gamma.
    """
    Rn_MJ_m2_h = df['Rn_Wm2'] * 0.0036
    df = df.copy()

    df['PM-ETo_hourly_mm'] = [
        eto_hourly_fao56_asce_row(
            Rn_MJ_m2_h=float(Rn_MJ_m2_h.iloc[i]),
            T_C=float(df['T_C'].iloc[i]),
            u2=float(df['U2_ms'].iloc[i]),
            es=float(df['es_kPa'].iloc[i]),
            ea=float(df['ea_kPa'].iloc[i]),
            delta=float(df['Delta_kPa_per_C'].iloc[i]),
            gamma=float(df['gamma_kPa_per_C'].iloc[i]),
            reference=reference,
            is_daytime=None,  # Let function decide based on Rn and time
            timestamp=df.index[i].to_pydatetime(),
            latitude_deg=latitude_deg,
            longitude_deg=longitude_deg,
            tz_offset_hours=tz_offset_hours,
            daytime_hours=daytime_hours
        )
        for i in range(len(df))
    ]

    # Daily sum from hourly values
    daily = df['PM-ETo_hourly_mm'].resample('D').sum().rename('PM-ETo_daily_mm')
    return df, daily
