from utils.load_l2 import load_l2

def test_load_l2_columns_exist():
    df = load_l2("data/*.parquet")
    needed = {"time", "ask_price_1", "bid_price_1"}
    assert needed.issubset(df.columns)