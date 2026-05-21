import {
  Area,
  ComposedChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

import TerminalPanel from "../ui/TerminalPanel";
import ForecastCard from "./ForecastCard";
import {
  getRechartsAxisProps,
  getRechartsGridProps,
  getRechartsTooltipStyle,
  TERMINAL_CHART_COLORS,
} from "../../utils/chartTheme";
import { formatPrice, shortDate } from "../../utils/analyticsHelpers";

export default function AiForecastSection({ forecast, symbol }) {
  const points = forecast?.points ?? [];
  const lastClose = forecast?.last_close ?? forecast?.next_day?.last_close;

  const chartData = [
    { label: "Now", date: "spot", price: lastClose, band: [lastClose, lastClose] },
    ...points.map((p) => ({
      label: shortDate(p.date),
      date: p.date,
      price: p.price,
      band: [p.lower, p.upper],
    })),
  ];

  return (
    <div className="space-y-3">
      <ForecastCard forecast={forecast} symbol={symbol} />

      <TerminalPanel
        title="Price Path"
        subtitle={`${forecast?.horizon_days ?? 5}D projection`}
        badge="PATH"
      >
        <div className="space-y-3">
          {points.length > 0 ? (
            <div
              className="border border-terminal-border/60 bg-terminal-surface/40 rounded-sm p-2 w-full"
              style={{ height: 160, minHeight: 160 }}
            >
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart
                  data={chartData}
                  margin={{ top: 8, right: 8, left: 0, bottom: 0 }}
                >
                  <CartesianGrid {...getRechartsGridProps()} />
                  <XAxis dataKey="label" {...getRechartsAxisProps()} />
                  <YAxis
                    domain={["auto", "auto"]}
                    {...getRechartsAxisProps()}
                    width={48}
                    tickFormatter={(v) => Number(v).toFixed(0)}
                  />
                  <Tooltip
                    {...getRechartsTooltipStyle()}
                    formatter={(v, name) => [
                      formatPrice(v),
                      name === "band" ? "Range" : "Forecast",
                    ]}
                  />
                  <Area
                    type="monotone"
                    dataKey="band"
                    fill="rgba(6,182,212,0.08)"
                    stroke="none"
                  />
                  <Line
                    type="monotone"
                    dataKey="price"
                    stroke={TERMINAL_CHART_COLORS.cyan}
                    strokeWidth={2}
                    dot={{ r: 2, fill: TERMINAL_CHART_COLORS.cyan }}
                  />
                </ComposedChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <p className="text-[10px] font-mono text-terminal-muted">
              Path chart unavailable.
            </p>
          )}

          <p className="text-[10px] text-terminal-muted leading-relaxed">
            Multi-day path extrapolated from next-day LSTM return. Bands are illustrative only.
          </p>
        </div>
      </TerminalPanel>
    </div>
  );
}
