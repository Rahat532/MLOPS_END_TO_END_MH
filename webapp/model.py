import os
import joblib
import numpy as np

# Default to Random Forest (best performing model)
MODEL_PATH = os.getenv("MODEL_PATH", "models/rf.joblib")

_model = None


def get_model():
    global _model
    if _model is None:
        _model = joblib.load(MODEL_PATH)
    return _model


def predict_risk(features: dict) -> str:
    """
    features keys must match training column names:
    Age, SystolicBP, DiastolicBP, BS, BodyTemp, HeartRate

    Note: Model was trained with pulse_pressure feature (SystolicBP - DiastolicBP)
    """
    model = get_model()

    # Add engineered feature: pulse_pressure
    pulse_pressure = features["SystolicBP"] - features["DiastolicBP"]

    X = np.array(
        [
            [
                features["Age"],
                features["SystolicBP"],
                features["DiastolicBP"],
                features["BS"],
                features["BodyTemp"],
                features["HeartRate"],
                pulse_pressure,
            ]
        ]
    )

    pred = model.predict(X)[0]

    # adapt mapping if your model outputs numbers
    # e.g. 0/1/2 -> Low/Mid/High
    if str(pred).isdigit():
        mapping = {0: "Low", 1: "Mid", 2: "High"}
        return mapping.get(int(pred), str(pred))

    # if your model outputs strings already
    return str(pred).title()
