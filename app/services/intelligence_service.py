def score_strategy(r):
    
    sharpe = r.get("sharpe", 0)
    ret = r.get("return", 0)
    dd = abs(r.get("max_drawdown", 0))

    # 🔥 weighted scoring (THIS IS YOUR EDGE)
    score = (
        sharpe * 0.5 +
        ret * 0.3 -
        dd * 0.2
    )

    return score