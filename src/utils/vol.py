# mm/utils/vol.py
from functools import lru_cache

import pandas as pd


@lru_cache
def load_sigma(csv_path: str = "dailysigma.csv") -> pd.Series:
    """
    Return a Series indexed by pd.Timestamp with daily volatility forecasts from our NN model
    We'll add a fallback to a constant 1 % daily vol in the case the model can't be found.

    Params
    ----------
    csv_path : str
        CSV with columns: date,sigma  (e.g. 2023-01-03,0.0123)

    Returns
    -------
    pd.Series
        index = trading dates (tz-naive), values = sigma (float)
    """
    try:
        ser = pd.read_csv(csv_path,
                          parse_dates=["date"],
                          index_col="date")["sigma"]
        # We shouldn't need to fix the csv at all but just in case we'll dropna and sort
        return ser.dropna().sort_index()
    except FileNotFoundError:
        # Fallback: 252 business days of flat 1 % vol
        # For now, an arbitrary date   []
        idx = pd.date_range("2023-01-02", periods=252, freq="B")
        return pd.Series(0.01, index=idx, name="sigma")
