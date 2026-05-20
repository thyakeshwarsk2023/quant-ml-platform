import TerminalPanel from "../ui/TerminalPanel";
import PerformerCard from "./PerformerCard";
import { formatReturn } from "../../utils/formatters";

export default function PortfolioAnalytics({ analytics, portfolioReturn }) {
  if (!analytics) {
    return null;
  }

  const bench = analytics.benchmark ?? {};
  const portRet = formatReturn(portfolioReturn);
  const benchRet = formatReturn(bench.return_pct);
  const excessRet = formatReturn(bench.excess_return_pct);
  const sharpe = Number(analytics.sharpe_ratio) || 0;
  const vol = Number(analytics.volatility_pct) || 0;

  return (
    <div className="space-y-3">
      <TerminalPanel
        title="Risk Metrics"
        subtitle={`${analytics.period ?? "1mo"} equal-weight book`}
        badge="RISK"
      >
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
          <div className="kpi-card !p-2">
            <p className="kpi-label">Sharpe</p>
            <p
              className={`font-mono text-base font-semibold tabular-nums ${
                sharpe >= 1 ? "text-terminal-positive" : "text-terminal-cyan"
              }`}
            >
              {sharpe.toFixed(2)}
            </p>
          </div>
          <div className="kpi-card !p-2">
            <p className="kpi-label">Volatility</p>
            <p className="font-mono text-base font-semibold text-terminal-gold tabular-nums">
              {vol.toFixed(1)}%
            </p>
          </div>
          <div className="kpi-card !p-2">
            <p className="kpi-label">Portfolio</p>
            <p className={`font-mono text-base font-semibold tabular-nums ${portRet.className}`}>
              {portRet.text}
            </p>
          </div>
          <div className="kpi-card !p-2">
            <p className="kpi-label">vs {bench.label ?? "NIFTY50"}</p>
            <p className={`font-mono text-base font-semibold tabular-nums ${excessRet.className}`}>
              {excessRet.text}
            </p>
          </div>
        </div>
      </TerminalPanel>

      <TerminalPanel
        title="Benchmark"
        subtitle={`${bench.label ?? "NIFTY50"} · ${bench.ticker ?? "^NSEI"}`}
        badge="IDX"
      >
        <div className="grid grid-cols-3 gap-2 text-center sm:text-left">
          <div className="rounded-sm border border-terminal-border bg-terminal-surface/80 px-2 py-1.5">
            <p className="kpi-label">Index 1M</p>
            <p className={`font-mono text-sm font-semibold tabular-nums ${benchRet.className}`}>
              {benchRet.text}
            </p>
          </div>
          <div className="rounded-sm border border-terminal-border bg-terminal-surface/80 px-2 py-1.5">
            <p className="kpi-label">Portfolio 1M</p>
            <p className={`font-mono text-sm font-semibold tabular-nums ${portRet.className}`}>
              {portRet.text}
            </p>
          </div>
          <div className="rounded-sm border border-terminal-border bg-terminal-surface/80 px-2 py-1.5">
            <p className="kpi-label">Excess</p>
            <p className={`font-mono text-sm font-semibold tabular-nums ${excessRet.className}`}>
              {excessRet.text}
            </p>
          </div>
        </div>
        <p className="text-[10px] font-mono text-terminal-muted mt-2">
          Excess return = portfolio compounded 1M return minus index 1M return.
        </p>
      </TerminalPanel>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
        <PerformerCard performer={analytics.best_performer} variant="best" />
        <PerformerCard performer={analytics.worst_performer} variant="worst" />
      </div>
    </div>
  );
}
