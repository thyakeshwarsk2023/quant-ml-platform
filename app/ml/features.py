import pandas as pd


# =========================
# VOLATILITY
# =========================
def add_volatility(df, window=14):

    df["volatility"] = (
        df["Close"]
        .pct_change()
        .rolling(window)
        .std()
    )

    return df


# =========================
# MOMENTUM
# =========================
def add_momentum(df, window=10):

    df["momentum"] = (
        df["Close"]
        / df["Close"].shift(window)
    ) - 1

    return df


# =========================
# TREND STRENGTH
# =========================
def add_trend_strength(df, window=14):

    ma = df["Close"].rolling(window).mean()

    df["trend_strength"] = ma.pct_change()

    return df


# =========================
# VOLUME SPIKE
# =========================
def add_volume_spike(df, window=20):

    avg_vol = (
        df["Volume"]
        .rolling(window)
        .mean()
    )

    df["volume_spike"] = (
        df["Volume"] / avg_vol
    )

    return df


# =========================
# ATR (VOLATILITY REGIME)
# =========================
def add_atr(df, window=14):

    high_low = df["High"] - df["Low"]

    high_close = (
        df["High"]
        - df["Close"].shift()
    ).abs()

    low_close = (
        df["Low"]
        - df["Close"].shift()
    ).abs()

    tr = pd.concat(
        [high_low, high_close, low_close],
        axis=1
    ).max(axis=1)

    df["atr"] = tr.rolling(window).mean()

    return df


# =========================
# MACD
# =========================
def add_macd(df):

    ema12 = (
        df["Close"]
        .ewm(span=12)
        .mean()
    )

    ema26 = (
        df["Close"]
        .ewm(span=26)
        .mean()
    )

    df["macd"] = ema12 - ema26

    df["macd_signal"] = (
        df["macd"]
        .ewm(span=9)
        .mean()
    )

    return df


# =========================
# BOLLINGER BAND WIDTH
# =========================
def add_bollinger_width(df, window=20):

    ma = (
        df["Close"]
        .rolling(window)
        .mean()
    )

    std = (
        df["Close"]
        .rolling(window)
        .std()
    )

    upper = ma + 2 * std
    lower = ma - 2 * std

    df["bb_width"] = (
        upper - lower
    ) / ma

    return df


# =========================
# MASTER PIPELINE
# =========================
def add_all_features(df):

    df = df.copy()

    # =========================
    # SAFETY CHECKS
    # =========================
    required_cols = [
        "Close",
        "High",
        "Low",
        "Volume"
    ]

    for col in required_cols:

        if col not in df.columns:
            raise ValueError(
                f"Missing required column: {col}"
            )

    # =========================
    # BASIC FEATURES
    # =========================
    df = add_volatility(df)

    df = add_momentum(df)

    df = add_trend_strength(df)

    df = add_volume_spike(df)

    # =========================
    # ADVANCED FEATURES
    # =========================
    df = add_atr(df)

    df = add_macd(df)

    df = add_bollinger_width(df)

    # =========================
    # CLEANING
    # =========================
    df = df.replace(
        [float("inf"), -float("inf")],
        0
    )

    df = df.dropna()

    return df