import pandas as pd
import os
from functools import lru_cache

SYMBOL_FILE = os.path.join(os.path.dirname(__file__), "symbols.csv")


@lru_cache(maxsize=1)
def get_symbols(limit=50, min_length=1):

    df = pd.read_csv(SYMBOL_FILE)

    if "symbol" not in df.columns:
        raise ValueError("CSV must contain 'symbol' column")

    symbols = (
        df["symbol"]
        .dropna()
        .astype(str)
        .str.upper()
    )

    # 🔥 FILTERING
    symbols = [s for s in symbols if len(s) >= min_length]

    return symbols[:limit]
def update_symbols_from_yfinance():
    
    import yfinance as yf

    # 🔥 simple seed list (expand later)
    tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"]

    valid = []

    for t in tickers:
        try:
            data = yf.download(t, period="1d")
            if not data.empty:
                valid.append(t)
        except:
            pass

    df = pd.DataFrame({"symbol": valid})
    df.to_csv(SYMBOL_FILE, index=False)

    return valid