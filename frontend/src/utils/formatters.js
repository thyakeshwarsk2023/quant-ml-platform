export function formatReturn(value, { suffix = "%", decimals = 2 } = {}) {
  if (value == null || Number.isNaN(Number(value))) {
    return { text: "—", className: "return-neutral" };
  }

  const num = Number(value);
  const className =
    num > 0 ? "return-positive" : num < 0 ? "return-negative" : "return-neutral";
  const sign = num > 0 ? "+" : "";

  return {
    text: `${sign}${num.toFixed(decimals)}${suffix}`,
    className,
  };
}

export function enrichRankingsWithReturns(rankings, portfolio) {
  const returnMap = Object.fromEntries(
    (portfolio?.selected_stocks ?? []).map((stock) => [
      stock.symbol,
      stock.return_pct,
    ])
  );

  return rankings.map((row) => ({
    ...row,
    return_pct:
      row.return_pct ?? returnMap[row.symbol] ?? null,
  }));
}
