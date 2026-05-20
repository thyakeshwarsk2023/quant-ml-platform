import TerminalPanel from "./ui/TerminalPanel";
import { formatReturn } from "../utils/formatters";

function ScoreBar({ score, maxScore }) {
  const width =
    maxScore > 0
      ? Math.min(100, (Math.abs(score) / maxScore) * 100)
      : 0;

  return (
    <div className="flex items-center gap-2 justify-end">
      <div className="score-bar-track">
        <div className="score-bar-fill" style={{ width: `${width}%` }} />
      </div>
    </div>
  );
}

export default function PortfolioSummary({
  portfolio,
  loading = false,
  error = null,
  compact = false,
}) {
  if (loading) {
    return (
      <TerminalPanel title="Portfolio" badge="PF">
        <p className="text-terminal-muted text-xs font-mono">
          Loading portfolio…
        </p>
      </TerminalPanel>
    );
  }

  if (error) {
    return (
      <TerminalPanel title="Portfolio" badge="PF">
        <p className="text-terminal-negative text-xs font-mono">{error}</p>
      </TerminalPanel>
    );
  }

  if (!portfolio) {
    return (
      <TerminalPanel title="Portfolio" badge="PF">
        <p className="text-terminal-muted text-xs font-mono">
          Portfolio unavailable
        </p>
      </TerminalPanel>
    );
  }

  const stocks = portfolio.selected_stocks || [];
  const analytics = portfolio.analytics;
  const bestStock =
    analytics?.best_performer ??
    (stocks.length > 0
      ? [...stocks].sort(
          (a, b) => (Number(b.return_pct) || 0) - (Number(a.return_pct) || 0)
        )[0]
      : null);
  const retFmt = formatReturn(portfolio.portfolio_return);
  const maxScore = Math.max(
    ...stocks.map((s) => Math.abs(Number(s.score) || 0)),
    0.0001
  );

  return (
    <TerminalPanel
      title="Portfolio"
      subtitle="Equal-weight top-K simulation"
      badge="PF"
      className="h-full"
    >
      <div className={`grid ${compact ? "grid-cols-4" : "grid-cols-2"} gap-2 mb-3`}>
        <div className="rounded-sm border border-terminal-border bg-terminal-surface/80 px-2 py-1.5">
          <p className="kpi-label">Return</p>
          <p className={`font-mono text-sm font-semibold ${retFmt.className}`}>
            {retFmt.text}
          </p>
        </div>
        <div className="rounded-sm border border-terminal-border bg-terminal-surface/80 px-2 py-1.5">
          <p className="kpi-label">Positions</p>
          <p className="font-mono text-sm font-semibold text-terminal-cyan">
            {stocks.length}
          </p>
        </div>
        <div className="rounded-sm border border-terminal-border bg-terminal-surface/80 px-2 py-1.5">
          <p className="kpi-label">Top</p>
          <p className="font-mono text-sm font-semibold text-terminal-text truncate">
            {bestStock?.symbol || "—"}
          </p>
        </div>
        <div className="rounded-sm border border-terminal-border bg-terminal-surface/80 px-2 py-1.5">
          <p className="kpi-label">Sharpe</p>
          <p className="font-mono text-sm font-semibold text-terminal-blue tabular-nums">
            {(Number(analytics?.sharpe_ratio) || 0).toFixed(2)}
          </p>
        </div>
      </div>

      {stocks.length > 0 && (
        <div
          className="terminal-table-wrap"
          style={{ maxHeight: compact ? "140px" : "200px" }}
        >
          <table className="terminal-table">
            <thead>
              <tr>
                <th className="text-left">Symbol</th>
                <th className="text-right">Score</th>
                <th className="text-right">1M Ret</th>
              </tr>
            </thead>
            <tbody>
              {stocks.map((stock, index) => {
                const score = Number(stock.score) || 0;
                const ret = formatReturn(stock.return_pct);

                return (
                  <tr key={stock.symbol || `stock-${index}`}>
                    <td className="text-terminal-cyan font-semibold">
                      {stock.symbol || "—"}
                    </td>
                    <td>
                      <ScoreBar score={score} maxScore={maxScore} />
                    </td>
                    <td className={`text-right ${ret.className}`}>
                      {ret.text}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </TerminalPanel>
  );
}
