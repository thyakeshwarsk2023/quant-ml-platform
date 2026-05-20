import { formatReturn } from "../../utils/formatters";

const VARIANTS = {
  best: {
    label: "Best performer",
    badge: "TOP",
    border: "border-terminal-positive/35",
    bg: "bg-terminal-positive/10",
    accent: "text-terminal-positive",
  },
  worst: {
    label: "Worst performer",
    badge: "BTM",
    border: "border-terminal-negative/35",
    bg: "bg-terminal-negative/10",
    accent: "text-terminal-negative",
  },
};

export default function PerformerCard({ performer, variant = "best" }) {
  const style = VARIANTS[variant] ?? VARIANTS.best;

  if (!performer?.symbol) {
    return (
      <div
        className={`rounded-sm border border-terminal-border bg-terminal-surface/60 px-3 py-2.5`}
      >
        <p className="kpi-label">{style.label}</p>
        <p className="text-[10px] font-mono text-terminal-muted mt-1">—</p>
      </div>
    );
  }

  const ret = formatReturn(performer.return_pct);

  return (
    <div
      className={`rounded-sm border px-3 py-2.5 ${style.border} ${style.bg}`}
    >
      <div className="flex items-center justify-between gap-2 mb-1">
        <p className="kpi-label">{style.label}</p>
        <span className="font-mono text-[9px] uppercase tracking-wider text-terminal-muted">
          {style.badge}
        </span>
      </div>
      <p className="font-mono text-lg font-bold text-terminal-cyan tracking-tight">
        {performer.symbol}
      </p>
      <div className="flex items-baseline justify-between mt-1.5 gap-2">
        <p className={`font-mono text-sm font-semibold tabular-nums ${ret.className}`}>
          {ret.text}
        </p>
        <p className="font-mono text-[10px] text-terminal-muted tabular-nums">
          ML {Number(performer.score).toFixed(3)}
        </p>
      </div>
    </div>
  );
}
