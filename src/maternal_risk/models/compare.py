from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import pandas as pd
import yaml
import matplotlib.pyplot as plt

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


def build_pipeline(needs_scaling: bool, estimator: object) -> Pipeline:
    steps = []
    if needs_scaling:
        steps.append(("scaler", StandardScaler()))
    steps.append(("model", estimator))
    return Pipeline(steps)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, required=True, help="Path to configs/train.yaml")
    parser.add_argument(
        "--save-models",
        action="store_true",
        help="If set, saves each trained model into /models (can be slower).",
    )
    args = parser.parse_args()

    cfg = yaml.safe_load(Path(args.config).read_text())

    raw_path = cfg["data"]["raw_path"]
    test_size = float(cfg["train"]["test_size"])
    random_state = int(cfg["train"]["random_state"])
    model_dir = Path(cfg["output"]["model_dir"])
    report_dir = Path(cfg["output"]["report_dir"])

    # Load
    df = load_data(raw_path)

    # Validate
    result = validate_schema(df)
    if not result.ok:
        raise ValueError(f"Data validation failed: {result.errors}")

    # Feature engineering
    df = add_features(df)

    # Prepare X/y
    df["RiskLevel"] = df["RiskLevel"].astype(str).str.strip().str.lower()
    X = df.drop(columns=["RiskLevel"])
    y = df["RiskLevel"]

    # Encode labels for models that require numeric (e.g., XGBoost)
    label_encoder = LabelEncoder()
    label_encoder.fit(LABELS)  # Fit on defined order: low, mid, high
    y_encoded = label_encoder.transform(y)

    # Split once (fair comparison)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=test_size, random_state=random_state, stratify=y_encoded
    )

    specs = get_model_specs(random_state=random_state)

    # Output dirs
    report_dir.mkdir(parents=True, exist_ok=True)
    fig_dir = report_dir / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    if args.save_models:
        model_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []

    for model_key, spec in specs.items():
        print(f"\n=== Training: {model_key} ({spec.name}) ===")

        pipeline = build_pipeline(spec.needs_scaling, spec.estimator)
        pipeline.fit(X_train, y_train)

        y_pred = pipeline.predict(X_test)

        # Decode predictions and test labels back to string labels for evaluation
        y_test_labels = label_encoder.inverse_transform(y_test)
        y_pred_labels = label_encoder.inverse_transform(y_pred)

        eval_result = evaluate_classification(y_test_labels, y_pred_labels, labels=LABELS)

        # Save confusion matrix
        save_confusion_matrix(
            y_test_labels,
            y_pred_labels,
            labels=LABELS,
            out_path=fig_dir / f"confusion_matrix_{model_key}.png",
        )

        # Optionally save model
        if args.save_models:
            joblib.dump(pipeline, model_dir / f"{model_key}.joblib")

        row = {
            "model_key": model_key,
            "model_name": spec.name,
            **eval_result.metrics,
        }
        rows.append(row)

        # Save report text per model
        (report_dir / f"classification_report_{model_key}.txt").write_text(
            eval_result.classification_report_text
        )

        print(json.dumps(row, indent=2))

    results_df = pd.DataFrame(rows).sort_values("f1_macro", ascending=False)

    # Save tables
    results_df.to_csv(report_dir / "model_comparison.csv", index=False)
    (report_dir / "model_comparison.json").write_text(
        results_df.to_json(orient="records", indent=2)
    )

    # Plot macro F1
    plt.figure()
    results_df.plot(x="model_key", y="f1_macro", kind="bar", legend=False)
    plt.title("Model Comparison (Macro F1)")
    plt.ylabel("f1_macro")
    plt.tight_layout()
    plt.savefig(fig_dir / "model_f1_macro.png", dpi=150)
    plt.close()

    print("\nSaved:")
    print(f"- {report_dir / 'model_comparison.csv'}")
    print(f"- {fig_dir / 'model_f1_macro.png'}")
    print("\nTop models:")
    print(results_df[["model_key", "f1_macro", "accuracy"]].head(5))


if __name__ == "__main__":
    main()
