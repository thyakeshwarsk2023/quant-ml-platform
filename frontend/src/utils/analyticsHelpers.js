export function parseAnalyticsResponse(data) {
  if (!data || data.status !== "success") {
    throw new Error(data?.detail || data?.error || "Invalid analytics response");
  }

  const forecast = data.forecast ?? { points: [], horizon_days: 0 };

  return {
    symbol: data.symbol,
    period: data.period,
    asOf: data.as_of,
    quote: data.quote ?? {},
    bars: Array.isArray(data.bars) ? data.bars : [],
    forecast: {
      ...forecast,
      next_day: forecast.next_day ?? null,
    },
    recommendation: data.recommendation ?? null,
  };
}

export function parseForecastResponse(data) {
  if (!data || data.status !== "success") {
    throw new Error(data?.detail || data?.error || "Invalid forecast response");
  }

  return {
    symbol: data.symbol,
    period: data.period,
    asOf: data.as_of,
    lastBarDate: data.last_bar_date,
    forecast: data.forecast ?? {},
  };
}

export function formatPrice(value, digits = 2) {
  if (value == null || Number.isNaN(Number(value))) {
    return "—";
  }
  return Number(value).toLocaleString(undefined, {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
}

export function formatVolume(value) {
  if (value == null) {
    return "—";
  }
  const n = Number(value);
  if (n >= 1_000_000_000) {
    return `${(n / 1_000_000_000).toFixed(2)}B`;
  }
  if (n >= 1_000_000) {
    return `${(n / 1_000_000).toFixed(2)}M`;
  }
  if (n >= 1_000) {
    return `${(n / 1_000).toFixed(1)}K`;
  }
  return String(n);
}

export function shortDate(dateStr) {
  if (!dateStr) {
    return "";
  }
  const d = new Date(`${dateStr}T00:00:00`);
  return d.toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

export const DEFAULT_OVERLAYS = {
  sma20: true,
  sma50: true,
  ema12: false,
  ema26: false,
  bollinger: true,
};
