from .base import Strategy


class MovingAverageStrategy(Strategy):
    def __init__(self, data, short=20, long=50):
        super().__init__(data)
        self.short = short
        self.long = long

        # Precompute once (IMPORTANT for performance)
        close = self.data["Close"]

        self.short_ma = close.ewm(span=self.short).mean()
        self.long_ma = close.ewm(span=self.long).mean()

    def generate_signal(self, i):
        if i < self.long:
            return 0

        short_prev = self.short_ma.iloc[i - 1]
        long_prev = self.long_ma.iloc[i - 1]

        short_now = self.short_ma.iloc[i]
        long_now = self.long_ma.iloc[i]

        # Trend filter (long MA rising)
        trend_up = long_now > long_prev
        trend_down = long_now < long_prev

        # BUY: crossover + trend confirmation
        if short_prev <= long_prev and short_now > long_now and trend_up:
            return 1

        # SELL: crossover + downtrend
        elif short_prev >= long_prev and short_now < long_now and trend_down:
            return -1

        return 0