import numpy as np
from engine import FastQueue
def test_queue_position_decreases():
    n = 3
    fq = FastQueue(
        mid = np.array([100,100,100], float),
        bid1= np.array([99,99,99], float),
        ask1= np.array([101,101,101], float),
        ts   = np.arange(n, dtype=float),
        qi   = np.zeros(n),
        sigI = np.ones(n)*0.002,
        bid_sz1 = np.array([10,8,5], int),   # two shares printed
        ask_sz1 = np.array([10,10,10], int),
        typ  = np.array([4,4,4],  np.int8),  # executions
        size = np.array([2,3,5],  np.int32),
        dir = np.array([-1,-1,-1], np.int8),
        latency_us = 0,
    )
    pnl = fq.run(None, {}, np.array([20240610], dtype=np.int32))
    # after three prints whole order should be filled
    assert fq.live_b == 0
    assert pnl[-1] != 0