# cython: langauge_level=3, boundscheck=False, wraparound=False

# TODO(v2): replace bid1_sz with cumulative depth for inside-spread quotes.

import numpy as np 
cimport numpy as np
from libc.math cimport log1p

from libc.stdint cimport int8_t, int32_t

cdef double DAY = 86400.0


# Helper functions to identify prints hitting
cdef inline bint hit_bid(int8_t typ, int8_t direction):
    # Retrurns True if execution reduces bid queue
    return typ in (4, 5) and direction == -1
cdef inline bint hit_ask(int8_t typ, int8_t direction):
    # Retrurns True if execution reduces bid queue
    return typ in (4, 5) and direction == 1

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

    cdef int8_t[:] typ          # LOBSTER message type
    cdef int32_t[:] size            
    cdef int8_t[:] dir

    cdef int32_t[:] bid1_sz
    cdef int32_t[:] ask1_sz

    cdef double latency
    cdef Py_ssize_t n_rows

    cdef Py_ssize_t pos_b       # shares ahead of us at bid
    cdef Py_ssize_t pos_a       # shares ahead of us at ask
    cdef bint live_b, live_a    # 1 = working, 0 = none

    cdef double filled_pnl      # running_pnl

    def __init__(self,
                 np.ndarray[np.double_t, ndim=1] mid,
                 np.ndarray[np.double_t, ndim=1] bid1,
                 np.ndarray[np.double_t, ndim=1] ask1,
                 np.ndarray[np.double_t, ndim=1] ts,
                 np.ndarray[np.double_t, ndim=1] qi,
                 np.ndarray[np.double_t, ndim=1] sigI,
                 np.ndarray[np.int32_t, ndim=1] bid1_sz,
                 np.ndarray[np.int32_t, ndim=1] ask1_sz,
                 np.ndarray[np.int8_t,   ndim=1] typ,
                 np.ndarray[np.int32_t,  ndim=1] size,
                 np.ndarray[np.int8_t,   ndim=1] dir,
                 double latency_us):
        self.mid   = mid
        self.bid1 = bid1
        self.ask1  = ask1
        self.ts    = ts   # timestamp
        self.qi    = qi
        self.sigI  = sigI
        self.typ = typ
        self.size = size
        self.dir = dir 
        self.bid1_sz = bid1_sz
        self.ask1_sz = ask1_sz
        self.latency = latency_us * 1e-6                            # Improve this- crude []
        self.n_rows = ts.shape[0]

        self.pos_a = self.pos_b = -1                                # -1 means flat
        self.live_b = self.live_a = 0

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

            # ------------------------ compute quote  ----------------------------------------

            bid_q, ask_q = agent.quote(state)

            # -------------------- reset queue position if we changed price -----------------------

            # TODO: when we quote inside spread, compute pos_* from cumulative depth

            if bid_q != last_bid:                       # we posted a NEW bid level
                self.pos_b  = self.bid1_sz[i]           # depth ahead of us right now
                self.live_b = 1                         # mark as working
                last_bid    = bid_q                     # remember posted price

            if ask_q != last_ask:                       # new ask level
                self.pos_a  = self.ask1_sz[i]
                self.live_a = 1
                last_ask    = ask_q
 

            # ---------------------- crude Latency-----------------------------------------------------------

            t_live = self.ts[i] + self.latency                         # []
            # find first market row after our latency-added time 
            while idx_fill < self.n_rows and self.ts[idx_fill] < t_live:
                idx_fill += 1
            if idx_fill == self.n_rows:
                break

            
            # ------------- eat queue at idx_fill ------------------------------------
            if self.live_b and hit_bid(self.typ[idx_fill], self.dir[idx_fill]):
                self.pos_b -= self.size[idx_fill]
                if self.pos_b <= 0:
                    fill_sz     = self.size[idx_fill] + self.pos_b
                    self.filled_pnl += (self.mid[idx_fill] - bid_q) * fill_sz
                    self.live_b  = 0

            if self.live_a and hit_ask(self.typ[idx_fill], self.dir[idx_fill]):
                self.pos_a -= self.size[idx_fill]
                if self.pos_a <= 0:
                    fill_sz     = self.size[idx_fill] + self.pos_a
                    self.filled_pnl += (ask_q - self.mid[idx_fill]) * fill_sz
                    self.live_a  = 0


            pnl.append(cash + inventory * self.mid[idx_fill])

        return pnl
            
