import numpy as np


class BacktestEngine:
    def __init__(self, data, strategy, portfolio):
        self.data = data
        self.strategy = strategy
        self.portfolio = portfolio

    def run(self):
        equity_curve = []
        trade_returns = []

        prev_equity = self.portfolio.cash

        for i in range(len(self.data)):
            price = self.data["Close"].iloc[i]

            # 🔥 signal
            signal = self.strategy.generate_signal(i)

            # update portfolio
            self.portfolio.update(price, signal)

            current_equity = float(self.portfolio.equity)

            # 🔥 track returns (important for metrics)
            if prev_equity > 0:
                ret = (current_equity - prev_equity) / prev_equity
                trade_returns.append(ret)

            prev_equity = current_equity

            equity_curve.append({
                "timestamp": str(self.data.index[i]),
                "equity": current_equity
            })

        # =========================
        # 🔥 METRICS
        # =========================

        returns = np.array(trade_returns)

        # total return
        total_return = (
            (self.portfolio.equity - self.portfolio.initial_capital)
            / self.portfolio.initial_capital
        ) * 100

        # sharpe
        sharpe = 0
        if len(returns) > 1 and np.std(returns) != 0:
            sharpe = (np.mean(returns) / np.std(returns)) * np.sqrt(252)

        # volatility
        volatility = np.std(returns) * np.sqrt(252) if len(returns) > 1 else 0

        # win rate
        wins = returns[returns > 0]
        win_rate = len(wins) / len(returns) if len(returns) > 0 else 0

        # profit factor
        gains = returns[returns > 0].sum()
        losses = abs(returns[returns < 0].sum())
        profit_factor = (gains / losses) if losses != 0 else 0

        # max drawdown
        max_drawdown = self._max_drawdown(equity_curve)

        return {
            "return": float(total_return),
            "sharpe": float(sharpe),
            "max_drawdown": float(max_drawdown),

            # 🔥 NEW METRICS
            "volatility": float(volatility),
            "win_rate": float(win_rate),
            "profit_factor": float(profit_factor),

            "equity_curve": equity_curve
        }

    def _max_drawdown(self, equity_curve):
        if not equity_curve:
            return 0

        peak = equity_curve[0]["equity"]
        max_dd = 0

        for point in equity_curve:
            equity = point["equity"]

            if equity > peak:
                peak = equity

            if peak > 0:
                dd = (equity - peak) / peak
                max_dd = min(max_dd, dd)

        return abs(max_dd)