import numpy as np
import pandas as pd

import pytest

from utils.load_l2 import load_l2
from utils.vol import load_sigma


def test_load_l2_columns_exist():
    df = load_l2("data/*.parquet")
    needed = {"time", "ask_price_1", "bid_price_1"}
    assert needed.issubset(df.columns)

# def test_date_alignment():
#     df = load_l2("data/AAPL_20120621.parquet")
#     trade_dates = (
#         pd.to_datetime(df["time"], unit="s")
#         .dt.floor("1D")
#         .unique()
#     )
#     bad_index = list(trade_dates) + [pd.Timestamp("1999-01-01")]  # <-- list, not Index
#     with pytest.raises(ValueError):
#         _ = load_sigma(index=bad_index, strict=True)