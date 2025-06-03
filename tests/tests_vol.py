import pandas as pd
from src.utils.vol import load_sigma
from utils.load_l2 import load_l2

def test_load_sigma_returns_series():
    ser = load_sigma()
    assert isinstance(ser, pd.Series)

    
def test_series_has_name_and_positive_values():
    ser = load_sigma()
    assert ser.name == "sigma"
    assert (ser > 0).all()        # all vols strictly positive
