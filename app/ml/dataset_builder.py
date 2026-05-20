import os

import pandas as pd
import yfinance as yf

from sqlalchemy import create_engine

from dotenv import load_dotenv

from app.ml.features import add_all_features


# =========================
# LOAD ENV
# =========================
BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../../"
    )
)

ENV_PATH = os.path.join(
    BASE_DIR,
    ".env"
)

load_dotenv(ENV_PATH)

DATABASE_URL = os.getenv("DATABASE_URL")

print("🔥 DEBUG DB URL:", DATABASE_URL)

if not DATABASE_URL:
    raise ValueError(
        "❌ DATABASE_URL not set"
    )

engine = create_engine(DATABASE_URL)


# =========================
# BUILD DATASET
# =========================
def build_dataset():

    query = """
        SELECT
            r.symbol,
            m.sharpe,
            m.max_drawdown,
            m.volatility,
            m.win_rate,
            m.profit_factor
        FROM metrics m
        JOIN backtest_runs r
        ON m.run_id = r.id
    """

    df = pd.read_sql(
        query,
        engine
    )

    if df.empty:
        raise ValueError(
            "❌ No data available"
        )

    # CLEANING
    df = df.dropna()

    df = df[
        (df["max_drawdown"] >= 0)
        &
        (df["sharpe"].abs() < 10)
    ]

    if df.empty:
        raise ValueError(
            "❌ Data invalid after cleaning"
        )

    return df


# =========================
# FEATURE ENGINEERING
# =========================
def add_features(df):

    df = df.copy()

    # CORE FEATURES
    df["risk_reward"] = (
        df["sharpe"]
        / (df["max_drawdown"] + 0.001)
    )

    df["stability"] = (
        df["sharpe"]
        / (df["volatility"] + 0.001)
    )

    df["consistency"] = (
        df["win_rate"]
        * df["profit_factor"]
    )

    df["drawdown_penalty"] = (
        1
        / (df["max_drawdown"] + 0.01)
    )

    df["win_quality"] = (
        df["win_rate"]
        * df["sharpe"]
    )

    df["safe_stability"] = (
        df["stability"]
        / (df["max_drawdown"] + 0.01)
    )

    # CLIPPING
    df["sharpe"] = (
        df["sharpe"]
        .clip(-5, 5)
    )

    # CLEAN INF
    df = df.replace(
        [float("inf"), -float("inf")],
        0
    )

    return df


# =========================
# MARKET ENRICHMENT
# =========================
import os

import pandas as pd
import yfinance as yf

from sqlalchemy import create_engine

from dotenv import load_dotenv

from app.ml.features import add_all_features


# =========================
# LOAD ENV
# =========================
BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../../"
    )
)

ENV_PATH = os.path.join(
    BASE_DIR,
    ".env"
)

load_dotenv(ENV_PATH)

DATABASE_URL = os.getenv("DATABASE_URL")

print("🔥 DEBUG DB URL:", DATABASE_URL)

if not DATABASE_URL:
    raise ValueError(
        "❌ DATABASE_URL not set"
    )

engine = create_engine(DATABASE_URL)


# =========================
# BUILD DATASET
# =========================
def build_dataset():

    query = """
        SELECT
            r.symbol,
            m.sharpe,
            m.max_drawdown,
            m.volatility,
            m.win_rate,
            m.profit_factor
        FROM metrics m
        JOIN backtest_runs r
        ON m.run_id = r.id
    """

    df = pd.read_sql(
        query,
        engine
    )

    if df.empty:
        raise ValueError(
            "❌ No data available"
        )

    # CLEANING
    df = df.dropna()

    df = df[
        (df["max_drawdown"] >= 0)
        &
        (df["sharpe"].abs() < 10)
    ]

    if df.empty:
        raise ValueError(
            "❌ Data invalid after cleaning"
        )

    return df


# =========================
# FEATURE ENGINEERING
# =========================
def add_features(df):

    df = df.copy()

    # CORE FEATURES
    df["risk_reward"] = (
        df["sharpe"]
        / (df["max_drawdown"] + 0.001)
    )

    df["stability"] = (
        df["sharpe"]
        / (df["volatility"] + 0.001)
    )

    df["consistency"] = (
        df["win_rate"]
        * df["profit_factor"]
    )

    df["drawdown_penalty"] = (
        1
        / (df["max_drawdown"] + 0.01)
    )

    df["win_quality"] = (
        df["win_rate"]
        * df["sharpe"]
    )

    df["safe_stability"] = (
        df["stability"]
        / (df["max_drawdown"] + 0.01)
    )

    # CLIPPING
    df["sharpe"] = (
        df["sharpe"]
        .clip(-5, 5)
    )

    # CLEAN INF
    df = df.replace(
        [float("inf"), -float("inf")],
        0
    )

    return df


# =========================
# MARKET ENRICHMENT
# =========================
import os

import pandas as pd
import yfinance as yf

from sqlalchemy import create_engine

from dotenv import load_dotenv

from app.ml.features import add_all_features


# =========================
# LOAD ENV
# =========================
BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../../"
    )
)

ENV_PATH = os.path.join(
    BASE_DIR,
    ".env"
)

load_dotenv(ENV_PATH)

DATABASE_URL = os.getenv("DATABASE_URL")

print("🔥 DEBUG DB URL:", DATABASE_URL)

if not DATABASE_URL:
    raise ValueError(
        "❌ DATABASE_URL not set"
    )

engine = create_engine(DATABASE_URL)


