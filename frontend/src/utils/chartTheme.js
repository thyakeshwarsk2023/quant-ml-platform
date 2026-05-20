/** Shared Chart.js styling for terminal charts */

export const TERMINAL_CHART_COLORS = {
  cyan: "#22d3ee",
  blue: "#3b82f6",
  positive: "#22c55e",
  negative: "#ef4444",
  grid: "rgba(148, 163, 184, 0.08)",
  tick: "#64748b",
  tooltipBg: "#0a0f18",
  tooltipBorder: "#1a2332",
};

export function buildEquityGradient(chart) {
  const { ctx, chartArea } = chart;
  if (!chartArea) {
    return "rgba(34, 197, 94, 0.15)";
  }

  const gradient = ctx.createLinearGradient(
    0,
    chartArea.top,
    0,
    chartArea.bottom
  );
  gradient.addColorStop(0, "rgba(34, 197, 94, 0.28)");
  gradient.addColorStop(0.55, "rgba(34, 211, 238, 0.08)");
  gradient.addColorStop(1, "rgba(34, 197, 94, 0)");
  return gradient;
}

export function getEquityChartOptions() {
  const c = TERMINAL_CHART_COLORS;

  return {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: "index",
      intersect: false,
    },
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: c.tooltipBg,
        borderColor: c.positive,
        borderWidth: 1,
        titleColor: "#e2e8f0",
        bodyColor: "#94a3b8",
        titleFont: { family: "'IBM Plex Mono', monospace", size: 11 },
        bodyFont: { family: "'IBM Plex Mono', monospace", size: 11 },
        padding: 10,
        displayColors: false,
        callbacks: {
          label(context) {
            const value = context.parsed?.y;
            if (value == null) {
              return "";
            }
            return `Equity  ${Number(value).toLocaleString(undefined, {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            })}`;
          },
        },
      },
    },
    scales: {
      x: {
        border: { display: false },
        grid: { color: c.grid, drawTicks: false },
        ticks: {
          color: c.tick,
          maxTicksLimit: 8,
          font: { size: 10, family: "'IBM Plex Mono', monospace" },
        },
      },
      y: {
        border: { display: false },
        grid: { color: c.grid },
        ticks: {
          color: c.tick,
          maxTicksLimit: 6,
          font: { size: 10, family: "'IBM Plex Mono', monospace" },
          callback(value) {
            if (value >= 1_000_000) {
              return `${(value / 1_000_000).toFixed(1)}M`;
            }
            if (value >= 1_000) {
              return `${(value / 1_000).toFixed(0)}K`;
            }
            return value;
          },
        },
      },
    },
  };
}

export const FEATURE_CHART_THEME = {
  grid: TERMINAL_CHART_COLORS.grid,
  tick: TERMINAL_CHART_COLORS.tick,
  tooltip: {
    background: TERMINAL_CHART_COLORS.tooltipBg,
    border: TERMINAL_CHART_COLORS.tooltipBorder,
  },
  barGradient: ["#0891b2", "#22d3ee"],
};

export const ANALYTICS_SERIES = {
  sma20: { key: "sma_20", label: "SMA 20", color: "#f59e0b" },
  sma50: { key: "sma_50", label: "SMA 50", color: "#a78bfa" },
  ema12: { key: "ema_12", label: "EMA 12", color: "#22d3ee" },
  ema26: { key: "ema_26", label: "EMA 26", color: "#3b82f6" },
  bbUpper: { key: "bb_upper", label: "BB Upper", color: "rgba(148,163,184,0.6)" },
  bbMiddle: { key: "bb_middle", label: "BB Mid", color: "rgba(148,163,184,0.35)" },
  bbLower: { key: "bb_lower", label: "BB Lower", color: "rgba(148,163,184,0.6)" },
};

export function getRechartsAxisProps() {
  return {
    tick: {
      fill: TERMINAL_CHART_COLORS.tick,
      fontSize: 10,
      fontFamily: "'IBM Plex Mono', monospace",
    },
    axisLine: false,
    tickLine: false,
  };
}

export function getRechartsGridProps() {
  return {
    stroke: TERMINAL_CHART_COLORS.grid,
    strokeDasharray: "2 4",
    vertical: false,
  };
}

export function getRechartsTooltipStyle() {
  return {
    contentStyle: {
      background: TERMINAL_CHART_COLORS.tooltipBg,
      border: `1px solid ${TERMINAL_CHART_COLORS.tooltipBorder}`,
      borderRadius: 2,
      fontFamily: "'IBM Plex Mono', monospace",
      fontSize: 11,
    },
    labelStyle: { color: "#e2e8f0" },
    itemStyle: { color: "#94a3b8" },
  };
}
