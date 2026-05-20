export function PanelHeader({ title, subtitle, action, badge }) {
  return (
    <div className="terminal-panel-header">
      <div className="min-w-0">
        <div className="flex items-center gap-2">
          <h2 className="terminal-panel-title">{title}</h2>
          {badge && (
            <span className="text-[10px] font-mono uppercase tracking-wider text-terminal-muted px-2 py-0.5 border border-terminal-border/60 bg-terminal-surface/50 rounded-sm">
              {badge}
            </span>
          )}
        </div>
        {subtitle && (
          <p className="text-[11px] text-terminal-muted mt-0.5 truncate">
            {subtitle}
          </p>
        )}
      </div>
      {action && <div className="shrink-0">{action}</div>}
    </div>
  );
}

export default function TerminalPanel({
  title,
  subtitle,
  badge,
  action,
  children,
  className = "",
  bodyClassName = "",
  noPadding = false,
}) {
  return (
    <section className={`terminal-panel flex flex-col h-full ${className}`}>
      {title && (
        <PanelHeader
          title={title}
          subtitle={subtitle}
          badge={badge}
          action={action}
        />
      )}
      <div
        className={
          noPadding
            ? `flex-1 min-h-0 ${bodyClassName}`
            : `terminal-panel-body flex-1 min-h-0 ${bodyClassName}`
        }
      >
        {children}
      </div>
    </section>
  );
}
