"""Lightweight LSTM inference for next-day return trend."""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import torch

from app.ml.lstm_model import LSTMModel
from app.ml.lstm_preprocessing import (
    MIN_PRICES,
    build_input_sequence,
    prices_to_returns,
    sanitize_prices,
)

logger = logging.getLogger(__name__)

_MODEL: LSTMModel | None = None
_MODEL_TRIED = False
_MODEL_PATH = Path(__file__).resolve().parent / "lstm_global.pt"

TREND_THRESHOLD = 0.0005
PRED_CLIP = 0.03


def _load_model() -> LSTMModel | None:
    global _MODEL, _MODEL_TRIED

    if _MODEL_TRIED:
        return _MODEL

    _MODEL_TRIED = True

    if not _MODEL_PATH.is_file():
        logger.warning("LSTM weights not found at %s", _MODEL_PATH)
        return None

    try:
        net = LSTMModel()
        state = torch.load(
            _MODEL_PATH,
            map_location="cpu",
            weights_only=True,
        )
        net.load_state_dict(state)
        net.eval()
        _MODEL = net
        logger.info("LSTM model loaded for inference")
    except TypeError:
        try:
            net = LSTMModel()
            state = torch.load(_MODEL_PATH, map_location="cpu")
            net.load_state_dict(state)
            net.eval()
            _MODEL = net
        except Exception as exc:
            logger.warning("LSTM load failed: %s", exc)
            _MODEL = None
    except Exception as exc:
        logger.warning("LSTM load failed: %s", exc)
        _MODEL = None

    return _MODEL


def _trend_from_return(pred_return: float) -> str:
    if pred_return > TREND_THRESHOLD:
        return "up"
    if pred_return < -TREND_THRESHOLD:
        return "down"
    return "neutral"


def _confidence_score(pred_return: float, recent_returns: np.ndarray) -> float:
    """Heuristic confidence from signal strength vs recent volatility (no ensembles)."""
    if recent_returns.size < 2:
        vol = 0.01
    else:
        vol = float(np.std(recent_returns[-20:]))
    vol = max(vol, 1e-4)

    z = abs(pred_return) / vol
    base = 42.0 + min(z * 14.0, 48.0)

    if abs(pred_return) < TREND_THRESHOLD:
        base = max(base - 12.0, 35.0)

    return round(min(92.0, max(35.0, base)), 1)


def _fallback_return(prices: np.ndarray) -> float:
    returns = prices_to_returns(prices)
    return float(np.mean(returns[-5:]))


def _run_inference(seq: np.ndarray) -> float | None:
    model = _load_model()
    if model is None:
        return None

    x = torch.tensor(seq, dtype=torch.float32)
    with torch.no_grad():
        out = model(x)
    return float(out.item())


def predict_next_day_forecast(prices: list[float] | np.ndarray) -> dict:
    """
    JSON-serializable next-day forecast payload.
    """
    base = {
        "horizon": "1d",
        "model_loaded": _load_model() is not None,
        "available": False,
        "trend": "neutral",
        "predicted_return": 0.0,
        "predicted_return_pct": 0.0,
        "predicted_price": None,
        "last_close": None,
        "confidence_pct": 0.0,
        "method": "unavailable",
    }

    try:
        cleaned = sanitize_prices(prices)
    except ValueError as exc:
        base["error"] = str(exc)
        return base

    last_close = float(cleaned[-1])
    base["last_close"] = round(last_close, 4)

    try:
        seq, recent_returns, _ = build_input_sequence(cleaned)
    except ValueError as exc:
        base["error"] = str(exc)
        return base

    raw_pred = _run_inference(seq)
    if raw_pred is None:
        pred_return = _fallback_return(cleaned)
        method = "momentum_fallback"
        confidence = 40.0
    else:
        pred_return = float(np.clip(raw_pred, -PRED_CLIP, PRED_CLIP))
        method = "lstm"
        confidence = _confidence_score(pred_return, recent_returns)

    trend = _trend_from_return(pred_return)
    predicted_price = round(last_close * (1.0 + pred_return), 4)

    base.update(
        {
            "available": True,
            "trend": trend,
            "predicted_return": round(pred_return, 6),
            "predicted_return_pct": round(pred_return * 100, 3),
            "predicted_price": predicted_price,
            "confidence_pct": confidence,
            "method": method,
        }
    )
    return base


def predict_lstm(prices: list[float] | np.ndarray) -> float:
    """Backward-compatible scalar return prediction for scan/analytics."""
    if len(prices) < MIN_PRICES:
        return 0.0

    result = predict_next_day_forecast(prices)
    if not result.get("available"):
        return 0.0
    return float(result["predicted_return"])
