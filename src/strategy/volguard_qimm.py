import numpy as np

from utils.vol import load_sigma
from utils.load_l2 import load_l2
from as_core.market_maker import AvellanedaStoikov

class VolGuardQIMM(AvellanedaStoikov):
    def __init__(self, gamma0=0.15, alpha=2, beta=0.8, k=1.5, sigma_daily=None):
        super().__init__(gamma=gamma0, k=k)
        self.gamma0, self.alpha, self.beta = gamma0, alpha, beta
        self.sigma_daily = sigma_daily or load_sigma()

    def quote(self, state):
        gamma_t = self.gamma0 * (1 + self.alpha * state["sigma_daily"])
        qi  = state["queue_imb"]
        sigma_i = state["sigma_i"]
        Delta = 0.5 * gamma_t * sigma_i**2 * (self.T - state["tfrac"])
        spread = Delta + (1/gamma_t) * np.log1p(gamma_t / self.k)

        bid = state["mid"] - (spread - self.beta * qi)
        ask = state["mid"] + (spread + self.beta * qi)
        return bid, ask
