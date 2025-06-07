# cython: langauge_level=3, boundscheck=False, wraparound=False
import numpy as np 
cimport numpy as np
from libc.math cimport log1p

cdef double DAY = 86400.0

cdef class FastQueue:
    """
        Back-test engine:
            Iterates over all market events
            Applies Latency
            Execute fills on crossing
    """
    cdef double[:] mid
    cdef double[:] bid1
    cdef double[:] ask1
    cdef double[:] ts
    cdef double[:] qi
    cdef double[:] sigI

    cdef double latency
    cdef Py_ssize_t n_rows

    def __init__(self,
                 np.ndarray[np.double_t, ndim=1] mid,
                 np.ndarray[np.double_t, ndim=1] bid1,
                 np.ndarray[np.double_t, ndim=1] ask1,
                 np.ndarray[np.double_t, ndim=1] ts,
                 np.ndarray[np.double_t, ndim=1] qi,
                 np.ndarray[np.double_t, ndim=1] sigI,
                 double latency_us):
        self.mid   = mid
        self.bid1 = bid1
        self.ask1  = ask1
        self.ts    = ts   # timestamp
        self.qi    = qi
        self.sigI  = sigI
        self.latency = latency_us * 1e-6                            # Improve this- crude []
        self.n_rows = ts.shape[0]

    cpdef run(self, agent, dict sigma_daily, int[:] trade_dates):
        """
        Parameters:
        --
        agent  : VolGuardQIMM instance- the quote
        sigma_daily : dict { date : sigma }
        trade_dates : int array the same length as rows, fetch the date for our daily vol             
        --
        Returns:
            pnl : list[double]
        """

        cdef Py_ssize_t i, idx_fill = 0
        cdef double cash = 0.0
        cdef long inventory = 0
        cdef double bid_q, ask_q, t_live
        cdef list pnl =[]

        # Now iterate our events
        for i in range(self.n_rows):
            # ------------------------- Reconcile pre-live rows ----------------------------

            while idx_fill < i and self.ts[idx_fill] < self.ts[i]:
                idx_fill += 1                                          # Placeholder- add queue logic later [] -o call engine.handle_book_change(idx_fill)
            
            # ------------------------- assemble our state ---------------------------------

            state = {
                "mid": self.mid[i],
                "sigma_i": self.sigI[i],
                "sigma_daily": sigma_daily.get(trade_dates[i], 0.01),
                "tfrac": self.ts[i] / DAY,
                "queue_imbalance": self.qi[i]
            }

            # ------------------------ compute quote and crude Latency ----------------------------------------

            bid_q, ask_q = agent.quote(state)

            t_live = self.ts[i] + self.latency                         # []


            # ---------------------- find first market row after our latency-added time -----------------------

            while idx_fill < self.n_rows and self.ts[idx_fill] < t_live:
                idx_fill += 1

            if idx_fill == self.n_rows:
                break

            # --------------------- cross check -----------------

            if self.ask1[idx_fill] <= bid_q:
                inventory += 1
                cash -= bid_q
            if self.bid1[idx_fill] >= ask_q:
                inventory -= 1
                cash += ask_q

            pnl.append(cash + inventory * self.mid[i])

        return pnl
            
