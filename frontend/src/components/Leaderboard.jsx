import { useEffect, useState } from "react";
import { getLeaderboard } from "../api/api";
import { parseLeaderboardResponse } from "../utils/apiHelpers";
import { formatReturn } from "../utils/formatters";

export default function Leaderboard({ embedded = false }) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    const fetchData = async () => {
      try {
        const res = await getLeaderboard();

        if (!isMounted) {
          return;
        }

        setData(parseLeaderboardResponse(res.data));
      } catch (err) {
        if (import.meta.env.DEV) {
          console.warn("Leaderboard fetch:", err);
        }

        if (!isMounted) {
          return;
        }

        setData([]);
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
      <p className="text-terminal-muted text-xs font-mono py-2">
        Loading leaderboard…
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
                  {row.symbol || "—"}
                </td>
                <td className="text-right text-terminal-slate">
                  {row.sharpe ? row.sharpe.toFixed(2) : "—"}
                </td>
                <td className={`text-right ${ret.className}`}>
                  {ret.text}
                </td>
                <td className="text-right text-terminal-cyan">
                  {row.ml_score ? row.ml_score.toFixed(2) : "—"}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
