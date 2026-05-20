import numpy as np
import joblib
from sklearn.metrics import mean_squared_error, r2_score

from app.ml.dataset_builder import get_training_data
from app.ml.train_rf import prepare_data

MODEL_PATH = "app/ml/rf_model.pkl"


def evaluate_model():

    # =========================
    # LOAD DATA
    # =========================
    df = get_training_data()

    if df.empty:
        raise ValueError("❌ Dataset is empty")

    # =========================
    # PREPARE FEATURES
    # =========================
    X, y, features = prepare_data(df)

    # 🔥 use correct target
    y_true = y.values

    # =========================
    # LOAD MODEL
    # =========================
    model = joblib.load(MODEL_PATH)

    # =========================
    # PREDICT
    # =========================
    y_pred = model.predict(X)

    # =========================
    # METRICS
    # =========================
    mse = mean_squared_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)

    print("\n📊 MODEL EVALUATION")
    print(f"MSE: {round(mse, 6)}")
    print(f"R2 : {round(r2, 4)}")

    return {
        "mse": float(mse),
        "r2": float(r2)
    }


if __name__ == "__main__":
    evaluate_model()