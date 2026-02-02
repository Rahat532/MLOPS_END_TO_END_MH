from __future__ import annotations

from dataclasses import dataclass
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.neural_network import MLPClassifier

# XGBoost is optional (install later). We'll support it if present.
try:
    from xgboost import XGBClassifier  # type: ignore

    _HAS_XGBOOST = True
except Exception:
    XGBClassifier = None  # type: ignore
    _HAS_XGBOOST = False


@dataclass(frozen=True)
class ModelSpec:
    name: str
    needs_scaling: bool
    estimator: object


def get_model_specs(random_state: int = 42) -> dict[str, ModelSpec]:
    """
    Returns a dictionary mapping model key -> ModelSpec
    This powers the model selection.
    """
    specs: dict[str, ModelSpec] = {}

    # 1) Dummy baseline
    specs["dummy"] = ModelSpec(
        name="Dummy (most_frequent)",
        needs_scaling=False,
        estimator=DummyClassifier(strategy="most_frequent"),
    )

    # 2) Logistic regression
    specs["logreg"] = ModelSpec(
        name="Logistic Regression",
        needs_scaling=True,
        estimator=LogisticRegression(
            max_iter=2000,
            class_weight="balanced",
            random_state=random_state,
        ),
    )

    # 3) Random Forest
    specs["rf"] = ModelSpec(
        name="Random Forest",
        needs_scaling=False,
        estimator=RandomForestClassifier(
            n_estimators=300,
            random_state=random_state,
            class_weight="balanced",
        ),
    )

    # 4) Extra Trees
    specs["extratrees"] = ModelSpec(
        name="Extra Trees",
        needs_scaling=False,
        estimator=ExtraTreesClassifier(
            n_estimators=500,
            random_state=random_state,
            class_weight="balanced",
        ),
    )

    # 5) MLP (Neural Network)
    specs["mlp"] = ModelSpec(
        name="MLP (Neural Network)",
        needs_scaling=True,
        estimator=MLPClassifier(
            hidden_layer_sizes=(64, 32),
            activation="relu",
            solver="adam",
            alpha=0.0005,
            learning_rate_init=0.001,
            max_iter=500,
            random_state=random_state,
            early_stopping=False,
        ),
    )

    # 6) XGBoost (if installed)
    if _HAS_XGBOOST:
        specs["xgboost"] = ModelSpec(
            name="XGBoost",
            needs_scaling=False,
            estimator=XGBClassifier(
                n_estimators=500,
                learning_rate=0.05,
                max_depth=4,
                subsample=0.9,
                colsample_bytree=0.9,
                objective="multi:softprob",
                eval_metric="mlogloss",
                random_state=random_state,
            ),
        )

    return specs
