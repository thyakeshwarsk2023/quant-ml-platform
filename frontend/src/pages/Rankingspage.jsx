import { useEffect, useState } from "react";

import Sidebar from "../components/Sidebar";
import RankingsTable from "../components/RankingsTable";
import { getPortfolio, getRankings } from "../api/api";
import {
  getApiErrorMessage,
  parsePortfolioResponse,
  parseRankingsResponse,
} from "../utils/apiHelpers";
import { enrichRankingsWithReturns } from "../utils/formatters";

export default function RankingsPage() {
  const [rankings, setRankings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isMounted = true;

    async function loadRankings() {
      try {
        const [rankOutcome, portOutcome] = await Promise.allSettled([
          getRankings(50),
          getPortfolio(50),
        ]);

        if (!isMounted) {
          return;
        }

        let parsedRanks = [];
        let parsedPort = null;

        if (rankOutcome.status === "fulfilled") {
          parsedRanks = parseRankingsResponse(rankOutcome.value.data);
        } else {
          setError(getApiErrorMessage(rankOutcome.reason, "Failed to load rankings"));
        }

        if (portOutcome.status === "fulfilled") {
          parsedPort = parsePortfolioResponse(portOutcome.value.data);
        }

        const enriched = enrichRankingsWithReturns(parsedRanks, parsedPort);
        setRankings(enriched);
      } catch (err) {
        if (import.meta.env.DEV) {
          console.error(err);
        }

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
