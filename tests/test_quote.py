import numpy as np

from strategy.volguard_qimm import VolGuardQIMM
from utils.load_l2 import load_l2
from features.l2_derived_features import queue_imbalance

def test_bid_ask_position():
    # just catches sign errors
    state = dict(mid=100.0, sigma_i=0.002, sigma_daily=0.01, tfrac=0.5, queue_imb=0.0)
    agent = VolGuardQIMM(gamma0=0.1, alpha=1.0, beta=0.5)
    bid, ask = agent.quote(state)
    assert bid < state["mid"] < ask

def test_more_intraday_vol_widens_spread():
    state = dict(
        mid=100.0,
        sigma_daily=0.01,
        queue_imb=0.0,
        tfrac=0.5,
    )
    agent = VolGuardQIMM(gamma0=0.1, alpha=0.0, beta=0.0)  # keep γ constant

    state["sigma_i"] = 0.002
    narrow = agent.quote(state)

    state["sigma_i"] = 0.008           # 4× more realised vol
    wide = agent.quote(state)

    assert (wide[1] - wide[0]) > (narrow[1] - narrow[0])

def test_queue_imbalance_range():
    # tests bounded imbalance QI = bid - ask / bid + ask
    df = load_l2("data/AAPL_20120621.parquet")
    qi = queue_imbalance(df)
    assert ((qi >= -1) & (qi <= 1)).all() 

def test_beta_tilts_quotes():
    state = dict(mid=100.0, sigma_i=0.002, sigma_daily=0.01,
                 tfrac=0.5, queue_imb=0.30)
    agent = VolGuardQIMM(beta=0.8)
    bid_skew, ask_skew = agent.quote(state)

    state["queue_imb"] = 0.0
    bid_neu, ask_neu = agent.quote(state)

    # Both quotes should shift up by the same amount; spread stays equal.
    shift = bid_skew - bid_neu
    assert np.isclose(shift, ask_skew - ask_neu, atol=1e-9)
    assert shift > 0                                # moved upward
    assert np.isclose((ask_skew - bid_skew), (ask_neu - bid_neu))

# def test_beta_tilts_quotes():
#     state = dict(mid=100.0,
#                  sigma_i=0.002,
#                  sigma_daily=0.01,
#                  tfrac=0.5,
#                  queue_imb=0.30)               # 30 % more size on bid side
#     agent = VolGuardQIMM(beta=0.8)
#     bid_up, ask_down = agent.quote(state)

#     # Now compute neutral quotes (QI = 0) for comparison
#     state["queue_imb"] = 0.0
#     bid_neu, ask_neu = agent.quote(state)

#     # Positive QI pushes bid *up* (toward mid) and ask *down* (toward mid)
#     assert bid_up > bid_neu and ask_down < ask_neu
