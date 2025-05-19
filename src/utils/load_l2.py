import pathlib
from typing import List, Union

import pandas as pd


def load_l2(path_or_glob: Union[str, List[str]]) -> pd.DataFrame:
    """
    Read one or more Parquet Level-2 files into a single DataFrame.

    Parameters
    ----------
    path_or_glob : str | list[str]
        "data/*.parquet"      or  ["a.parquet", "b.parquet"]

    Returns
    -------
    pd.DataFrame
    """
    if isinstance(path_or_glob, list):
        paths = path_or_glob
    else:
        paths = [str(p) for p in pathlib.Path().glob(path_or_glob)]

    if not paths:
        raise FileNotFoundError(f"No Parquet files matched {path_or_glob!r}")

    dfs = [pd.read_parquet(p) for p in sorted(paths)]
    return pd.concat(dfs).reset_index(drop=True)