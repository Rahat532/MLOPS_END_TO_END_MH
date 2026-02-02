import os
import mlflow
import mlflow.sklearn

from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix

import matplotlib.pyplot as plt


def save_confusion_matrix(cm, out_path: str):
    fig = plt.figure()
    plt.imshow(cm)
    plt.title("Confusion Matrix")
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.colorbar()
    plt.tight_layout()
    fig.savefig(out_path, dpi=200)
    plt.close(fig)


def main():
    # Point THIS script to your running MLflow server
    mlflow.set_tracking_uri("http://127.0.0.1:5000")
    mlflow.set_experiment("step5_sanity_check")

    # Data
    X, y = load_iris(return_X_y=True)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Model
    params = {"C": 1.0, "max_iter": 200, "solver": "lbfgs"}
    model = LogisticRegression(**params)

    with mlflow.start_run(run_name="logreg_iris"):
        # Log params
        mlflow.log_params(params)

        # Train
        model.fit(X_train, y_train)

        # Predict + metrics
        preds = model.predict(X_test)
        acc = accuracy_score(y_test, preds)
        f1 = f1_score(y_test, preds, average="macro")

        mlflow.log_metric("accuracy", acc)
        mlflow.log_metric("macro_f1", f1)

        # Confusion matrix artifact
        cm = confusion_matrix(y_test, preds)
        os.makedirs("tmp", exist_ok=True)
        cm_path = os.path.join("tmp", "confusion_matrix.png")
        save_confusion_matrix(cm, cm_path)
        mlflow.log_artifact(cm_path, artifact_path="eval")

        # Log model artifact
        mlflow.sklearn.log_model(model, artifact_path="model")


if __name__ == "__main__":
    main()
