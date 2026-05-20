import { ANALYTICS_SERIES } from "../../utils/chartTheme";

const TOGGLES = [
  { id: "sma20", label: ANALYTICS_SERIES.sma20.label },
  { id: "sma50", label: ANALYTICS_SERIES.sma50.label },
  { id: "ema12", label: ANALYTICS_SERIES.ema12.label },
  { id: "ema26", label: ANALYTICS_SERIES.ema26.label },
  { id: "bollinger", label: "Bollinger" },
];

export default function IndicatorToggles({ overlays, onChange }) {
  return (
    <div className="flex flex-wrap gap-1.5">
      {TOGGLES.map(({ id, label }) => {
        const active = overlays[id];
        return (
          <button
            key={id}
            type="button"
            onClick={() => onChange({ ...overlays, [id]: !active })}
            className={`font-mono text-[9px] uppercase tracking-wider px-2 py-1 rounded-sm border transition-colors ${
              active
                ? "border-terminal-cyan/40 bg-terminal-cyan/10 text-terminal-cyan"
                : "border-terminal-border text-terminal-muted hover:text-terminal-text"
            }`}
          >
            {label}
          </button>
        );
      })}
    </div>
  );
}
