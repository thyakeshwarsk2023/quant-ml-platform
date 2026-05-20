from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np

from app.services.backtest_service import run_multi_strategy

# 🔥 ML
from app.ml.ranker import predict_score

# 🔥 OPTIONAL LSTM
try:
    from app.ml.lstm_predictor import predict_lstm
except:
    predict_lstm = None


# =========================
# 🔥 SAFE NORMALIZATION
# =========================
def safe(x, default=0.0):
    try:
        if x is None or np.isnan(x):
            return default
        return float(x)
    except:
        return default


# =========================
# 🔥 PROCESS SINGLE SYMBOL
# =========================
def process_symbol(symbol: str):

    try:
        result = run_multi_strategy(symbol)

        if not result:
            return None

        prices = result.get("prices", [])

        # =========================
        # 🔥 CORE METRICS
        # =========================
        ret = safe(result.get("return"))
        sharpe = safe(result.get("sharpe"))
        drawdown = safe(result.get("max_drawdown"))

        # =========================
        # 🔥 ML SCORE (PRIMARY)
        # =========================
        ml_score = safe(predict_score(result))

        # =========================
        # 🔥 LSTM SIGNAL (OPTIONAL)
        # =========================
        lstm_signal = 0.0
        if predict_lstm and prices and len(prices) > 20:
            try:
                lstm_signal = safe(predict_lstm(prices))
            except:
                lstm_signal = 0.0

        # =========================
        # 🔥 FINAL SCORE
        # =========================
        risk_penalty = drawdown * 0.5

        final_score = (
            0.6 * ml_score +
            0.25 * lstm_signal +
            0.15 * sharpe -
            risk_penalty
        )

        return {
            "symbol": symbol,
            "strategy": result.get("strategy", "unknown"),

            # 🔥 FINAL SCORE
            "score": safe(final_score),

            # 🔍 DEBUG
            "ml_score": ml_score,
            "lstm_signal": lstm_signal,

            # 📊 METRICS
            "return": ret,
            "sharpe": sharpe,
            "drawdown": drawdown,
        }

    except Exception as e:
        print(f"❌ Failed {symbol}: {e}")
        return None


# =========================
# 🔥 MAIN SCAN FUNCTION
# =========================
def scan_market(symbols, max_workers=5):

    if not symbols:
        return []

    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:

        futures = {
            executor.submit(process_symbol, s): s
            for s in symbols
        }

        for future in as_completed(futures):
            try:
                res = future.result(timeout=15)
                if res:
                    results.append(res)
            except Exception as e:
                print(f"⚠️ Timeout/Fail: {futures[future]} -> {e}")

    # =========================
    # 🔥 SORT
    # =========================
    ranked = sorted(results, key=lambda x: x["score"], reverse=True)

    return ranked


# =========================
# 📊 SUMMARY
# =========================
def summarize_results(results):

    if not results:
        return {}

    returns = [safe(r["return"]) for r in results]
    sharpes = [safe(r["sharpe"]) for r in results]
    scores = [safe(r["score"]) for r in results]

    return {
        "avg_return": sum(returns) / len(returns),
        "avg_sharpe": sum(sharpes) / len(sharpes),
        "top_score": max(scores),
        "total_scanned": len(results),
    }