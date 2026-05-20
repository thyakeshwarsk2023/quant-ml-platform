import { Link, useLocation } from "react-router-dom";

const navItems = [
  { path: "/", label: "Dashboard", icon: "📊" },
  { path: "/analytics", label: "Analytics", icon: "📉" },
  { path: "/rankings", label: "Rankings", icon: "📈" },
  { path: "/portfolio", label: "Portfolio", icon: "💼" },
  { path: "/backtests", label: "Backtests", icon: "⚡" },
  { path: "/scanner", label: "Scanner", icon: "🔍" },
];

export default function Sidebar() {
  const location = useLocation();

  return (
    <aside className="fixed left-0 top-0 h-screen w-56 bg-[#0f141f] border-r border-[#1e293b] flex flex-col z-50">
      {/* Logo Section */}
      <div className="p-4 border-b border-[#1e293b]">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded bg-gradient-to-br from-[#06b6d4] to-[#3b82f6] flex items-center justify-center">
            <span className="text-[#0a0e17] font-bold text-sm">Q</span>
          </div>
          <div>
            <h1 className="text-sm font-semibold text-[#e2e8f0] tracking-tight">
              QUANT ML
            </h1>
            <p className="text-[10px] text-[#64748b] uppercase tracking-wider">
              Research Terminal
            </p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-3 space-y-1">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 px-3 py-2 rounded-sm text-xs font-medium transition-all duration-150 ${
                isActive
                  ? "bg-[#06b6d4]/10 text-[#06b6d4] border border-[#06b6d4]/30"
                  : "text-[#64748b] hover:text-[#e2e8f0] hover:bg-[#1e293b]/50 border border-transparent"
              }`}
            >
              <span className="text-sm">{item.icon}</span>
              <span className="tracking-wide">{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* Status Footer */}
      <div className="p-3 border-t border-[#1e293b]">
        <div className="flex items-center gap-2 px-3 py-2 rounded-sm bg-[#10b981]/5 border border-[#10b981]/20">
          <span className="w-2 h-2 rounded-full bg-[#10b981] animate-pulse" />
          <span className="text-[10px] font-mono text-[#10b981] uppercase tracking-wider">
            System Online
          </span>
        </div>
      </div>
    </aside>
  );
}
