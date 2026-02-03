import os
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from webapp.schemas import PredictRequest
from webapp.model import predict_risk

app = FastAPI(title="Maternal Risk Predictor")

# Mount static directories (only if they exist)
if os.path.isdir("webapp/static"):
    app.mount("/static", StaticFiles(directory="webapp/static"), name="static")
app.mount("/assets", StaticFiles(directory="webapp/assets"), name="assets")
templates = Jinja2Templates(directory="webapp")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request, "result": None, "error": None}
    )


@app.get("/check.html", response_class=HTMLResponse)
def check(request: Request):
    return templates.TemplateResponse("check.html", {"request": request})


@app.get("/resources.html", response_class=HTMLResponse)
def resources(request: Request):
    return templates.TemplateResponse("resources.html", {"request": request})


@app.get("/articles.html", response_class=HTMLResponse)
def articles(request: Request):
    return templates.TemplateResponse("articles.html", {"request": request})


@app.get("/blog.html", response_class=HTMLResponse)
def blog(request: Request):
    return templates.TemplateResponse("blog.html", {"request": request})


@app.get("/medication.html", response_class=HTMLResponse)
def medication(request: Request):
    return templates.TemplateResponse("medication.html", {"request": request})


@app.get("/contact.html", response_class=HTMLResponse)
def contact(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})


@app.post("/predict", response_class=HTMLResponse)
def predict_form(
    request: Request,
    Age: float = Form(...),
    SystolicBP: float = Form(...),
    DiastolicBP: float = Form(...),
    BS: float = Form(...),
    BodyTemp: float = Form(...),
    HeartRate: float = Form(...),
):
    try:
        payload = PredictRequest(
            Age=Age,
            SystolicBP=SystolicBP,
            DiastolicBP=DiastolicBP,
            BS=BS,
            BodyTemp=BodyTemp,
            HeartRate=HeartRate,
        ).model_dump()

        result = predict_risk(payload)
        return templates.TemplateResponse(
            "index.html", {"request": request, "result": result, "error": None}
        )

    except ValidationError as e:
        errors = [f"{err['loc'][0]}: {err['msg']}" for err in e.errors()]
        error_msg = "Validation failed: " + "; ".join(errors)
        return templates.TemplateResponse(
            "index.html", {"request": request, "result": None, "error": error_msg}
        )


# Optional: JSON API (useful for frontend later)
@app.post("/api/predict")
def predict_api(req: PredictRequest):
    risk = predict_risk(req.model_dump())
    return {"risk_level": risk}
