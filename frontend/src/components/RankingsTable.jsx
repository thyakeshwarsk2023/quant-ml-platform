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
      <span className="text-terminal-cyan w-12 text-right">
        {score.toFixed(3)}
      </span>
    </div>
  );
}

export default function RankingsTable({
  rankings = [],
  loading = false,
  error = null,
  emptyMessage = "No rankings available",
  showReturns = true,
  maxHeight = "280px",
}) {
  if (loading) {
    return (
      <p className="text-terminal-muted text-xs font-mono py-3">
        Loading rankings…
      </p>
    );
  }

  if (error) {
    return (
      <p className="text-terminal-negative text-xs font-mono py-3">{error}</p>
    );
  }

  if (!rankings.length) {
    return (
      <p className="text-terminal-muted text-xs font-mono py-3">
        {emptyMessage}
      </p>
    );
  }

  const maxScore = Math.max(
    ...rankings.map((row) => Math.abs(Number(row.score) || 0)),
    0.0001
  );

  return (
    <div
      className="terminal-table-wrap"
      style={{ maxHeight }}
    >
      <table className="terminal-table">
        <thead>
          <tr>
            <th className="text-left w-8">#</th>
            <th className="text-left">Symbol</th>
            {showReturns && (
              <th className="text-right w-20">1M Ret</th>
            )}
            <th className="text-right">ML Score</th>
          </tr>
        </thead>
        <tbody>
          {rankings.map((row, index) => {
            const score = Number(row.score) || 0;
            const ret = formatReturn(row.return_pct);

            return (
              <tr key={row.symbol || `rank-${index}`}>
                <td className="text-terminal-muted">{index + 1}</td>
                <td className="text-terminal-cyan font-semibold">
                  {row.symbol}
                </td>
                {showReturns && (
                  <td className={`text-right ${ret.className}`}>
                    {row.return_pct != null ? ret.text : "—"}
                  </td>
                )}
                <td>
                  <ScoreBar score={score} maxScore={maxScore} />
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
