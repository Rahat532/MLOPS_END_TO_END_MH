import pandas as pd
from maternal_risk.data.validate import validate_schema


def test_validate_schema_ok():
    df = pd.DataFrame(
        {
            "Age": [25, 31],
            "SystolicBP": [120, 130],
            "DiastolicBP": [80, 85],
            "BS": [7.0, 6.5],
            "BodyTemp": [98.6, 99.1],
            "HeartRate": [72, 78],
            "RiskLevel": ["low risk", "high risk"],
        }
    )
    result = validate_schema(df)
    assert result.ok is True
    assert result.errors == []


def test_validate_schema_missing_column_fails():
    df = pd.DataFrame(
        {
            "Age": [25],
            "SystolicBP": [120],
            # Missing DiastolicBP
            "BS": [7.0],
            "BodyTemp": [98.6],
            "HeartRate": [72],
            "RiskLevel": ["low risk"],
        }
    )
    result = validate_schema(df)
    assert result.ok is False
    assert any("Missing required columns" in e for e in result.errors)
