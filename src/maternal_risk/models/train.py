from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import yaml
import mlflow  # >>> MLflow
import mlflow.sklearn  # >>> MLflow
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, LabelEncoder

from maternal_risk.data.load_data import load_data
from maternal_risk.data.validate import validate_schema
from maternal_risk.features.build_features import add_features
from maternal_risk.models.registry import get_model_specs
from maternal_risk.evaluation.metrics import evaluate_classification
from maternal_risk.evaluation.plots import save_confusion_matrix


LABELS = ["low risk", "mid risk", "high risk"]


def build_pipeline(model_key: str, random_state: int) -> Pipeline:
    specs = get_model_specs(random_state=random_state)

    if model_key not in specs:
        available = ", ".join(specs.keys())
        raise ValueError(f"Unknown model '{model_key}'. Available: {available}")

    spec = specs[model_key]

    steps = []
    if spec.needs_scaling:
        steps.append(("scaler", StandardScaler()))
    steps.append(("model", spec.estimator))

    return Pipeline(steps)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, required=True, help="Path to configs/train.yaml")
    parser.add_argument(
        "--model", type=str, required=True, help="Model key (e.g., logreg, rf, svm)"
    )
    args = parser.parse_args()

    cfg = yaml.safe_load(Path(args.config).read_text())

    raw_path = cfg["data"]["raw_path"]
    test_size = float(cfg["train"]["test_size"])
    random_state = int(cfg["train"]["random_state"])
    model_dir = Path(cfg["output"]["model_dir"])
    report_dir = Path(cfg["output"]["report_dir"])

    # >>> MLflow: tell this script where MLflow is running + choose experiment name
    mlflow.set_tracking_uri("http://127.0.0.1:5000")
    mlflow.set_experiment("maternal_risk")

    # Optional: fetch model specs so we can log params cleanly
    specs = get_model_specs(random_state=random_state)
    if args.model not in specs:
        available = ", ".join(specs.keys())
        raise ValueError(f"Unknown model '{args.model}'. Available: {available}")
    spec = specs[args.model]

    # >>> MLflow: one run per training execution (per model)
    with mlflow.start_run(run_name=args.model):
        # >>> MLflow: log useful inputs (params)
        mlflow.log_param("model_key", args.model)
        mlflow.log_param("test_size", test_size)
        mlflow.log_param("random_state", random_state)
        mlflow.log_param("needs_scaling", spec.needs_scaling)

        # If your registry exposes hyperparams as a dict, log them too (optional-safe)
        # This won't crash if it's not available.
        if hasattr(spec, "params") and isinstance(spec.params, dict):
            mlflow.log_params(spec.params)

        # 1) Load
        df = load_data(raw_path)

        # 2) Validate
        result = validate_schema(df)
        if not result.ok:
            raise ValueError(f"Data validation failed: {result.errors}")

        # 3) Feature engineering
        df = add_features(df)

        # 4) Prepare X/y
        df["RiskLevel"] = df["RiskLevel"].astype(str).str.strip().str.lower()
        X = df.drop(columns=["RiskLevel"])
        y = df["RiskLevel"]

        # Encode labels for models that require numeric (e.g., XGBoost)
        label_encoder = LabelEncoder()
        label_encoder.fit(LABELS)  # Fit on defined order: low, mid, high
        y_encoded = label_encoder.transform(y)

        # 5) Split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=test_size, random_state=random_state, stratify=y_encoded
        )

        # 6) Train
        pipeline = build_pipeline(args.model, random_state=random_state)
        pipeline.fit(X_train, y_train)

        # 7) Predict + evaluate
        y_pred = pipeline.predict(X_test)

        # Decode predictions and test labels back to string labels for evaluation
        y_test_labels = label_encoder.inverse_transform(y_test)
        y_pred_labels = label_encoder.inverse_transform(y_pred)

        eval_result = evaluate_classification(y_test_labels, y_pred_labels, labels=LABELS)

        # >>> MLflow: log metrics
        # (Your eval_result.metrics is already a dict: perfect)
        for k, v in eval_result.metrics.items():
            # MLflow expects metrics to be numeric
            if isinstance(v, (int, float)):
                mlflow.log_metric(k, float(v))

        # 8) Save artifacts (your existing behavior stays the same)
        model_dir.mkdir(parents=True, exist_ok=True)
        report_dir.mkdir(parents=True, exist_ok=True)
        (report_dir / "figures").mkdir(parents=True, exist_ok=True)

        model_path = model_dir / f"{args.model}.joblib"
        joblib.dump(pipeline, model_path)

        metrics_path = report_dir / f"metrics_{args.model}.json"
        metrics_path.write_text(json.dumps(eval_result.metrics, indent=2))

        report_path = report_dir / f"classification_report_{args.model}.txt"
        report_path.write_text(eval_result.classification_report_text)

        cm_path = report_dir / "figures" / f"confusion_matrix_{args.model}.png"
        save_confusion_matrix(
            y_test_labels,
            y_pred_labels,
            labels=LABELS,
            out_path=cm_path,
        )

        # >>> MLflow: log artifacts + model
        mlflow.log_artifact(str(metrics_path), artifact_path="eval")
        mlflow.log_artifact(str(report_path), artifact_path="eval")
        mlflow.log_artifact(str(cm_path), artifact_path="eval")

        # Log the sklearn pipeline model in MLflow format
        mlflow.sklearn.log_model(pipeline, artifact_path="model")

        print(f"\nModel saved to: {model_path}")
        print(f"Metrics saved to: {metrics_path}")
        print("\nMetrics:")
        print(json.dumps(eval_result.metrics, indent=2))
        print("\nClassification Report:")
        print(eval_result.classification_report_text)


if __name__ == "__main__":
    main()
