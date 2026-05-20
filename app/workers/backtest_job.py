from sqlalchemy import text
from datetime import datetime

from app.db.session import SessionLocal
from app.services.backtest_service import run_backtest_sync
from app.ml.ranker import predict_score


def run_backtest_job(run_id, symbol):
    db = SessionLocal()

    try:
        print(f"🚀 Running backtest: {symbol} | run_id={run_id}")

        # =========================
        # RUN BACKTEST
        # =========================
        bt_result = run_backtest_sync(symbol)

        # =========================
        # EXTRACT METRICS
        # =========================
        ret = float(bt_result.get("return", 0))
        sharpe = float(bt_result.get("sharpe", 0))
        dd = float(bt_result.get("max_drawdown", 0))

        # 🔥 OPTIONAL (if available)
        volatility = float(bt_result.get("volatility", 0))
        win_rate = float(bt_result.get("win_rate", 0))
        profit_factor = float(bt_result.get("profit_factor", 0))

        # =========================
        # BUILD ML INPUT
        # =========================
        ml_input = {
            "sharpe": sharpe,
            "max_drawdown": dd,
            "risk_reward": sharpe / (dd + 0.001),
            "stability": sharpe / (volatility + 0.001),
            "consistency": win_rate * profit_factor,

            # ⚠️ TEMP (until you connect live market features)
            "mkt_volatility": 0,
            "momentum": 0,
            "trend_strength": 0,
            "volume_spike": 0,
        }

        ml_score = predict_score(ml_input)

        # =========================
        # SAVE METRICS
        # =========================
        db.execute(text("""
            INSERT INTO metrics (
                run_id,
                return_pct,
                sharpe,
                max_drawdown,
                volatility,
                win_rate,
                profit_factor,
                ml_score
            )
            VALUES (
                :id, :ret, :sharpe, :dd,
                :vol, :wr, :pf, :ml
            )
        """), {
            "id": run_id,
            "ret": ret,
            "sharpe": sharpe,
            "dd": dd,
            "vol": volatility,
            "wr": win_rate,
            "pf": profit_factor,
            "ml": ml_score
        })

        # =========================
        # SAVE EQUITY
        # =========================
        db.execute(text("DELETE FROM equity_curve WHERE run_id=:id"), {"id": run_id})

        db.execute(text("""
            INSERT INTO equity_curve (run_id, timestamp, equity)
            VALUES (:id, :ts, :eq)
        """), [
            {
                "id": run_id,
                "ts": p["timestamp"],
                "eq": float(p["equity"])
            }
            for p in bt_result.get("equity_curve", [])
        ])

        # =========================
        # MARK COMPLETED
        # =========================
        db.execute(text("""
            UPDATE backtest_runs
            SET status='completed',
                completed_at=:time
            WHERE id=:id
        """), {
            "id": run_id,
            "time": datetime.utcnow()
        })

        db.commit()

        print(f"✅ Backtest completed: {symbol} | ML score={ml_score:.4f}")

    except Exception as e:
        print(f"❌ Job failed: {e}")

        db.execute(text("""
            UPDATE backtest_runs
            SET status='failed'
            WHERE id=:id
        """), {"id": run_id})

        db.commit()

    finally:
        db.close()