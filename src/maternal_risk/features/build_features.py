from __future__ import annotations

import pandas as pd


FEATURE_COLUMNS = ["Age", "SystolicBP", "DiastolicBP", "BS", "BodyTemp", "HeartRate"]


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add simple, explainable engineered features.

    We keep it minimal and defensible:
    - pulse_pressure = SystolicBP - DiastolicBP
    """
    df = df.copy()

    df["pulse_pressure"] = df["SystolicBP"] - df["DiastolicBP"]

    return df
