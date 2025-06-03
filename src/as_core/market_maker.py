import numpy as np

class AvellanedaStoikov:
    """
    Core A–S market maker.
    Stores inventory & cash; provides `quote()` placeholder and a toy back-test loop.
    Subclasses override `quote`.
    """

    def __init__(self, gamma=0.15, k=1.5, T=1.0):
        self.gamma, self.k, self.T = gamma, k, T
        self.inventory = 0
        self.cash = 0.0

    # ---------- to be overridden ----------
    def quote(self, state):
        raise NotImplementedError

    # ---------- toy back-test ----------
    def backtest(self, df):
        pnl = []
        for i, row in df.iterrows():
            bid, ask = self.quote(row)
            # «very» simple fill rule: cross inside spread
            if row["ask_price_1"] <= bid:
                self.inventory += 1
                self.cash -= bid
            if row["bid_price_1"] >= ask:
                self.inventory -= 1
                self.cash += ask
            pnl.append(self.cash + self.inventory * row["mid"])
        return np.array(pnl)