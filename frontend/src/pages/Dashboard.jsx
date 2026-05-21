import { useEffect, useMemo, useState } from "react";

import Sidebar from "../components/Sidebar";
import PortfolioSummary from "../components/PortfolioSummary";
import RunPanel from "../components/RunPanel";
import EquityChart from "../components/EquityChart";
import Leaderboard from "../components/Leaderboard";
import FeatureImportance from "../components/FeatureImportance";
import RankingsTable from "../components/RankingsTable";
import KpiCard from "../components/ui/KpiCard";
import TerminalPanel from "../components/ui/TerminalPanel";

import { getPortfolio, getRankings } from "../api/api";
import {
  getApiErrorMessage,
  parsePortfolioResponse,
  parseRankingsResponse,
} from "../utils/apiHelpers";
import {
  enrichRankingsWithReturns,
  formatReturn,
} from "../utils/formatters";

export default function Dashboard() {
  const [runId, setRunId] = useState(null);
  const [portfolio, setPortfolio] = useState(null);
  const [rankings, setRankings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isMounted = true;

    async function loadData() {
      setLoading(true);
      setError(null);

      try {
        const [portfolioOutcome, rankingsOutcome] = await Promise.allSettled([
          getPortfolio(),
          getRankings(),
        ]);

        if (!isMounted) {
          return;
        }

        const messages = [];

        if (portfolioOutcome.status === "fulfilled") {
          setPortfolio(parsePortfolioResponse(portfolioOutcome.value.data));
        } else {
          setPortfolio(null);
          messages.push(
            getApiErrorMessage(
              portfolioOutcome.reason,
              "Portfolio data unavailable"
            )
          );
        }

        if (rankingsOutcome.status === "fulfilled") {
          setRankings(parseRankingsResponse(rankingsOutcome.value.data));
        } else {
          setRankings([]);
          messages.push(
            getApiErrorMessage(rankingsOutcome.reason, "Rankings unavailable")
          );
        }

        setError(messages.length ? messages.join(" · ") : null);
      } catch (err) {
        if (!isMounted) {
          return;
        }

        if (import.meta.env.DEV) {
          console.error(err);
        }

        setError(getApiErrorMessage(err, "Failed to load dashboard data"));
        setPortfolio(null);
        setRankings([]);
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    loadData();

    return () => {
      isMounted = false;
    };
  }, []);

  const enrichedRankings = useMemo(
    () => enrichRankingsWithReturns(rankings, portfolio),
    [rankings, portfolio]
  );

  const portfolioReturn = portfolio?.portfolio_return ?? null;
  const returnFmt = formatReturn(portfolioReturn);

  if (loading) {
    return (
      <div className="terminal-shell flex items-center justify-center min-h-screen">
        <Sidebar />
        <div className="ml-56 flex-1 flex items-center justify-center">
          <div className="text-center">
            <p className="font-mono text-xs uppercase tracking-[0.2em] text-terminal-muted">
              Initializing
            </p>
            <p className="font-mono text-terminal-cyan mt-2 animate-pulse">
              Research terminal…
            </p>
          </div>
        </div>
      </div>
    );
  }

  const now = new Date().toLocaleString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <div className="terminal-shell terminal-grid-bg min-h-screen">
      <Sidebar />

      <main className="ml-56 px-4 py-4 max-w-[calc(100vw-14rem)] space-y-4">
        <header className="flex flex-wrap items-end justify-between gap-2 border-b border-terminal-border pb-3">
          <div>
            <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-terminal-muted">
              Quant Research Terminal
            </p>
            <h1 className="text-lg sm:text-xl font-semibold text-terminal-text tracking-tight">
              Cross-Sectional ML Desk
            </h1>
          </div>
          <p className="font-mono text-[10px] text-terminal-muted tabular-nums">
            {now} · LIVE
          </p>
        </header>

        {error && (
          <div className="rounded-sm border border-terminal-negative/40 bg-terminal-negative/10 px-3 py-2 text-xs font-mono text-terminal-negative">
            {error}
          </div>
        )}

        <section className="grid grid-cols-2 lg:grid-cols-4 gap-3">
          <KpiCard
            label="Portfolio Return"
            value={portfolioReturn !== null ? returnFmt.text : "—"}
            tone={
              portfolioReturn > 0
                ? "green"
                : portfolioReturn < 0
                  ? "red"
                  : "slate"
            }
            subValue="Simulated 1M"
          />
          <KpiCard label="Universe" value="Top‑K" tone="blue" subValue="Cached signals" />
          <KpiCard label="Model" value="LightGBM" tone="cyan" subValue="Ranker v1" />
          <KpiCard
            label="Ranked"
            value={String(rankings.length)}
            tone="slate"
            subValue="Active signals"
          />
        </section>

        <section className="grid grid-cols-1 xl:grid-cols-12 gap-3">
          <div className="xl:col-span-5 min-h-[280px]">
            <PortfolioSummary
              portfolio={portfolio}
              loading={false}
              error={error && !portfolio ? error : null}
              compact
            />
          </div>

          <div className="xl:col-span-4 min-h-[280px]">
            <TerminalPanel
              title="ML Rankings"
              subtitle="Top signals · score vs universe"
              badge="RANK"
              className="h-full"
            >
              <RankingsTable
                rankings={enrichedRankings.slice(0, 12)}
                maxHeight="240px"
              />
            </TerminalPanel>
          </div>

          <div className="xl:col-span-3 min-h-[280px]">
            <RunPanel setRunId={setRunId} compact />
          </div>
        </section>

        <section className="grid grid-cols-1 lg:grid-cols-2 gap-3">
          <TerminalPanel
            title="Backtest Leaderboard"
            subtitle="Per-symbol strategy metrics"
            badge="BT"
            className="min-h-[340px]"
          >
            <Leaderboard embedded />
          </TerminalPanel>

          <TerminalPanel
            title="Equity Curve"
            subtitle={runId ? `Run #${runId}` : "Awaiting backtest"}
            badge="PNL"
            className="min-h-[340px]"
            bodyClassName="!p-2"
            noPadding
          >
            <EquityChart runId={runId} embedded />
          </TerminalPanel>
        </section>

        <section>
          <FeatureImportance embedded />
        </section>
      </main>
    </div>
  );
}
