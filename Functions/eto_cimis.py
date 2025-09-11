import numpy as np
import pandas as pd

def eto_cimis(
    T_C,              # mean hourly air temperature (°C)
    ea_kPa,           # mean hourly vapor pressure, ea (kPa)
    Rn_Wm2,           # mean hourly net radiation, Rn (W m-2)
    U2_ms,            # mean hourly wind speed at 2 m, u2 (m s-1)
    Z_m,              # station elevation above MSL (m) - scalar or array broadcastable to inputs
    time_index=None,  # optional: DatetimeIndex aligned to inputs (hourly). If provided, daily ETo is returned by day.
    clip_negative_daily=True  # if True, negative daily totals (rare) are clipped to 0
):
    """
    Computes hourly reference ET (RET, mm/hr) and daily ETo (mm/day) using your CIMIS-style workflow.

    Equations implemented (exactly as provided):
      es = 0.6108 * exp((17.27*T) / (237.3 + T))
      VPD = es - ea
      Δ = 4098*es / (T + 237.3)^2
      P = 101.3 - 0.0115*Z + 5.44e-7*Z^2       # (NOTE: the symbol in your text used Δ, but this is barometric pressure P)
      γ = 0.000646 * (1 + 0.000946*T) * P
      W = Δ / (Δ + γ)
      NR = Rn / (694.5 * (1 - 0.000946) * T)   # (NOTE: used exactly as written)
      FU2 (night, Rn<=0): 0.125 + 0.0439*U
      FU2 (day,   Rn> 0): 0.030 + 0.0576*U
      RET = W*NR + (1 - W)*VPD*FU2
      Daily ETo = sum of 24 hourly RET

    Inputs can be numpy arrays/Series; shapes must be broadcast-compatible.
    If `time_index` is provided (hourly), returns a DataFrame with hourly and daily results.
    """
    # Convert to numpy arrays
    T = np.asarray(T_C, dtype=float)
    ea = np.asarray(ea_kPa, dtype=float)
    Rn = np.asarray(Rn_Wm2, dtype=float)
    U  = np.asarray(U2_ms, dtype=float)
    Z  = np.asarray(Z_m, dtype=float)

    # 1) Saturation vapor pressure (kPa)
    es = 0.6108 * np.exp((17.27 * T) / (237.3 + T))

    # 2) Vapor pressure deficit (kPa)
    VPD = es - ea

    # 3) Slope of saturation vapor pressure curve (kPa/°C)
    Delta = (4098.0 * es) / np.power(T + 237.3, 2.0)

    # 4) Barometric pressure, P (kPa)  [polynomial given in your notes]
    P = 101.3 - 0.0115 * Z + 5.44e-7 * (Z**2)

    # 5) Psychrometric constant, gamma (kPa/°C)
    gamma = 0.000646 * (1.0 + 0.000946 * T) * P

    # 6) Weighting function, W
    W = Delta / (Delta + gamma)

    # 7) Convert hourly net radiation from W m-2 to mm/hr (NR)
    #    EXACTLY as written in your formula:
    #    NR = Rn / (694.5 * (1 - 0.000946) * T)
    #    To avoid division-by-zero at T=0 °C, set NR=0 where T==0.
    denom = 694.5 * (1.0 - 0.000946) * T
    NR = np.zeros_like(Rn, dtype=float)
    safe = ~np.isclose(denom, 0.0)
    NR[safe] = Rn[safe] / denom[safe]
    # (Optional) If you prefer strict physical limits, you could also set NR<0 at night via Rn sign, but we keep formula as-is.

    # 8) Wind function FU2: day vs night by Rn sign
    FU2 = np.where(Rn <= 0.0, 0.125 + 0.0439 * U, 0.030 + 0.0576 * U)

    # 9) Hourly RET (mm/hr)
    RET = W * NR + (1.0 - W) * VPD * FU2

    # Prepare outputs
    if time_index is None:
        return {
            "RET_mm_per_hr": RET,
            "components": {
                "es_kPa": es,
                "VPD_kPa": VPD,
                "Delta_kPa_per_C": Delta,
                "P_kPa": P,
                "gamma_kPa_per_C": gamma,
                "W": W,
                "NR_mm_per_hr": NR,
                "FU2": FU2,
            }
        }

    # If a time index is provided, build a tidy DataFrame and produce daily sums
    # Expecting hourly frequency (or anything resample-able to 'D')
    if not isinstance(time_index, (pd.DatetimeIndex, pd.Series)):
        time_index = pd.to_datetime(time_index)

    df = pd.DataFrame(
        {
            "T_C": T,
            "ea_kPa": ea,
            "Rn_Wm2": Rn,
            "U2_ms": U,
            "RET_mm_hr": RET,
            "es_kPa": es,
            "VPD_kPa": VPD,
            "Delta_kPa_per_C": Delta,
            "P_kPa": P,
            "gamma_kPa_per_C": gamma,
            "W": W,
            "NR_mm_hr": NR,
            "FU2": FU2,
        },
        index=pd.DatetimeIndex(time_index)
    )

    # Daily ETo is sum of hourly RET over each day
    daily = df["RET_mm_hr"].resample("D").sum(min_count=1)
    if clip_negative_daily:
        daily = daily.clip(lower=0.0)

    return df, daily.rename("ETo_mm_day")
