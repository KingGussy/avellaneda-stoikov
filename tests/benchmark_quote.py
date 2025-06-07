import pytest
from strategy.volguard_qimm import VolGuardQIMM

# fixed synthetic state (no IO in the benchmark)
state = dict(
    mid=100.0,
    sigma_i=0.002,
    sigma_daily=0.01,
    tfrac=0.5,
    queue_imb=0.10,
)

agent = VolGuardQIMM(beta=0.8)

def test_quote_speed(benchmark):
    benchmark(agent.quote, state)