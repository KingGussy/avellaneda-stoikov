#
# Some derived features frm l2 level data
#
import numpy as np


def queue_imbalance(df, level=1):
    bid = df[f"bid_size_{level}"]
    ask = df[f"ask_size_{level}"]

    return (bid - ask) / (bid + ask)

def realised_sigma(df, window_s=60):
    # Realised vol over window (defualt = 60 seconds)
    mid = 0.5 * (df["bid_price_1"] + df["ask_price_1"])
    logret = np.log(mid).diff()
    win = int(window_s / 0.01)                              # crude tick-count window
    return logret/pow(2).rolling(win).mean().pow(0.5).ffill()