# =========================
# BUILD DATASET
# =========================
def build_dataset():

    query = """
        SELECT
            r.symbol,
            m.sharpe,
            m.max_drawdown,
            m.volatility,
            m.win_rate,
            m.profit_factor
        FROM metrics m
        JOIN backtest_runs r
        ON m.run_id = r.id
    """

    df = pd.read_sql(
        query,
        engine
    )

    if df.empty:
        raise ValueError(
            "❌ No data available"
        )

    # CLEANING
    df = df.dropna()

    df = df[
        (df["max_drawdown"] >= 0)
        &
        (df["sharpe"].abs() < 10)
    ]

    if df.empty:
        raise ValueError(
            "❌ Data invalid after cleaning"
        )

    return df


# =========================
# FEATURE ENGINEERING
# =========================
def add_features(df):

    df = df.copy()

    # CORE FEATURES
    df["risk_reward"] = (
        df["sharpe"]
        / (df["max_drawdown"] + 0.001)
    )

    df["stability"] = (
        df["sharpe"]
        / (df["volatility"] + 0.001)
    )

    df["consistency"] = (
        df["win_rate"]
        * df["profit_factor"]
    )

    df["drawdown_penalty"] = (
        1
        / (df["max_drawdown"] + 0.01)
    )

    df["win_quality"] = (
        df["win_rate"]
        * df["sharpe"]
    )

    df["safe_stability"] = (
        df["stability"]
        / (df["max_drawdown"] + 0.01)
    )

    # CLIPPING
    df["sharpe"] = (
        df["sharpe"]
        .clip(-5, 5)
    )

    # CLEAN INF
    df = df.replace(
        [float("inf"), -float("inf")],
        0
    )

    return df


# =========================
# MARKET ENRICHMENT
# =========================
def enrich_with_market_data(df):

    enriched = []

    symbols = df["symbol"].unique()

    for symbol in symbols:

        try:

            print(f"📊 Fetching {symbol}")

            price_df = yf.download(
                symbol,
                period="6mo",
                interval="1d"
            )

            # FIX MULTIINDEX
            if isinstance(
                price_df.columns,
                pd.MultiIndex
            ):
                price_df.columns = (
                    price_df.columns
                    .get_level_values(0)
                )

            # VALIDATION
            if (
                price_df.empty
                or len(price_df) < 60
            ):
                print(
                    f"⚠️ Skipping "
                    f"{symbol}"
                )
                continue

            # FEATURE ENGINEERING
            price_df = add_all_features(
                price_df
            )

            # REQUIRED COLS
            required_cols = [

                "volatility",
                "momentum",
                "trend_strength",
                "volume_spike",

                "atr",
                "macd",
                "macd_signal",
                "bb_width",

                "Close"
            ]

            if not all(
                col in price_df.columns
                for col in required_cols
            ):

                print(
                    f"⚠️ Missing cols "
                    f"in {symbol}"
                )

                continue

            # ALL DB ROWS
            symbol_rows = df[
                df["symbol"] == symbol
            ]

            # BUILD TRAINING DATA
            for _, base_row in symbol_rows.iterrows():

                base = base_row.to_dict()
                for i in range(20,
                               len(price_df) - 5,
                               5
                               ):
                     row = price_df.iloc[i]

                    # =========================
                    # FUTURE SHARPE TARGET
                    # =========================
                     future_returns = (
                        price_df["Close"]
                        .pct_change()
                        .iloc[i:i+5]
                     )

                     future_mean = (
                        future_returns.mean()
                     )

                     future_std = (
                        future_returns.std()
                     )

                     target = 0

                     if (
                        future_std is not None
                        and future_std != 0
                     ):
                         target = (future_mean/ future_std)
                         enriched.append({

                        **base,

                        # BASIC MARKET
                        "mkt_volatility":
                            row["volatility"],

                        "momentum":
                            row["momentum"],

                        "trend_strength":
                            row["trend_strength"],

                        "volume_spike":
                            row["volume_spike"],

                        # ADVANCED FEATURES
                        "atr":
                            row["atr"],

                        "macd":
                            row["macd"],

                        "macd_signal":
                            row["macd_signal"],

                        "bb_width":
                            row["bb_width"],

                        # TARGET
                        "target":
                            target
                    })

        except Exception as e:

            print(
                f"⚠️ Skipping "
                f"{symbol}: {e}"
            )

    if not enriched:
        raise ValueError(
            "❌ No enriched data"
        )

    df_final = pd.DataFrame(enriched)

    # CLEANING
    df_final = df_final.replace(
        [float("inf"), -float("inf")],
        0
    )

    df_final = df_final.dropna()

    print(
        f"✅ Enriched dataset size: "
        f"{df_final.shape}"
    )

    return df_final


# =========================
# FINAL PIPELINE
# =========================
def get_training_data():

    df = build_dataset()

    df = add_features(df)

    df = enrich_with_market_data(df)

    print(
        f"✅ Final dataset shape: "
        f"{df.shape}"
    )

    return df
# =========================
# FINAL PIPELINE
# =========================
def get_training_data():

    df = build_dataset()

    df = add_features(df)

    df = enrich_with_market_data(df)

    print(
        f"✅ Final dataset shape: "
        f"{df.shape}"
    )

    return df
# =========================
# FINAL PIPELINE
# =========================
def get_training_data():

    df = build_dataset()

    df = add_features(df)

    df = enrich_with_market_data(df)

    print(
        f"✅ Final dataset shape: "
        f"{df.shape}"
    )

    return df