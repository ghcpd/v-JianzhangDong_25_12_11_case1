import pandas as pd
import numpy as np
from pathlib import Path


def load_csv(path: str) -> pd.DataFrame:
    file = Path(path)
    if not file.exists():
        raise FileNotFoundError(f"File not found: {path}")
    df = pd.read_csv(file)
    df = df.fillna(0)
    return df