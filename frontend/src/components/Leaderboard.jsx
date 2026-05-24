import { useEffect, useState } from "react";
import { getLeaderboard } from "../api/api";
import { getApiErrorMessage, parseLeaderboardResponse } from "../utils/apiHelpers";
import { formatReturn } from "../utils/formatters";

export default function Leaderboard({ embedded = false }) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isMounted = true;

    const fetchData = async () => {
      try {
        const res = await getLeaderboard();

        if (!isMounted) {
          return;
        }

        setData(parseLeaderboardResponse(res.data));
        setError(null);
      } catch (err) {
        if (!isMounted) {
          return;
        }

        setData([]);
        setError(getApiErrorMessage(err, "Leaderboard unavailable"));
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    fetchData();

    return () => {
      isMounted = false;
    };
  }, []);

  if (loading) {
    return (
      <div className="space-y-2 py-1">
        {[0, 1, 2, 3].map((row) => (
          <div
            key={row}
            className="h-7 rounded-sm border border-terminal-border/50 bg-terminal-surface/60 animate-pulse"
          />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <p className="text-terminal-negative text-xs font-mono py-2">
        {error}
      </p>
    );
  }

  if (!data.length) {
    return (
      <p className="text-terminal-muted text-xs font-mono py-2">
        No backtest results. Run a symbol backtest to populate.
      </p>
    );
  }

  return (
    <div
      className={`terminal-table-wrap ${
        embedded ? "max-h-[240px]" : "max-h-[320px]"
      }`}
    >
      <table className="terminal-table">
        <thead>
          <tr>
            <th className="text-left">Symbol</th>
            <th className="text-right">Sharpe</th>
            <th className="text-right">Return</th>
            <th className="text-right">ML</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row, index) => {
            const ret = formatReturn(row.return);

            return (
              <tr key={row.symbol || `leader-${index}`}>
                <td className="text-terminal-cyan font-semibold">
                  {row.symbol || "-"}
                </td>
                <td className="text-right text-terminal-slate">
                  {row.sharpe ? row.sharpe.toFixed(2) : "-"}
                </td>
                <td className={`text-right ${ret.className}`}>
                  {ret.text}
                </td>
                <td className="text-right text-terminal-cyan">
                  {row.ml_score ? row.ml_score.toFixed(2) : "-"}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
