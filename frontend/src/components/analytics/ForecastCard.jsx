import TerminalPanel from "../ui/TerminalPanel";
import { formatPrice } from "../../utils/analyticsHelpers";

const TREND_CONFIG = {
  up: {
    label: "Bullish",
    arrow: "▲",
    text: "text-terminal-positive",
    border: "border-terminal-positive/35",
    bg: "bg-terminal-positive/10",
  },
  down: {
    label: "Bearish",
    arrow: "▼",
    text: "text-terminal-negative",
    border: "border-terminal-negative/35",
    bg: "bg-terminal-negative/10",
  },
  neutral: {
    label: "Neutral",
    arrow: "◆",
    text: "text-terminal-gold",
    border: "border-terminal-gold/30",
    bg: "bg-terminal-gold/5",
  },
};

function ConfidenceMeter({ value }) {
  const pct = Math.min(100, Math.max(0, Number(value) || 0));
  return (
    <div className="space-y-1">
      <div className="flex justify-between items-baseline">
        <span className="kpi-label">Confidence</span>
        <span className="font-mono text-sm font-semibold text-terminal-cyan tabular-nums">
          {pct.toFixed(1)}%
        </span>
      </div>
      <div className="score-bar-track h-1.5 max-w-none">
        <div
          className="score-bar-fill h-full transition-all duration-300"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

export default function ForecastCard({ forecast, symbol }) {
  const nextDay = forecast?.next_day ?? forecast;
  const available = nextDay?.available;
  const trend = (nextDay?.trend ?? "neutral").toLowerCase();
  const style = TREND_CONFIG[trend] ?? TREND_CONFIG.neutral;
  const confidence = nextDay?.confidence_pct ?? 0;
  const returnPct = nextDay?.predicted_return_pct ?? forecast?.lstm_delta_pct;
  const predictedPrice = nextDay?.predicted_price;
  const lastClose = nextDay?.last_close ?? forecast?.last_close;
  const method = nextDay?.method ?? "unknown";
  const modelLoaded = nextDay?.model_loaded;

  if (!available) {
    return (
      <TerminalPanel title="LSTM Forecast" subtitle={symbol} badge="1D">
        <p className="text-[10px] font-mono text-terminal-muted">
          {nextDay?.error || "Forecast unavailable — insufficient data or model."}
        </p>
      </TerminalPanel>
    );
  }

  return (
    <TerminalPanel
      title="LSTM Forecast"
      subtitle={`Next session · ${symbol}`}
      badge="1D"
    >
      <div className="space-y-3">
        <div
          className={`rounded-sm border px-3 py-2.5 ${style.border} ${style.bg}`}
        >
          <div className="flex items-center justify-between gap-2">
            <div>
              <p className="kpi-label">Trend</p>
              <p className={`font-mono text-xl font-bold tracking-tight ${style.text}`}>
                <span className="mr-1.5">{style.arrow}</span>
                {style.label}
              </p>
            </div>
            <div className="text-right">
              <p className="kpi-label">Next-day return</p>
              <p
                className={`font-mono text-lg font-semibold tabular-nums ${
                  (returnPct ?? 0) >= 0
                    ? "text-terminal-positive"
                    : "text-terminal-negative"
                }`}
              >
                {returnPct != null ? `${returnPct >= 0 ? "+" : ""}${returnPct}%` : "—"}
              </p>
            </div>
          </div>
        </div>

        <ConfidenceMeter value={confidence} />

        <div className="grid grid-cols-2 gap-2">
          <div className="rounded-sm border border-terminal-border bg-terminal-surface/80 px-2 py-1.5">
            <p className="kpi-label">Last close</p>
            <p className="font-mono text-sm font-semibold text-terminal-text tabular-nums">
              {formatPrice(lastClose)}
            </p>
          </div>
          <div className="rounded-sm border border-terminal-border bg-terminal-surface/80 px-2 py-1.5">
            <p className="kpi-label">Target (1D)</p>
            <p className="font-mono text-sm font-semibold text-terminal-cyan tabular-nums">
              {formatPrice(predictedPrice)}
            </p>
          </div>
        </div>

        <p className="text-[9px] font-mono text-terminal-muted uppercase tracking-wider">
          {modelLoaded ? "LSTM weights loaded" : "Momentum fallback"} · {method}
        </p>
      </div>
    </TerminalPanel>
  );
}
