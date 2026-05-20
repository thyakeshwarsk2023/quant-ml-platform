from .base import Strategy


class RSIStrategy(Strategy):

    def __init__(self, data, period=14):
        super().__init__(data)
        self.period = period
        self.rsi = self._precompute_rsi()

    def _precompute_rsi(self):
        close = self.data["Close"]
        delta = close.diff()

        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(self.period).mean()
        avg_loss = loss.rolling(self.period).mean()

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def generate_signal(self, i):

        # Not enough data → do nothing
        if i < self.period:
            return 0

        rsi_now = self.rsi.iloc[i]

        # Trading logic
        if rsi_now < 30:
            return 1     # BUY
        elif rsi_now > 70:
            return -1    # SELL

        return 0