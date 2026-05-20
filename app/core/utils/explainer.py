def explain_strategy(metrics):
    explanation = []

    if metrics["return"] > 0.5:
        explanation.append("high return")
    if metrics["sharpe"] > 1:
        explanation.append("good risk-adjusted performance")

    if metrics["drawdown"] < 0.25:
        explanation.append("low drawdown")

    if not explanation:
        return "moderate performance"

    return ", ".join(explanation)
