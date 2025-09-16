import numpy as np
import pandas as pd

# ----- Expect df to be your dataframe with a DatetimeIndex named "time" -----
# Required columns (case-sensitive here, rename if needed):
# ['T_C','ea_kPa','es_kPa','Delta_kPa_per_C','gamma_kPa_per_C','U2_ms','Rn_Wm2']

def eto_hourly_fao56_asce_row(Rn_MJ_m2_h, T_C, u2, es, ea, delta, gamma, reference="short", is_daytime=None):
    """
    Hourly FAO-56 / ASCE Penman-Monteith.
    Inputs:
      - Rn_MJ_m2_h : net radiation [MJ m-2 h-1]
      - T_C        : air temperature [°C]
      - u2         : wind speed at 2 m [m s-1]
      - es, ea     : saturation & actual vapor pressure [kPa]
      - delta      : slope of svp curve [kPa °C-1]
      - gamma      : psychrometric constant [kPa °C-1]
      - reference  : 'short' (grass) or 'tall' (alfalfa)
      - is_daytime : True/False; if None, inferred from Rn>0
    Returns ET0 in mm h-1.
    """
    if is_daytime is None:
        is_daytime = (Rn_MJ_m2_h > 0.0)

    # Coefficients from ASCE Table 8-1
    if reference == "short":
        if is_daytime:
            Cn, Cd, G_over_Rn = 37.0, 0.24, 0.10
        else:
            Cn, Cd, G_over_Rn = 37.0, 0.96, 0.50
    else:  # tall
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
    return max(0.0, et0)  # clamp negatives at night

def compute_eto_hourly_and_daily(df: pd.DataFrame, reference="short"):
    # Convert Rn from W m-2 to MJ m-2 h-1 (1 W = 1 J s-1)
    Rn_MJ_m2_h = df['Rn_Wm2'] * 0.0036

    # Vectorized hourly ET0
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
            is_daytime=None  # inferred from Rn
        )
        for i in range(len(df))
    ]

    # Daily ET0 = sum of hourly ET0 (preferred when you start from hourly met)
    daily = df['PM-ETo_hourly_mm'].resample('D').sum().rename('PM-ETo_daily_mm')

    return df, daily

