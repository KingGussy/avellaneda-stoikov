import pytest, pandas as pd
import numpy as np
from engine import FastQueue
from utils.load_l2 import load_l2
from utils.vol import load_sigma
from strategy.volguard_qimm import VolGuardQIMM
from features.l2_derived_features import realised_sigma, queue_imbalance

@pytest.mark.benchmark(group="day")
def test_full_day_backtest(benchmark):
    # ---------- One-time prep (excluded from timing) -----------------
    df = load_l2("data/AAPL_20120621.parquet")
    df["sigma_i"] = realised_sigma(df)
    df["qi"]      = queue_imbalance(df)
    df["mid"]     = 0.5 * (df["bid_price_1"] + df["ask_price_1"])

    bid1  = df["bid_price_1"].to_numpy()
    ask1  = df["ask_price_1"].to_numpy()
    mid           = df["mid"].to_numpy()
    ts            = df["time"].to_numpy()
    qi            = df["qi"].to_numpy()
    sigI          = df["sigma_i"].to_numpy()


    dir = df['direction'].to_numpy(dtype=np.int8)   # np. or dtype?
    typ = df["type"].to_numpy(dtype=np.int8)
    size = df["size"].to_numpy(dtype=np.int32)

    bid1_sz = df["bid_size_1"].astype(np.int32).to_numpy()
    ask1_sz = df["ask_size_1"].astype(np.int32).to_numpy()

    # Define the day as an int
    date_int = (
        pd.to_datetime(df["time"], unit="s")
          .dt.strftime("%Y%m%d")
          .astype(np.int32)
          .to_numpy()
    )

    engine = FastQueue(
        mid,
        bid1,
        ask1, 
        ts, 
        qi, 
        sigI, 
        bid1_sz,
        ask1_sz,
        typ,
        size,
        dir,
        latency_us=4
    )
    agent  = VolGuardQIMM(beta=0.8)

    sigma_d = load_sigma().to_dict() 

    # ---------------- Timed section ---------------------------------
    def run():
        engine.run(agent, sigma_d, date_int)

    result = benchmark(run)      # pytest-benchmark measures wall-clock
    #assert result.stats.median < 5.0   # <-- fail if slower than 5 s

