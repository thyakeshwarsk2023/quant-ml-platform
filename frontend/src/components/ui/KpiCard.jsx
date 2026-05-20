const toneStyles = {
  cyan: {
    card: "",
    value: "text-terminal-cyan",
    accent: "from-cyan-500/8 to-transparent",
    border: "border-l-2 border-l-cyan-500/50",
  },
  green: {
    card: "kpi-card-positive",
    value: "text-terminal-positive",
    accent: "from-emerald-500/8 to-transparent",
    border: "border-l-2 border-l-emerald-500/50",
  },
  red: {
    card: "",
    value: "text-terminal-negative",
    accent: "from-red-500/8 to-transparent",
    border: "border-l-2 border-l-red-500/50",
  },
  blue: {
    card: "",
    value: "text-terminal-blue",
    accent: "from-blue-500/8 to-transparent",
    border: "border-l-2 border-l-blue-500/50",
  },
  slate: {
    card: "",
    value: "text-terminal-muted",
    accent: "from-slate-500/5 to-transparent",
    border: "border-l-2 border-l-slate-500/30",
  },
};

export default function KpiCard({
  label,
  value,
  subValue,
  tone = "cyan",
  className = "",
}) {
  const styles = toneStyles[tone] ?? toneStyles.cyan;

  return (
    <div className={`kpi-card ${styles.card} ${styles.border} ${className}`}>
      <div
        className={`absolute inset-0 bg-gradient-to-br ${styles.accent} pointer-events-none`}
        aria-hidden="true"
      />
      <p className="kpi-label relative">{label}</p>
      <p className={`kpi-value relative ${styles.value}`}>{value}</p>
      {subValue && (
        <p className="text-[11px] font-mono text-terminal-muted mt-1 relative">
          {subValue}
        </p>
      )}
    </div>
  );
}
