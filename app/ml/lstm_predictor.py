"""Lightweight LSTM inference for next-day return trend."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import numpy as np

try:
    import torch
    from app.ml.lstm_model import LSTMModel
except (ImportError, OSError, Exception):
    torch = None
    LSTMModel = Any  # type: ignore[misc, assignment]

from app.ml.lstm_preprocessing import (
    MIN_PRICES,
    build_input_sequence,
    prices_to_returns,
    sanitize_prices,
)

logger = logging.getLogger(__name__)

_MODEL: Any | None = None
_MODEL_TRIED = False
_MODEL_PATH = Path(__file__).resolve().parent / "lstm_global.pt"

TREND_THRESHOLD = 0.0005
PRED_CLIP = 0.03


def _load_model() -> Any | None:
    global _MODEL, _MODEL_TRIED

    if _MODEL is not None:
        return _MODEL

    if torch is None or LSTMModel is Any:
        return None

    if not _MODEL_PATH.is_file():
        if not _MODEL_TRIED:
            logger.info("LSTM weights not found at %s; using momentum fallback", _MODEL_PATH)
            _MODEL_TRIED = True
        return None

    _MODEL_TRIED = True

    try:
        net = LSTMModel()
        try:
            state = torch.load(
                _MODEL_PATH,
                map_location="cpu",
                weights_only=True,
            )
        except TypeError:
            state = torch.load(_MODEL_PATH, map_location="cpu")

        if isinstance(state, dict):
            if "state_dict" in state:
                state = state["state_dict"]
            elif "model_state_dict" in state:
                state = state["model_state_dict"]
            net.load_state_dict(state)
        elif hasattr(state, "eval") and callable(state.eval):
            net = state
        else:
            net.load_state_dict(state)

        net.eval()
        _MODEL = net
        logger.info("LSTM model loaded successfully for inference")
    except Exception as exc:
        logger.warning("LSTM load failed: %s; using momentum fallback", exc)
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
    if recent_returns is None or recent_returns.size < 2:
        vol = 0.01
    else:
        vol = float(np.std(recent_returns[-20:]))
    vol = max(vol, 1e-4)

    z = abs(pred_return) / vol
    base = 42.0 + min(z * 14.0, 48.0)

    if abs(pred_return) < TREND_THRESHOLD:
        base = max(base - 12.0, 35.0)

    return round(min(92.0, max(35.0, base)), 1)


def _fallback_return(prices_or_returns: np.ndarray) -> float:
    """Estimate expected next-day return from recent returns or prices."""
    if prices_or_returns is None or prices_or_returns.size == 0:
        return 0.0
    try:
        # If already a returns array (values typically within [-0.2, 0.2])
        if len(prices_or_returns) >= 5 and np.all(np.abs(prices_or_returns) < 1.0):
            return float(np.mean(prices_or_returns[-5:]))
        returns = prices_to_returns(prices_or_returns)
        return float(np.mean(returns[-5:]))
    except Exception:
        if len(prices_or_returns) >= 2:
            return float((prices_or_returns[-1] - prices_or_returns[-2]) / (prices_or_returns[-2] + 1e-9))
        return 0.0


def _run_inference(seq: np.ndarray) -> float | None:
    if torch is None:
        return None
    model = _load_model()
    if model is None:
        return None

    try:
        device = next(model.parameters()).device if hasattr(model, "parameters") else "cpu"
        x = torch.tensor(seq, dtype=torch.float32, device=device)
        with torch.no_grad():
            out = model(x)
        return float(out.item())
    except Exception as exc:
        logger.warning("LSTM inference failed: %s; falling back to momentum", exc)
        return None


def predict_next_day_forecast(prices: list[float] | np.ndarray) -> dict:
    """
    JSON-serializable next-day forecast payload.
    """
    model_available = _load_model() is not None
    base = {
        "horizon": "1d",
        "model_loaded": model_available,
        "available": False,
        "trend": "neutral",
        "predicted_return": 0.0,
        "predicted_return_pct": 0.0,
        "predicted_price": None,
        "last_close": None,
        "confidence_pct": 0.0,
        "method": "unavailable",
    }

    if prices is None:
        base["error"] = f"Need at least {MIN_PRICES} valid prices, got 0"
        return base

    try:
        cleaned = sanitize_prices(prices)
    except (ValueError, TypeError, Exception) as exc:
        base["error"] = str(exc)
        return base

    last_close = float(cleaned[-1])
    base["last_close"] = round(last_close, 4)

    try:
        seq, recent_returns, _ = build_input_sequence(cleaned)
    except (ValueError, TypeError, Exception) as exc:
        base["error"] = str(exc)
        return base

    raw_pred = _run_inference(seq)
    if raw_pred is None:
        pred_return = _fallback_return(recent_returns)
        method = "momentum_fallback"
        confidence = _confidence_score(pred_return, recent_returns)
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
            "model_loaded": method == "lstm",
        }
    )
    return base


def predict_lstm(prices: list[float] | np.ndarray) -> float:
    """Backward-compatible scalar return prediction for scan/analytics."""
    if prices is None:
        return 0.0
    try:
        if len(prices) < MIN_PRICES:
            return 0.0
    except (TypeError, ValueError):
        return 0.0

    result = predict_next_day_forecast(prices)
    if not result.get("available"):
        return 0.0
    return float(result["predicted_return"])
