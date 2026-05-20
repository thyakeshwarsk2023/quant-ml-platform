from sqlalchemy import text


class DBService:

    def create_run(self, db, payload):

        result = db.execute(text("""
            INSERT INTO backtest_runs (strategy_id, symbol, initial_capital, status)
            VALUES (:strategy_id, :symbol, :capital, 'pending')
            RETURNING id
        """), {
            "strategy_id": payload["strategy_id"],
            "symbol": payload["symbol"],
            "capital": payload.get("capital", 100000)
        })

        run_id = result.scalar()

        db.execute(text("""
            INSERT INTO jobs (run_id, status)
            VALUES (:run_id, 'pending')
        """), {"run_id": run_id})

        db.commit()

        return run_id