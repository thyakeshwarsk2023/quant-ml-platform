import numpy as np


def compute_returns(arr):
    arr = np.array(arr)
    if len(arr) < 2:
        return np.array([])
    return np.diff(arr) / arr[:-1]


def sharpe_ratio(returns):
    if len(returns) == 0 or np.std(returns) == 0:
        return 0
    return np.mean(returns) / np.std(returns) * np.sqrt(252)


def max_drawdown(arr):
    arr = np.array(arr)

    if len(arr) == 0:
        return 0

    peak = arr[0]
    max_dd = 0

    for val in arr:
        peak = max(peak, val)
        dd = (peak - val) / peak
        max_dd = max(max_dd, dd)

    return max_dd


def compute_all_metrics(equity, buy_hold):
    equity = np.array(equity)
    bh = np.array(buy_hold).flatten()

    returns = compute_returns(equity)
    bh_returns = compute_returns(bh)

    return {
        "return": (equity[-1] / equity[0]) - 1 if len(equity) > 0 else 0,
        "sharpe": sharpe_ratio(returns),
        "max_drawdown": max_drawdown(equity),   # 🔥 FIX NAME

        "bh_return": (bh[-1] / bh[0]) - 1 if len(bh) > 0 else 0,
        "bh_sharpe": sharpe_ratio(bh_returns),
        "bh_drawdown": max_drawdown(bh)
    }