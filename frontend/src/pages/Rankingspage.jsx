import { useEffect, useState } from "react";

import Sidebar from "../components/Sidebar";
import RankingsTable from "../components/RankingsTable";
import { getRankings } from "../api/api";
import {
  getApiErrorMessage,
  parseRankingsResponse,
} from "../utils/apiHelpers";

export default function RankingsPage() {
  const [rankings, setRankings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isMounted = true;

    async function loadRankings() {
      try {
        const res = await getRankings(50);

        if (!isMounted) {
          return;
        }

        setRankings(parseRankingsResponse(res.data));
        setError(null);
      } catch (err) {
        console.error(err);

        if (!isMounted) {
          return;
        }

        setError(getApiErrorMessage(err, "Failed to load rankings"));
        setRankings([]);
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    loadRankings();

    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <div className="terminal-shell terminal-grid-bg min-h-screen">
      <Sidebar />

      <main className="ml-56 px-4 py-4 max-w-[calc(100vw-14rem)]">
        <header className="border-b border-terminal-border pb-3 mb-4">
          <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-terminal-muted">
            Rankings
          </p>
          <h1 className="text-lg font-semibold text-terminal-text tracking-tight">
            ML Stock Rankings
          </h1>
        </header>

        <RankingsTable
          rankings={rankings}
          loading={loading}
          error={error}
          showReturns={true}
          maxHeight="600px"
        />
      </main>
    </div>
  );
}
