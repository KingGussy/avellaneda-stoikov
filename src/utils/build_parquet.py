import pandas as pd
from pathlib import Path

def load_l2(message_path: str,
            orderbook_path: str,
            parquet_out: str,
            n_levels: int):
    """
    Load LOBSTER Level-2 data by merging message and orderbook files,
    then write to Parquet.
    
    Parameters
    ----------

    message_path : str           Path to the LOBSTER message CSV
    orderbook_path : str         Path to the LOBSTER orderbook CSV
    parquet_out : str            Path where the output .parquet will be saved
    n_levels : int               Number of levels recorded in the orderbook file (1 in the sample)
    """

    # Define column names for message file
    msg_cols = [
        "time",      # seconds after midnight (float)
        "type",      # event type (1,2,3,4,5,7)
        "order_id",  
        "size",      
        "price",     # price × 10000
        "direction"  # -1 sell, +1 buy
    ]

    # 2. Read message file
    msg = pd.read_csv(
        message_path,
        names=msg_cols,
        header=None,
        dtype={
            "time": float,
            "type": int,
            "order_id": int,
            "size": int,
            "price": int,
            "direction": int
        }
    )

    # Define column names for the orderbook file
    ob_cols = []
    for lvl in range(1, n_levels+1):
        ob_cols += [
            f"ask_price_{lvl}",
            f"ask_size_{lvl}",
            f"bid_price_{lvl}",
            f"bid_size_{lvl}",
        ]

    # Read orderbook file
    ob = pd.read_csv(
        orderbook_path,
        names=ob_cols,
        header=None,
        dtype={col: int for col in ob_cols}
    )

    # Merge on index as both files have the same row ordering
    # To be safe, we re-use the msg.time as an index.
    df = pd.concat([msg, ob], axis=1)

    # Convert price columns back to floats in dollars
    price_cols = [c for c in df.columns if c.startswith("ask_price") or c.startswith("bid_price")]
    df[price_cols] = df[price_cols].astype(float).div(10000)

    # Write out to Parquet
    # Using snappy compression by default for a good balance of size/speed
    Path(parquet_out).parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(parquet_out, compression="snappy")

    return df


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Merge LOBSTER L2 files to Parquet")
    p.add_argument("message_csv", help="Path to the message CSV")
    p.add_argument("orderbook_csv", help="Path to the orderbook CSV")
    p.add_argument("n_levels",    type=int, help="Number of levels in the orderbook file")
    p.add_argument("parquet_out", help="Where to write the resulting .parquet")
    args = p.parse_args()

    df = load_l2(
        args.message_csv,
        args.orderbook_csv,
        args.parquet_out,
        args.n_levels
    )
    print(f"Written {len(df):,} rows to {args.parquet_out}")