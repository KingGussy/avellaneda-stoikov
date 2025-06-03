"""
Utility package for data conversion & IO.
`build_parquet` : CSV ➜ Parquet converter
`load_l2`       : Parquet ➜ pandas DataFrame reader
"""

from .build_parquet import \
    load_l2 as build_parquet  # keep old name for CLI scripts
from .load_l2 import load_l2  # reader

__all__ = ["build_parquet", "load_l2"]
