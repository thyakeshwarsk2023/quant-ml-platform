from .base import Strategy
import numpy as np


class CombinedStrategy(Strategy):

    def __init__(self, data, short=20, long=50, rsi_period=14):
        super().__init__(data)

        close = self.data["Close"]

        # =========================
        # EMA
        # =========================
        self.short_ma = close.ewm(span=short, adjust=False).mean()
        self.long_ma = close.ewm(span=long, adjust=False).mean()

        # =========================
        # RSI
        # =========================
        delta = close.diff()

        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(window=rsi_period, min_periods=rsi_period).mean()
        avg_loss = loss.rolling(window=rsi_period, min_periods=rsi_period).mean()

        rs = avg_gain / (avg_loss + 1e-9)
        self.rsi = 100 - (100 / (1 + rs))

        # =========================
        # MOMENTUM
        # =========================
        self.momentum = close.pct_change(5)

    # =========================
    # SIGNAL GENERATION
    # =========================
    def generate_signal(self, i):

        if i < 50:
            return 0

        try:
            short_now = self.short_ma.iloc[i]
            long_now = self.long_ma.iloc[i]
            long_prev = self.long_ma.iloc[i - 1]

            rsi_now = self.rsi.iloc[i]
            mom = self.momentum.iloc[i]

            # 🔥 STRICT VALIDATION (handles NaN + Inf)
            values = [short_now, long_now, long_prev, rsi_now, mom]

            if not all(np.isfinite(v) for v in values):
                return 0

            trend_up = long_now > long_prev
            trend_down = long_now < long_prev

            # =========================
            # BUY
            # =========================
            if (
                short_now > long_now
                and trend_up
                and rsi_now < 35
                and mom > 0
            ):
                return 1

            # =========================
            # SELL
            # =========================
            elif (
                short_now < long_now
                and trend_down
                and rsi_now > 65
                and mom < 0
            ):
                return -1

            return 0

        except Exception:
            return 0