from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    Age: float = Field(..., ge=10, le=60)
    SystolicBP: float = Field(..., ge=70, le=200)
    DiastolicBP: float = Field(..., ge=40, le=140)
    BS: float = Field(..., ge=3, le=30)
    BodyTemp: float = Field(..., ge=95, le=105)  # many datasets use °F
    HeartRate: float = Field(..., ge=40, le=200)
