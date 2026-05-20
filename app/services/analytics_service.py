"""Stock analytics: OHLC, technical indicators, LSTM forecast, recommendation."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import yfinance as yf

from app.core.utils.serialize import sanitize_forecast
from app.ml.lstm_predictor import predict_next_day_forecast

logger = logging.getLogger(__name__)


def _load_ohlc(symbol: str, period: str = "1y") -> pd.DataFrame:
    data = yf.download(
        symbol,
        period=period,
        interval="1d",
        progress=False,
        auto_adjust=True,
    )

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    if data is None or data.empty:
        raise ValueError(f"No market data for {symbol}")

    required = ["Open", "High", "Low", "Close", "Volume"]
    for col in required:
        if col not in data.columns:
            raise ValueError(f"Missing column {col} for {symbol}")

    data = data[required].copy()
    for col in required:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    data = data.dropna()
    if data.empty:
        raise ValueError(f"Empty OHLC series for {symbol}")

    data.index = pd.to_datetime(data.index)
    return data


def _add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    out["sma_20"] = out["Close"].rolling(20).mean()
    out["sma_50"] = out["Close"].rolling(50).mean()
    out["ema_12"] = out["Close"].ewm(span=12, adjust=False).mean()
    out["ema_26"] = out["Close"].ewm(span=26, adjust=False).mean()

    delta = out["Close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    out["rsi"] = 100 - (100 / (1 + rs))

    ema12 = out["Close"].ewm(span=12, adjust=False).mean()
    ema26 = out["Close"].ewm(span=26, adjust=False).mean()
    out["macd"] = ema12 - ema26
    out["macd_signal"] = out["macd"].ewm(span=9, adjust=False).mean()
    out["macd_hist"] = out["macd"] - out["macd_signal"]

    bb_mid = out["Close"].rolling(20).mean()
    bb_std = out["Close"].rolling(20).std()
    out["bb_upper"] = bb_mid + 2 * bb_std
    out["bb_middle"] = bb_mid
    out["bb_lower"] = bb_mid - 2 * bb_std

    return out


def _build_forecast(df: pd.DataFrame, days: int = 5) -> dict:
    closes = df["Close"].dropna().tolist()
    last_close = float(closes[-1])
    last_date = df.index[-1]

    next_day = sanitize_forecast(predict_next_day_forecast(closes))
    daily_return = float(next_day.get("predicted_return", 0) or 0)

    points = []
    price = last_close
    for i in range(1, days + 1):
        price = price * (1 + daily_return)
        date = last_date + timedelta(days=i)
        band = abs(daily_return) * 2.5 * price
        points.append(
            {
                "date": date.strftime("%Y-%m-%d"),
                "price": round(price, 2),
                "lower": round(price - band, 2),
                "upper": round(price + band, 2),
            }
        )

    return {
        "horizon_days": days,
        "next_day": next_day,
        "lstm_delta_pct": next_day.get("predicted_return_pct", 0),
        "last_close": round(last_close, 2),
        "points": points,
    }


def _build_recommendation(df: pd.DataFrame, lstm_delta: float) -> dict:
    row = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else row

    signals = []
    score = 0.0

    rsi = float(row.get("rsi", 50) or 50)
    if rsi < 30:
        signals.append({"name": "RSI", "bias": "bullish", "detail": f"Oversold ({rsi:.1f})"})
        score += 1.2
    elif rsi > 70:
        signals.append({"name": "RSI", "bias": "bearish", "detail": f"Overbought ({rsi:.1f})"})
        score -= 1.2
    else:
        signals.append({"name": "RSI", "bias": "neutral", "detail": f"Neutral ({rsi:.1f})"})

    macd = float(row.get("macd", 0) or 0)
    macd_sig = float(row.get("macd_signal", 0) or 0)
    prev_macd = float(prev.get("macd", 0) or 0)
    prev_sig = float(prev.get("macd_signal", 0) or 0)

    if prev_macd <= prev_sig and macd > macd_sig:
        signals.append({"name": "MACD", "bias": "bullish", "detail": "Bullish crossover"})
        score += 1.5
    elif prev_macd >= prev_sig and macd < macd_sig:
        signals.append({"name": "MACD", "bias": "bearish", "detail": "Bearish crossover"})
        score -= 1.5
    else:
        signals.append(
            {
                "name": "MACD",
                "bias": "bullish" if macd > macd_sig else "bearish",
                "detail": "MACD above signal" if macd > macd_sig else "MACD below signal",
            }
        )
        score += 0.5 if macd > macd_sig else -0.5

    close = float(row["Close"])
    sma20 = float(row.get("sma_20", close) or close)
    sma50 = float(row.get("sma_50", close) or close)

    if close > sma20 > sma50:
        signals.append({"name": "Trend", "bias": "bullish", "detail": "Price above SMA20/50"})
        score += 1.0
    elif close < sma20 < sma50:
        signals.append({"name": "Trend", "bias": "bearish", "detail": "Price below SMA20/50"})
        score -= 1.0
    else:
        signals.append({"name": "Trend", "bias": "neutral", "detail": "Mixed moving averages"})

    bb_upper = float(row.get("bb_upper", close) or close)
    bb_lower = float(row.get("bb_lower", close) or close)
    if close <= bb_lower:
        signals.append({"name": "Bollinger", "bias": "bullish", "detail": "At lower band"})
        score += 0.8
    elif close >= bb_upper:
        signals.append({"name": "Bollinger", "bias": "bearish", "detail": "At upper band"})
        score -= 0.8

    if lstm_delta > 0.002:
        signals.append(
            {
                "name": "LSTM",
                "bias": "bullish",
                "detail": f"Model drift +{lstm_delta * 100:.2f}%/day",
            }
        )
        score += 1.0
    elif lstm_delta < -0.002:
        signals.append(
            {
                "name": "LSTM",
                "bias": "bearish",
                "detail": f"Model drift {lstm_delta * 100:.2f}%/day",
            }
        )
        score -= 1.0
    else:
        signals.append({"name": "LSTM", "bias": "neutral", "detail": "Flat model outlook"})

    if score >= 2.0:
        action = "BUY"
    elif score <= -2.0:
        action = "SELL"
    else:
        action = "HOLD"

    confidence = int(min(95, max(45, 55 + abs(score) * 8)))

    summaries = {
        "BUY": "Momentum and model signals lean bullish; consider accumulation on pullbacks.",
        "SELL": "Overbought or weakening structure; consider trimming exposure.",
        "HOLD": "Mixed signals — wait for clearer trend confirmation.",
    }

    return {
        "action": action,
        "confidence": confidence,
        "score": round(score, 2),
        "signals": signals,
        "summary": summaries[action],
    }


def _serialize_bars(df: pd.DataFrame) -> list[dict]:
    bars = []
    for ts, row in df.iterrows():
        bars.append(
            {
                "date": ts.strftime("%Y-%m-%d"),
                "open": _safe(row["Open"]),
                "high": _safe(row["High"]),
                "low": _safe(row["Low"]),
                "close": _safe(row["Close"]),
                "volume": _safe(row["Volume"]),
                "sma_20": _safe(row.get("sma_20")),
                "sma_50": _safe(row.get("sma_50")),
                "ema_12": _safe(row.get("ema_12")),
                "ema_26": _safe(row.get("ema_26")),
                "rsi": _safe(row.get("rsi")),
                "macd": _safe(row.get("macd")),
                "macd_signal": _safe(row.get("macd_signal")),
                "macd_hist": _safe(row.get("macd_hist")),
                "bb_upper": _safe(row.get("bb_upper")),
                "bb_middle": _safe(row.get("bb_middle")),
                "bb_lower": _safe(row.get("bb_lower")),
            }
        )
    return bars


def _safe(value) -> float | None:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return None
    return round(float(value), 4)


def get_stock_analytics(symbol: str, period: str = "1y") -> dict:
    symbol = symbol.strip().upper()
    df = _load_ohlc(symbol, period=period)
    df = _add_indicators(df)

    display = df.tail(252).copy()
    forecast = _build_forecast(display)
    lstm_delta = float(
        forecast.get("next_day", {}).get("predicted_return", 0) or 0
    )
    recommendation = _build_recommendation(display, lstm_delta)

    last = display.iloc[-1]
    prev_close = float(display.iloc[-2]["Close"]) if len(display) > 1 else float(last["Close"])
    last_close = float(last["Close"])
    change_pct = ((last_close - prev_close) / prev_close * 100) if prev_close else 0

    return {
        "status": "success",
        "symbol": symbol,
        "period": period,
        "as_of": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "quote": {
            "last": round(last_close, 2),
            "change_pct": round(change_pct, 2),
            "high_52w": round(float(display["High"].max()), 2),
            "low_52w": round(float(display["Low"].min()), 2),
            "volume": int(last["Volume"]),
        },
        "bars": _serialize_bars(display),
        "forecast": forecast,
        "recommendation": recommendation,
    }
