import logging
from pathlib import Path
import numpy as np
import joblib

logger = logging.getLogger(__name__)

MODEL_PATH = Path(__file__).resolve().parent / "rf_model.pkl"

try:
    model = joblib.load(str(MODEL_PATH))
except Exception as exc:
    logger.warning("Failed to load RF model from %s: %s", MODEL_PATH, exc)
    model = None


# =========================
# BUILD FEATURES (MATCH TRAINING)
# =========================
def build_features(result):
    sharpe = float(result.get("sharpe", 0) or 0)
    dd = float(result.get("max_drawdown", 0) or 0)
    vol = float(result.get("volatility", 0) or 0)
    win_rate = float(result.get("win_rate", 0) or 0)
    profit_factor = float(result.get("profit_factor", 0) or 0)

    # derived features with fallback calculations
    risk_reward = result.get("risk_reward")
    if risk_reward is None:
        risk_reward = sharpe / (dd + 0.001)

    win_quality = result.get("win_quality")
    if win_quality is None:
        win_quality = win_rate * sharpe

    stability = result.get("stability")
    if stability is None:
        stability = sharpe / (vol + 0.001)

    consistency = result.get("consistency")
    if consistency is None:
        consistency = win_rate * profit_factor

    return [
        sharpe,
        dd,
        float(risk_reward),
        float(win_quality),
        float(stability),
        float(consistency),

        # market features
        float(result.get("mkt_volatility", 0) or 0),
        float(result.get("momentum", 0) or 0),
        float(result.get("trend_strength", 0) or 0),
        float(result.get("volume_spike", 0) or 0),
    ]


# =========================
# PREDICT SCORE
# =========================
def predict_score(result):
    feats = build_features(result)
    fallback_score = float(feats[0] * 0.5 - feats[1] * 0.3 + feats[3] * 0.2)

    if model is None:
        return fallback_score

    try:
        X = np.array(feats).reshape(1, -1)
        score = model.predict(X)[0]
        return float(score)

    except Exception as e:
        logger.warning(f"Prediction error: {e}")
        return fallback_score