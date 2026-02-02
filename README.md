# Maternal Risk MLOps Project

End-to-end ML + MLOps project to predict maternal health risk level (Low/Mid/High) from basic vital signs.

## Features

- **Data Validation**: Schema validation using Pydantic
- **Feature Engineering**: Automated feature building pipeline
- **Multiple Models**: Dummy, Logistic Regression, Random Forest, Extra Trees, MLP, XGBoost
- **Experiment Tracking**: MLflow integration for metrics, artifacts, and model versioning
- **Model Comparison**: Automated comparison across all models
- **API Ready**: FastAPI-based inference endpoint

## Project Structure

```
├── configs/              # YAML configuration files
│   └── train.yaml        # Training configuration
├── data/
│   ├── raw/              # Raw data (not committed)
│   └── processed/        # Processed data (not committed)
├── models/               # Saved model artifacts (not committed)
├── notebooks/            # Jupyter notebooks for EDA
│   ├── 01_eda.ipynb
│   └── 02_model_comparison.ipynb
├── reports/              # Metrics and figures
│   └── figures/          # Confusion matrices, charts
├── src/maternal_risk/    # Source code
│   ├── api/              # FastAPI endpoints
│   ├── data/             # Data loading and validation
│   ├── evaluation/       # Metrics and plotting
│   ├── features/         # Feature engineering
│   └── models/           # Model registry and training
└── tests/                # Unit tests
```

## Quickstart

### 1. Setup Environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate

pip install -e .
pip install -r requirements.txt
```

### 2. Train a Single Model

```bash
python -m maternal_risk.models.train --config configs/train.yaml --model logreg
python -m maternal_risk.models.train --config configs/train.yaml --model rf
python -m maternal_risk.models.train --config configs/train.yaml --model xgboost
```

Available models: `dummy`, `logreg`, `rf`, `extratrees`, `mlp`, `xgboost`

### 3. Compare All Models

```bash
python -m maternal_risk.models.compare --config configs/train.yaml
```

This will train all models and generate:
- `reports/model_comparison.csv`
- `reports/figures/model_f1_macro.png`
- Confusion matrices for each model

### 4. MLflow Tracking

Start the MLflow server:

```bash
mlflow server \
  --backend-store-uri sqlite:///mlflow/backend/mlflow.db \
  --default-artifact-root ./mlflow/artifacts \
  --host 127.0.0.1 \
  --port 5000
```

Then view experiments at: http://127.0.0.1:5000

### 5. Run Tests

```bash
pytest tests/
```

## Model Performance

| Model | F1 Macro | Accuracy |
|-------|----------|----------|
| Random Forest | 0.879 | 87.2% |
| XGBoost | 0.871 | 86.7% |
| Extra Trees | 0.864 | 85.7% |
| MLP | 0.710 | 70.4% |
| Logistic Regression | 0.595 | 60.1% |
| Dummy (baseline) | 0.190 | 39.9% |

## Configuration

Edit `configs/train.yaml` to customize:

```yaml
data:
  raw_path: data/raw/maternal_health.csv

train:
  test_size: 0.2
  random_state: 42

output:
  model_dir: models
  report_dir: reports
```

## License

MIT
