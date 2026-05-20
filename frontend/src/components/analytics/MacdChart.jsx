import {
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

import ChartFrame from "./ChartFrame";
import {
  getRechartsAxisProps,
  getRechartsGridProps,
  getRechartsTooltipStyle,
  TERMINAL_CHART_COLORS,
} from "../../utils/chartTheme";
import { shortDate } from "../../utils/analyticsHelpers";

export default function MacdChart({ bars = [] }) {
  const chartData = bars
    .filter((b) => b.macd != null)
    .map((b) => ({
      label: shortDate(b.date),
      date: b.date,
      macd: b.macd,
      macd_signal: b.macd_signal,
      macd_hist: b.macd_hist,
    }));

  if (!chartData.length) {
    return (
      <ChartFrame title="MACD" badge="12/26/9">
        <div className="h-full flex items-center justify-center text-xs font-mono text-terminal-muted">
          MACD unavailable
        </div>
      </ChartFrame>
    );
  }

  return (
    <ChartFrame title="MACD" subtitle="Line + histogram" badge="12/26/9" height="h-[160px]">
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={chartData} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
          <CartesianGrid {...getRechartsGridProps()} />
          <XAxis dataKey="label" {...getRechartsAxisProps()} minTickGap={50} />
          <YAxis {...getRechartsAxisProps()} width={44} />
          <Tooltip {...getRechartsTooltipStyle()} />
          <Bar dataKey="macd_hist" isAnimationActive={false}>
            {chartData.map((entry, i) => (
              <Cell
                key={`macd-h-${i}`}
                fill={
                  entry.macd_hist >= 0
                    ? "rgba(16,185,129,0.5)"
                    : "rgba(239,68,68,0.5)"
                }
              />
            ))}
          </Bar>
          <Line
            type="monotone"
            dataKey="macd"
            name="MACD"
            stroke={TERMINAL_CHART_COLORS.cyan}
            dot={false}
            strokeWidth={1.5}
          />
          <Line
            type="monotone"
            dataKey="macd_signal"
            name="Signal"
            stroke="#f59e0b"
            dot={false}
            strokeWidth={1.5}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </ChartFrame>
  );
}
