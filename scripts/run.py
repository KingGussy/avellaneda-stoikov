import argparse
import pathlib

import pandas as pd

from features.l2_derived_features import queue_imbalance, realised_sigma
from src.strategy.volguard_qimm import VolGuardQIMM
from utils.load_l2 import load_l2
from utils.vol import load_sigma

p = argparse.ArgumentParser()
p.add_argument("--l2", default="data/*.parquet")
p.add_argument("--out", default="results/pnl.csv")
args = p.parse_args()

df   = load_l2(args.l2)
df["qi"]       = queue_imbalance(df)
df["sigma_i"]  = realised_sigma(df)
df["mid"]      = 0.5 * (df["bid_price_1"] + df["ask_price_1"])
df["date"]     = pd.to_datetime(df["time"], unit="s").dt.floor("1D")
df["sigma_d"]  = load_sigma().reindex(df["date"]).values

agent = VolGuardQIMM(sigma_daily=df.groupby("date")["sigma_d"].first())
pnl   = agent.backtest(df)                 # base class provides simple loop
pnl.to_csv(args.out)
print("PnL saved ->", args.out)