import numpy as np
import joblib

MODEL_PATH = "app/ml/rf_model.pkl"

try:
    model = joblib.load(MODEL_PATH)
except:
    model = None


# =========================
# BUILD FEATURES (MATCH TRAINING)
# =========================
def build_features(result):

    return [
        result.get("sharpe", 0),
        result.get("max_drawdown", 0),

        # derived features (must match dataset_builder)
        result.get("risk_reward", 0),
        result.get("stability", 0),
        result.get("consistency", 0),

        # market features
        result.get("mkt_volatility", 0),
        result.get("momentum", 0),
        result.get("trend_strength", 0),
        result.get("volume_spike", 0),
    ]


# =========================
# PREDICT SCORE
# =========================
def predict_score(result):

    if model is None:
        return 0.0

    try:
        X = np.array(build_features(result)).reshape(1, -1)
        score = model.predict(X)[0]

        return float(score)

    except Exception as e:
        print(f"⚠️ Prediction error: {e}")
        return 0.0