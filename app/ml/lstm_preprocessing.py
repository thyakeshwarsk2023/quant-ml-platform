"""Lightweight preprocessing for LSTM return-sequence inference."""

from __future__ import annotations

import numpy as np

SEQ_LEN = 10
MIN_PRICES = 15
RETURN_CLIP = 0.15


def sanitize_prices(prices: list[float] | np.ndarray) -> np.ndarray:
    arr = np.asarray(prices, dtype=np.float64).reshape(-1)
    mask = np.isfinite(arr) & (arr > 0)
    cleaned = arr[mask]
    if cleaned.size < MIN_PRICES:
        raise ValueError(
            f"Need at least {MIN_PRICES} valid prices, got {cleaned.size}"
        )
    return cleaned


def prices_to_returns(prices: np.ndarray) -> np.ndarray:
    returns = np.diff(prices) / prices[:-1]
    returns = returns[np.isfinite(returns)]
    returns = np.clip(returns, -RETURN_CLIP, RETURN_CLIP)
    if returns.size < SEQ_LEN:
        raise ValueError(
            f"Need at least {SEQ_LEN} return observations, got {returns.size}"
        )
    return returns.astype(np.float32)


def build_input_sequence(prices: list[float] | np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    """
    Returns (model_input [1, SEQ_LEN, 1], recent_returns, last_close).
    """
    cleaned = sanitize_prices(prices)
    last_close = float(cleaned[-1])
    returns = prices_to_returns(cleaned)
    seq = returns[-SEQ_LEN:].reshape(1, SEQ_LEN, 1)
    return seq, returns, last_close
