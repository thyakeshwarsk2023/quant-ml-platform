import { useState } from "react";
import { runBacktest, isProductionApiConfigured } from "../api/api";
import { getApiErrorMessage } from "../utils/apiHelpers";
import TerminalPanel from "./ui/TerminalPanel";

export default function RunPanel({ setRunId, compact = false }) {
  const [symbol, setSymbol] = useState("AAPL");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastRunId, setLastRunId] = useState(null);

  const apiDisabled = import.meta.env.PROD && !isProductionApiConfigured();

  const handleRun = async () => {
    if (apiDisabled) {
      setError("Backtest requires VITE_API_BASE_URL in production.");
      return;
    }
    if (!symbol || symbol.trim().length < 1) {
      setError("Enter a valid symbol");
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const res = await runBacktest(symbol.trim().toUpperCase());
      const runId = res.data?.run_id;

      if (!runId) {
        throw new Error("Invalid response: missing run_id");
      }

      setLastRunId(runId);

      if (typeof setRunId === "function") {
        setRunId(runId);
      }
    } catch (err) {
      if (import.meta.env.DEV) {
        console.error("Run error:", err);
      }
      setError(getApiErrorMessage(err, "Failed to start backtest"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <TerminalPanel
      title="Backtest"
      subtitle="Single-symbol engine"
      badge="RUN"
      className="h-full"
    >
      <div className={`flex flex-col ${compact ? "gap-2" : "gap-3"}`}>
        <label className="kpi-label" htmlFor="backtest-symbol">
          Symbol
        </label>
        <div className="flex gap-2">
          <input
            id="backtest-symbol"
            value={symbol}
            onChange={(event) => setSymbol(event.target.value)}
            placeholder="AAPL"
            className="terminal-input flex-1 min-w-0 uppercase"
          />
          <button
            type="button"
            onClick={handleRun}
            disabled={loading || apiDisabled}
            className="terminal-btn shrink-0"
          >
            {loading ? "..." : "Run"}
          </button>
        </div>

        {error ? (
          <p className="text-terminal-negative text-[10px] font-mono">
            {error}
          </p>
        ) : null}

        {lastRunId && !error ? (
          <p className="text-terminal-muted text-[10px] font-mono">
            Run {lastRunId} - streaming equity
          </p>
        ) : null}
      </div>
    </TerminalPanel>
  );
}
