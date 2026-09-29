import logging
import yfinance as yf
import pandas as pd

from .cache import load_from_cache, save_to_cache, clear_cache

logger = logging.getLogger(__name__)


def load_data(symbol, start="2020-01-01", end="2023-01-01",
              force_refresh=False, expiry_days=1):

    # -------------------------------
    # FORCE REFRESH
    # -------------------------------
    if force_refresh:
        logger.info(f"Force refresh for {symbol}")
        clear_cache(symbol)

    # -------------------------------
    # TRY CACHE
    # -------------------------------
    data = load_from_cache(symbol, expiry_days)

    if data is not None:
        return clean_data(data)

    # -------------------------------
    # DOWNLOAD
    # -------------------------------
    logger.info(f"Downloading {symbol}...")
    try:
        data = yf.download(symbol, start=start, end=end, progress=False)
    except Exception as exc:
        logger.warning(f"Download failed for {symbol}: {exc}")
        data = None

    # Auto-fallback to .NS if Indian ticker was passed without extension
    if (data is None or data.empty) and not symbol.endswith(".NS") and not symbol.endswith(".BO"):
        try:
            logger.info(f"Trying {symbol}.NS...")
            data = yf.download(f"{symbol}.NS", start=start, end=end, progress=False)
        except Exception as exc:
            logger.warning(f"Download fallback failed for {symbol}.NS: {exc}")

    # Flatten MultiIndex columns (yfinance returns these for single symbols)
    if data is not None and isinstance(data.columns, pd.MultiIndex):
        if "Close" in data.columns.get_level_values(0):
            data.columns = data.columns.get_level_values(0)
        elif "Close" in data.columns.get_level_values(1):
            data.columns = data.columns.get_level_values(1)
        else:
            data.columns = data.columns.get_level_values(0)

    # -------------------------------
    # VALIDATION BEFORE SAVE
    # -------------------------------
    if data is None or data.empty:
        raise ValueError(f"No data returned for {symbol}")

    # Save raw data
    save_to_cache(symbol, data)

    return clean_data(data)


# -------------------------------
# CLEAN + VALIDATE DATA
# -------------------------------
def clean_data(data):

    # Ensure required column
    if "Close" not in data.columns:
        raise ValueError("Missing 'Close' column")

    data = data.copy()

    # Convert safely
    data["Close"] = pd.to_numeric(data["Close"], errors="coerce")

    # Drop bad rows
    data = data.dropna(subset=["Close"])

    # Final validation
    if data.empty:
        raise ValueError("Data became empty after cleaning")

    # Keep Volume if available (needed for feature engineering)
    cols = ["Close"]
    if "Volume" in data.columns:
        data["Volume"] = pd.to_numeric(data["Volume"], errors="coerce")
        cols.append("Volume")

    return data[cols]