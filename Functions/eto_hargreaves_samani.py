# Functions/eto_hs.py (second helper)
import numpy as np
import pandas as pd

def eto_hargreaves_samani(Tmax, Tmin, Tmean=None, Ra=None):
    """
    Hargreaves–Samani ETo using arrays/Series:
    ETo = 0.0023 * (Tmean + 17.8) * sqrt(Tmax - Tmin) * Ra

    Parameters
    ----------
    Tmax, Tmin : array-like (°C)
    Tmean : array-like or None (°C). If None, uses (Tmax+Tmin)/2.
    Ra : array-like (MJ m^-2 day^-1). REQUIRED.

    Returns
    -------
    np.ndarray of ETo (mm/day)
    """
    if Ra is None:
        raise ValueError("Ra is required (MJ m^-2 day^-1). Compute with solar_radiation().")
    Tmax = np.asarray(Tmax, dtype=float)
    Tmin = np.asarray(Tmin, dtype=float)
    if Tmean is None:
        Tmean = (Tmax + Tmin) / 2.0
    else:
        Tmean = np.asarray(Tmean, dtype=float)
    Ra = np.asarray(Ra, dtype=float)

    dtr = np.maximum(Tmax - Tmin, 0.0)
    return 0.0023 * (Tmean + 17.8) * np.sqrt(dtr) * Ra
