import TerminalPanel from "../ui/TerminalPanel";

const ACTION_STYLES = {
  BUY: {
    border: "border-terminal-positive/40",
    bg: "bg-terminal-positive/10",
    text: "text-terminal-positive",
    label: "Accumulate",
  },
  SELL: {
    border: "border-terminal-negative/40",
    bg: "bg-terminal-negative/10",
    text: "text-terminal-negative",
    label: "Reduce",
  },
  HOLD: {
    border: "border-terminal-gold/30",
    bg: "bg-terminal-gold/5",
    text: "text-terminal-gold",
    label: "Neutral",
  },
};

const BIAS_DOT = {
  bullish: "bg-terminal-positive",
  bearish: "bg-terminal-negative",
  neutral: "bg-terminal-muted",
};

export default function RecommendationCard({ recommendation }) {
  if (!recommendation) {
    return (
      <TerminalPanel title="Signal" badge="REC">
        <p className="text-[10px] font-mono text-terminal-muted">No recommendation data</p>
      </TerminalPanel>
    );
  }

  const { action, confidence, summary, signals = [] } = recommendation;
  const style = ACTION_STYLES[action] ?? ACTION_STYLES.HOLD;

  return (
    <TerminalPanel title="Trade Signal" subtitle="Multi-factor composite" badge="REC">
      <div className="space-y-3">
        <div
          className={`rounded-sm border px-3 py-3 ${style.border} ${style.bg}`}
        >
          <div className="flex items-center justify-between gap-2">
            <div>
              <p className="kpi-label">Action</p>
              <p className={`font-mono text-2xl font-bold tracking-tight ${style.text}`}>
                {action}
              </p>
              <p className="text-[10px] text-terminal-muted mt-0.5">{style.label}</p>
            </div>
            <div className="text-right">
              <p className="kpi-label">Confidence</p>
              <p className="font-mono text-xl font-semibold text-terminal-text tabular-nums">
                {confidence}%
              </p>
            </div>
          </div>
          <p className="text-[11px] text-terminal-muted mt-2 leading-relaxed">{summary}</p>
        </div>

        <div>
          <p className="kpi-label mb-2">Factor breakdown</p>
          <ul className="space-y-1.5">
            {signals.map((sig) => (
              <li
                key={`${sig.name}-${sig.detail}`}
                className="flex items-start gap-2 text-[10px] font-mono border-b border-terminal-border/40 pb-1.5 last:border-0"
              >
                <span
                  className={`mt-1 w-1.5 h-1.5 rounded-full shrink-0 ${
                    BIAS_DOT[sig.bias] ?? BIAS_DOT.neutral
                  }`}
                />
                <span className="text-terminal-cyan shrink-0 w-16">{sig.name}</span>
                <span className="text-terminal-muted">{sig.detail}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </TerminalPanel>
  );
}
