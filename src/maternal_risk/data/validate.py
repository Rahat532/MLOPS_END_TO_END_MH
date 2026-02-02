from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
import pandas as pd


@dataclass(frozen=True)
class DataValidationResult:
    ok: bool
    errors: list[str]


REQUIRED_COLUMNS: tuple[str, ...] = (
    "Age",
    "SystolicBP",
    "DiastolicBP",
    "BS",
    "BodyTemp",
    "HeartRate",
    "RiskLevel",
)

ALLOWED_RISK_LEVELS: set[str] = {"low risk", "mid risk", "high risk"}


def _missing_columns(df: pd.DataFrame, required: Iterable[str]) -> list[str]:
    req = set(required)
    present = set(df.columns)
    return sorted(list(req - present))


def validate_schema(df: pd.DataFrame) -> DataValidationResult:
    """
    Validate schema + basic value sanity checks.

    This is NOT medical-grade validation. It's engineering validation
    to catch broken data early.
    """
    errors: list[str] = []

    # Column presence
    missing = _missing_columns(df, REQUIRED_COLUMNS)
    if missing:
        errors.append(f"Missing required columns: {missing}")
        return DataValidationResult(ok=False, errors=errors)  # can't continue safely

    # Null checks
    null_counts = df[list(REQUIRED_COLUMNS)].isna().sum()
    if int(null_counts.sum()) > 0:
        errors.append(f"Null values found:\n{null_counts[null_counts > 0].to_dict()}")

    # Type sanity (numeric features should be coercible)
    numeric_cols = ["Age", "SystolicBP", "DiastolicBP", "BS", "BodyTemp", "HeartRate"]
    for col in numeric_cols:
        coerced = pd.to_numeric(df[col], errors="coerce")
        if coerced.isna().any():
            bad = int(coerced.isna().sum())
            errors.append(f"Column '{col}' has {bad} non-numeric values.")

    # Range checks (engineering sanity, not medical diagnosis)
    if (df["Age"] < 0).any():
        errors.append("Age has negative values.")
    if (df["SystolicBP"] <= 0).any():
        errors.append("SystolicBP has non-positive values.")
    if (df["DiastolicBP"] <= 0).any():
        errors.append("DiastolicBP has non-positive values.")
    if (df["HeartRate"] <= 0).any():
        errors.append("HeartRate has non-positive values.")
    if (df["BodyTemp"] <= 0).any():
        errors.append("BodyTemp has non-positive values.")
    if (df["BS"] <= 0).any():
        errors.append("BS has non-positive values.")

    # Target check
    if df["RiskLevel"].dtype != object:
        df["RiskLevel"] = df["RiskLevel"].astype(str)

    invalid_targets = (
        set(df["RiskLevel"].str.strip().str.lower().unique()) - ALLOWED_RISK_LEVELS
    )
    if invalid_targets:
        errors.append(
            f"Invalid RiskLevel values found: {sorted(list(invalid_targets))}"
        )

    return DataValidationResult(ok=len(errors) == 0, errors=errors)
