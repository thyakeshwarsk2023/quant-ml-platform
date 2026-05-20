import { useEffect, useState } from "react";

import Sidebar from "../components/Sidebar";
import PortfolioSummary from "../components/PortfolioSummary";
import PortfolioAnalytics from "../components/portfolio/PortfolioAnalytics";
import { getPortfolio } from "../api/api";
import {
  getApiErrorMessage,
  parsePortfolioResponse,
} from "../utils/apiHelpers";

export default function PortfolioPage() {
  const [portfolio, setPortfolio] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isMounted = true;

    async function loadPortfolio() {
      try {
        const res = await getPortfolio(10);

        if (!isMounted) {
          return;
        }

        setPortfolio(parsePortfolioResponse(res.data));
        setError(null);
      } catch (err) {
        console.error(err);

        if (!isMounted) {
          return;
        }

        setError(getApiErrorMessage(err, "Failed to load portfolio"));
        setPortfolio(null);
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    loadPortfolio();

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
            Book
          </p>
          <h1 className="text-lg font-semibold text-terminal-text tracking-tight">
            Portfolio Analytics
          </h1>
        </header>

        <div className="grid grid-cols-1 xl:grid-cols-[1fr_360px] gap-4">
          <PortfolioSummary
            portfolio={portfolio}
            loading={loading}
            error={error}
          />
          {!loading && !error && portfolio?.status !== "error" && (
            <PortfolioAnalytics
              analytics={portfolio?.analytics}
              portfolioReturn={portfolio?.portfolio_return}
            />
          )}
        </div>
      </main>
    </div>
  );
}
