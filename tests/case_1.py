import pandas as pd
import numpy as np


def test_pandas_numpy():
    try:
        df = pd.DataFrame({"a": np.arange(5)})
        print(df)
        print("case_1 OK")
    except Exception as e:
        print("Dependency error in case_1:", e)
        raise