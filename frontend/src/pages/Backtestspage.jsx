import { useState } from "react";

import Sidebar from "../components/Sidebar";
import RunPanel from "../components/RunPanel";
import EquityChart from "../components/EquityChart";

export default function BacktestsPage() {
  const [runId, setRunId] = useState(null);

  return (
    <div className="terminal-shell terminal-grid-bg min-h-screen">
      <Sidebar />

      <main className="ml-56 px-4 py-4 max-w-[calc(100vw-14rem)] space-y-4">
        <header className="border-b border-terminal-border pb-3 mb-4">
          <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-terminal-muted">
            Engine
          </p>
          <h1 className="text-lg font-semibold text-terminal-text tracking-tight">
            Backtest Engine
          </h1>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div className="min-h-[340px]">
            <RunPanel setRunId={setRunId} />
          </div>

          <div className="min-h-[340px]">
            <EquityChart runId={runId} />
          </div>
        </div>
      </main>
    </div>
  );
}
