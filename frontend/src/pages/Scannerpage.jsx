import Sidebar from "../components/Sidebar";

import ScanPanel from "../components/ScanPanel";


export default function ScannerPage() {

  return (

    <div className="terminal-shell terminal-grid-bg min-h-screen">

      <Sidebar />

      <main className="ml-56 px-4 py-4 max-w-[calc(100vw-14rem)] space-y-4">
        <header className="border-b border-terminal-border pb-3 mb-4">
          <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-terminal-muted">
            Scanner
          </p>
          <h1 className="text-lg font-semibold text-terminal-text tracking-tight">
            Market Scanner
          </h1>
        </header>

        <ScanPanel />
      </main>

    </div>
  );
}