import { Link, useLocation } from "react-router-dom";

export default function Navbar() {
  const location = useLocation();

  const navItem = (path, label) => {
    const active = location.pathname === path;

    return (
      <Link
        to={path}
        className={`
          px-2.5 py-1 rounded-sm font-mono text-[11px] uppercase tracking-wider
          transition-colors duration-150
          ${
            active
              ? "bg-cyan-500/15 text-terminal-cyan border border-cyan-500/30"
              : "text-terminal-muted border border-transparent hover:text-terminal-text hover:border-terminal-border"
          }
        `}
      >
        {label}
      </Link>
    );
  };

  return (
    <header className="sticky top-0 z-50 border-b border-terminal-border bg-[#04070d]/95 backdrop-blur-md">
      <div className="max-w-[1920px] mx-auto flex items-center justify-between gap-4 px-3 sm:px-4 h-11">
        <div className="flex items-center gap-3 min-w-0">
          <div className="w-1 h-6 bg-gradient-to-b from-terminal-cyan to-terminal-blue shrink-0" />
          <div className="min-w-0">
            <p className="font-mono text-[10px] font-semibold tracking-[0.18em] text-terminal-cyan truncate">
              QUANT ML
            </p>
            <p className="text-[9px] text-terminal-muted uppercase tracking-widest hidden sm:block">
              Research Terminal
            </p>
          </div>
        </div>

        <nav className="flex items-center gap-1 flex-wrap justify-center">
          {navItem("/", "Desk")}
          {navItem("/rankings", "Rankings")}
          {navItem("/portfolio", "Portfolio")}
          {navItem("/backtests", "Backtest")}
          {navItem("/scanner", "Scanner")}
        </nav>

        <div className="flex items-center gap-2 shrink-0 border border-terminal-positive/25 bg-terminal-positive/5 px-2 py-0.5 rounded-sm">
          <span className="w-1.5 h-1.5 rounded-full bg-terminal-positive animate-pulse" />
          <span className="font-mono text-[10px] text-terminal-positive uppercase tracking-wider">
            Live
          </span>
        </div>
      </div>
    </header>
  );
}
