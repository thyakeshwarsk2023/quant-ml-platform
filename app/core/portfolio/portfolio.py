import numpy as np
class Portfolio:
    def __init__(self, cash=100000):
        self.initial_capital = float(cash)
        self.cash = float(cash)
        self.position = 0.0  # number of shares

        self.equity = float(cash)
        self.prev_equity = float(cash)

        self.returns = []
        self.equity_curve = []

    def update(self, price, signal):
        price = float(price)
        signal = int(signal)

    # =========================
    # 🔥 EXECUTE SIGNAL
    # =========================
    # 
        if signal == 1 and self.position == 0:
            self.position = self.cash / price
            self.cash = 0.0

        elif signal == -1 and self.position > 0:
            self.cash = self.position * price
            self.position = 0.0

        new_equity = float(self.cash + self.position * price)

    # =========================
    # 🔥 TRACK RETURNS (SAFE)
    # =========================
        if self.prev_equity > 0:
            ret = (new_equity - self.prev_equity) / self.prev_equity

            # 🔥 avoid NaN / Inf pollution
            if np.isfinite(ret):
                self.returns.append(ret)

        self.equity = new_equity
        self.prev_equity = new_equity

    # =========================
    # 🔥 STORE CURVE
    # =========================
        self.equity_curve.append(new_equity)