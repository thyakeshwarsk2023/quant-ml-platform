import time
import traceback
import numpy as np

from sqlalchemy import text

from app.core.data.nifty250 import NIFTY_250
from app.db.session import SessionLocal
from app.services.backtest_service import run_backtest_sync


# =========================
# 🔥 NIFTY 250 STOCKS
# =========================
def get_live_nse_symbols(limit=None):

    if limit:
        return NIFTY_250[:limit]

    return NIFTY_250


# =========================
# 🔥 STRATEGY CONFIGS
# =========================
STRATEGY_CONFIGS = [

    # =========================
    # RSI STRATEGIES
    # =========================
    (
        "rsi",
        {
            "period": 7
        }
    ),

    (
        "rsi",
        {
            "period": 14
        }
    ),

    (
        "rsi",
        {
            "period": 21
        }
    ),

    # =========================
    # MOVING AVERAGE
    # =========================
    (
        "ma",
        {
            "short": 10,
            "long": 20
        }
    ),

    (
        "ma",
        {
            "short": 20,
            "long": 50
        }
    ),

    (
        "ma",
        {
            "short": 50,
            "long": 200
        }
    ),

    # =========================
    # HYBRID
    # =========================
    (
        "hybrid",
        {
            "short": 10,
            "long": 50,
            "rsi_period": 14
        }
    ),

    (
        "hybrid",
        {
            "short": 20,
            "long": 100,
            "rsi_period": 21
        }
    ),
]


# =========================
# 🔥 STRATEGY ID LOOKUP
# =========================
def get_strategy_id(db, strategy_name):

    result = db.execute(text("""
        SELECT id
        FROM strategies
        WHERE name = :name
    """), {
        "name": strategy_name
    })

    row = result.fetchone()

    if not row:

        raise ValueError(
            f"Strategy not found: "
            f"{strategy_name}"
        )

    return row[0]


# =========================
# 🔥 SAFE FLOAT
# =========================
def safe_float(value, default=0.0):

    try:

        if value is None:
            return default

        if not np.isfinite(value):
            return default

        return float(value)

    except Exception:
        return default


# =========================
# 🔥 VALIDATE METRICS
# =========================
def validate_metrics(metrics):

    required = [

        "return",
        "sharpe",
        "max_drawdown",
        "volatility",
        "win_rate",
        "profit_factor"
    ]

    for key in required:

        if key not in metrics:

            print(
                f"⚠️ Missing metric: "
                f"{key}"
            )

            return False

        value = metrics.get(key)

        if value is None:

            print(
                f"⚠️ None metric: "
                f"{key}"
            )

            return False

        if not np.isfinite(value):

            print(
                f"⚠️ Non-finite metric: "
                f"{key}"
            )

            return False

    return True


# =========================
# 🔥 GENERATE DATA
# =========================
def run_batch(n=250):

    db = SessionLocal()

    symbols = get_live_nse_symbols(limit=n)

    print(
        f"\n🔥 Running batch for "
        f"{len(symbols)} symbols"
    )

    print(
        f"🔥 Strategy configs: "
        f"{len(STRATEGY_CONFIGS)}"
    )

    total_jobs = (
        len(symbols)
        * len(STRATEGY_CONFIGS)
    )

    print(
        f"🔥 Total jobs: "
        f"{total_jobs}\n"
    )

    success = 0
    fail = 0

    # =========================
    # SYMBOL LOOP
    # =========================
    for i, symbol in enumerate(symbols):

        print(
            f"\n🚀 "
            f"{i+1}/{len(symbols)} "
            f"→ {symbol}"
        )

        # =========================
        # STRATEGY LOOP
        # =========================
        for strategy_name, params in STRATEGY_CONFIGS:

            print(
                f"   ⚡ "
                f"{strategy_name} "
                f"{params}"
            )

            try:

                # =========================
                # RUN BACKTEST
                # =========================
                result_data = run_backtest_sync(

                    symbol=symbol,

                    strategy_name=strategy_name,

                    strategy_params=params
                )

                # =========================
                # EMPTY CHECK
                # =========================
                if not result_data:

                    print(
                        f"⚠️ Empty result "
                        f"({strategy_name})"
                    )

                    fail += 1
                    continue

                # =========================
                # ENSURE METRICS
                # =========================
                result_data.setdefault(
                    "volatility",
                    0.0
                )

                result_data.setdefault(
                    "win_rate",
                    0.0
                )

                result_data.setdefault(
                    "profit_factor",
                    0.0
                )

                # =========================
                # VALIDATE
                # =========================
                if not validate_metrics(
                    result_data
                ):

                    print(
                        f"⚠️ Invalid metrics "
                        f"for {symbol}"
                    )

                    fail += 1
                    continue

                # =========================
                # EXTRACT METRICS
                # =========================
                ret = safe_float(
                    result_data.get("return")
                )

                sharpe = safe_float(
                    result_data.get("sharpe")
                )

                dd = safe_float(
                    result_data.get("max_drawdown")
                )

                vol = safe_float(
                    result_data.get("volatility")
                )

                wr = safe_float(
                    result_data.get("win_rate")
                )

                pf = safe_float(
                    result_data.get("profit_factor")
                )

                # =========================
                # GET STRATEGY ID
                # =========================
                strategy_id = get_strategy_id(
                    db,
                    strategy_name
                )

                # =========================
                # CREATE RUN
                # =========================
                res = db.execute(text("""

                    INSERT INTO backtest_runs (

                        strategy_id,
                        symbol,
                        initial_capital,
                        status

                    )

                    VALUES (

                        :strategy_id,
                        :symbol,
                        :capital,
                        'completed'

                    )

                    RETURNING id

                """), {

                    "strategy_id":
                        strategy_id,

                    "symbol":
                        symbol,

                    "capital":
                        100000
                })

                run_id = res.scalar()

                if not run_id:

                    raise ValueError(
                        "Failed to create run_id"
                    )

                # =========================
                # INSERT METRICS
                # =========================
                db.execute(text("""

                    INSERT INTO metrics (

                        run_id,
                        return_pct,
                        sharpe,
                        max_drawdown,
                        volatility,
                        win_rate,
                        profit_factor

                    )

                    VALUES (

                        :id,
                        :ret,
                        :sharpe,
                        :dd,
                        :vol,
                        :wr,
                        :pf

                    )

                """), {

                    "id":
                        run_id,

                    "ret":
                        ret,

                    "sharpe":
                        sharpe,

                    "dd":
                        dd,

                    "vol":
                        vol,

                    "wr":
                        wr,

                    "pf":
                        pf,
                })

                # =========================
                # COMMIT
                # =========================
                db.commit()

                success += 1

                print(
                    f"✅ Saved "
                    f"{symbol} "
                    f"({strategy_name})"
                )

            except Exception:

                print(
                    f"\n❌ FAILED "
                    f"{symbol} "
                    f"({strategy_name})"
                )

                traceback.print_exc()

                db.rollback()

                fail += 1

            # =========================
            # API THROTTLE
            # =========================
            time.sleep(0.1)

    db.close()

    # =========================
    # FINAL SUMMARY
    # =========================
    print("\n✅ Data generation complete")

    print(
        f"✔ Success: "
        f"{success}"
    )

    print(
        f"❌ Failed: "
        f"{fail}"
    )

    total = success + fail

    if total > 0:

        success_rate = (
            success / total
        ) * 100

        print(
            f"📊 Success Rate: "
            f"{round(success_rate, 2)}%"
        )


# =========================
# 🔥 ENTRY POINT
# =========================
if __name__ == "__main__":

    run_batch(n=250)