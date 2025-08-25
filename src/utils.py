import os
import time
import pandas as pd
from typing import List, Dict, Optional

def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def ts() -> str:
    return time.strftime("%Y%m%d_%H%M%S")

def write_csv(df: pd.DataFrame, path: str) -> None:
    ensure_dir(os.path.dirname(path))
    df.to_csv(path, index=False)

def write_parquet(df: pd.DataFrame, path: str) -> None:
    ensure_dir(os.path.dirname(path))
    df.to_parquet(path, index=False)
