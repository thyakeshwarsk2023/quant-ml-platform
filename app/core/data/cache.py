import os
import pandas as pd
from datetime import datetime, timedelta

CACHE_DIR = "data_cache"


# =========================
# 📁 PATH
# =========================
def get_cache_path(symbol):
    return os.path.join(CACHE_DIR, f"{symbol}.csv")


# =========================
# ⏱️ CACHE VALIDITY
# =========================
def is_cache_valid(path, expiry_days):
    if not os.path.exists(path):
        return False

    file_time = datetime.fromtimestamp(os.path.getmtime(path))
    return datetime.now() - file_time < timedelta(days=expiry_days)


# =========================
# 📦 LOAD CACHE (FIXED)
# =========================
def load_from_cache(symbol, expiry_days=1):
    path = get_cache_path(symbol)

    if os.path.exists(path) and is_cache_valid(path, expiry_days):
        print(f"📦 Using fresh cache for {symbol}")

        try:
            df = pd.read_csv(path, index_col=0, parse_dates=True)

            # =========================
            # 🔥 CRITICAL FIX: FORCE NUMERIC
            # =========================
            for col in ["Open", "High", "Low", "Close", "Volume"]:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")

            # =========================
            # 🔥 CLEAN BAD DATA
            # =========================
            df = df.replace([float("inf"), -float("inf")], pd.NA)
            df = df.dropna()

            # 🔥 MINIMUM LENGTH CHECK (important)
            if len(df) < 50:
                print(f"⚠️ Cache too small for {symbol}, ignoring")
                return None

            return df

        except Exception as e:
            print(f"⚠️ Corrupted cache for {symbol}: {e}")
            return None

    return None


# =========================
# 💾 SAVE CACHE
# =========================
def save_to_cache(symbol, data):
    os.makedirs(CACHE_DIR, exist_ok=True)

    path = get_cache_path(symbol)

    # 🔥 ensure index is datetime
    if not isinstance(data.index, pd.DatetimeIndex):
        data.index = pd.to_datetime(data.index, errors="coerce")

    data.to_csv(path)

    print(f"💾 Saved {symbol} to cache")


# =========================
# 🗑️ CLEAR CACHE
# =========================
def clear_cache(symbol):
    path = get_cache_path(symbol)

    if os.path.exists(path):
        os.remove(path)
        print(f"🗑️ Cache cleared for {symbol}")


# =========================
# 💣 CLEAR ALL CACHE (NEW)
# =========================
def clear_all_cache():
    if not os.path.exists(CACHE_DIR):
        return

    for file in os.listdir(CACHE_DIR):
        path = os.path.join(CACHE_DIR, file)
        try:
            os.remove(path)
        except Exception:
            pass

    print("🧹 Cleared entire cache")