export default function ChartFrame({
  title,
  subtitle,
  badge,
  /** Explicit pixel height for Recharts (avoids width/height -1 in production). */
  chartHeightPx = 280,
  children,
  footer,
}) {
  return (
    <div className="border border-terminal-border/60 bg-terminal-surface/40 rounded-sm overflow-hidden">
      {(title || badge) && (
        <div className="flex items-center justify-between gap-2 px-3 py-2 border-b border-terminal-border/50 bg-black/20">
          <div className="min-w-0">
            {title && (
              <h3 className="font-mono text-[10px] uppercase tracking-wider text-terminal-cyan">
                {title}
              </h3>
            )}
            {subtitle && (
              <p className="text-[10px] text-terminal-muted truncate">{subtitle}</p>
            )}
          </div>
          {badge && (
            <span className="shrink-0 font-mono text-[9px] uppercase tracking-wider text-terminal-muted px-1.5 py-0.5 border border-terminal-border/60 rounded-sm">
              {badge}
            </span>
          )}
        </div>
      )}
      <div
        className="w-full px-2 py-2"
        style={{ height: chartHeightPx, minHeight: 200, minWidth: 0 }}
      >
        {children}
      </div>
      {footer && (
        <div className="px-3 py-1.5 border-t border-terminal-border/40 text-[10px] font-mono text-terminal-muted">
          {footer}
        </div>
      )}
    </div>
  );
}
