from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from sklearn.metrics import accuracy_score, f1_score, classification_report


@dataclass(frozen=True)
class EvalResult:
    metrics: dict[str, Any]
    classification_report_text: str


def evaluate_classification(y_true, y_pred, labels=None) -> EvalResult:
    """
    Metrics for multi-class classification.
    We emphasize macro-F1 (treats classes equally).
    """
    metrics = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "f1_macro": float(f1_score(y_true, y_pred, average="macro")),
        "f1_weighted": float(f1_score(y_true, y_pred, average="weighted")),
    }

    report = classification_report(y_true, y_pred, labels=labels, zero_division=0)
    return EvalResult(metrics=metrics, classification_report_text=report)
