"""Symbol-level LSTM forecast API service."""

from __future__ import annotations

import logging
from datetime import datetime

from app.core.utils.serialize import sanitize_forecast
from app.ml.lstm_predictor import predict_next_day_forecast
from app.services.analytics_service import _load_ohlc

logger = logging.getLogger(__name__)


def get_symbol_forecast(symbol: str, period: str = "6mo") -> dict:
    symbol = symbol.strip().upper()
    df = _load_ohlc(symbol, period=period)
    closes = df["Close"].astype(float).tolist()

    forecast = sanitize_forecast(predict_next_day_forecast(closes))
    last_bar_date = df.index[-1].strftime("%Y-%m-%d")

    return {
        "status": "success",
        "symbol": symbol,
        "period": period,
        "as_of": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "last_bar_date": last_bar_date,
        "forecast": forecast,
    }
