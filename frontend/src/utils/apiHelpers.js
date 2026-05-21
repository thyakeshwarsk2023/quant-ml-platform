export function asArray(value) {
  return Array.isArray(value) ? value : [];
}

export function parseRankingsResponse(data) {
  if (data?.status === "error") {
    return [];
  }

  return asArray(data?.results).map((row) => ({
    symbol: row?.symbol ?? "—",
    score: Number(row?.score) || 0,
  }));
}

export function parsePortfolioResponse(data) {
  if (!data || typeof data !== "object") {
    return null;
  }

  if (data.status === "error") {
    return {
      status: "error",
      portfolio_size: 0,
      portfolio_return: 0,
      selected_stocks: [],
      analytics: null,
      error: data.error || "Unknown error",
    };
  }

  const analytics = data.analytics ?? {};

  return {
    status: data.status ?? "unknown",
    portfolio_size: data.portfolio_size ?? 0,
    portfolio_return: Number(data.portfolio_return) || 0,
    selected_stocks: asArray(data.selected_stocks).map((stock) => ({
      symbol: stock?.symbol ?? "—",
      score: Number(stock?.score) || 0,
      return_pct: Number(stock?.return_pct) || 0,
    })),
    analytics: {
      sharpe_ratio: Number(analytics.sharpe_ratio) || 0,
      volatility_pct: Number(analytics.volatility_pct) || 0,
      period: analytics.period ?? "1mo",
      benchmark: {
        label: analytics.benchmark?.label ?? "NIFTY50",
        ticker: analytics.benchmark?.ticker ?? "^NSEI",
        return_pct: Number(analytics.benchmark?.return_pct) || 0,
        excess_return_pct: Number(analytics.benchmark?.excess_return_pct) || 0,
      },
      best_performer: analytics.best_performer ?? null,
      worst_performer: analytics.worst_performer ?? null,
    },
  };
}

export function parseLeaderboardResponse(data) {
  return asArray(data).map((row) => ({
    symbol: row?.symbol ?? "—",
    sharpe: Number(row?.sharpe) || 0,
    return: Number(row?.return) || 0,
    ml_score: Number(row?.ml_score) || 0,
    explanation: row?.explanation ?? "",
  }));
}

export function parseEquityResponse(data) {
  return asArray(data)
    .map((point) => ({
      timestamp: point?.timestamp ?? "",
      equity: Number(point?.equity) || 0,
    }))
    .filter((point) => point.timestamp && Number.isFinite(point.equity));
}

export function getApiErrorMessage(error, fallback = "Request failed") {
  if (
    error?.code === "NO_API_BASE" ||
    error?.message === "VITE_API_BASE_URL_NOT_SET"
  ) {
    return "API URL not configured. Set VITE_API_BASE_URL in deployment settings.";
  }

  const detail = error?.response?.data?.detail;

  if (typeof detail === "string") {
    return detail;
  }

  if (Array.isArray(detail)) {
    return detail.map((item) => item?.msg ?? String(item)).join(", ");
  }

  const status = error?.response?.status;
  if (status === 404) {
    return "Data unavailable for this request.";
  }

  return error?.message || fallback;
}

export function formatChartLabel(timestamp) {
  if (!timestamp) {
    return "";
  }

  const date = new Date(timestamp);

  if (Number.isNaN(date.getTime())) {
    return String(timestamp);
  }

  return date.toLocaleDateString();
}
