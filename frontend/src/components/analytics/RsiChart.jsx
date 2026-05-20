import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";

import ChartFrame from "./ChartFrame";
import {
  getRechartsAxisProps,
  getRechartsGridProps,
  getRechartsTooltipStyle,
  TERMINAL_CHART_COLORS,
} from "../../utils/chartTheme";
import { shortDate } from "../../utils/analyticsHelpers";

export default function RsiChart({ bars = [] }) {
  const chartData = bars
    .filter((b) => b.rsi != null)
    .map((b) => ({ label: shortDate(b.date), date: b.date, rsi: b.rsi }));

  if (!chartData.length) {
    return (
      <ChartFrame title="RSI" badge="14">
        <div className="h-full flex items-center justify-center text-xs font-mono text-terminal-muted">
          RSI unavailable
        </div>
      </ChartFrame>
    );
  }

  return (
    <ChartFrame title="RSI" subtitle="Relative Strength Index" badge="14" height="h-[160px]">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
          <CartesianGrid {...getRechartsGridProps()} />
          <XAxis dataKey="label" {...getRechartsAxisProps()} minTickGap={50} />
          <YAxis domain={[0, 100]} {...getRechartsAxisProps()} width={36} />
          <ReferenceLine y={70} stroke={TERMINAL_CHART_COLORS.negative} strokeDasharray="3 3" />
          <ReferenceLine y={30} stroke={TERMINAL_CHART_COLORS.positive} strokeDasharray="3 3" />
          <Tooltip
            {...getRechartsTooltipStyle()}
            formatter={(v) => [Number(v).toFixed(1), "RSI"]}
          />
          <Line
            type="monotone"
            dataKey="rsi"
            stroke={TERMINAL_CHART_COLORS.cyan}
            dot={false}
            strokeWidth={1.5}
          />
        </LineChart>
      </ResponsiveContainer>
    </ChartFrame>
  );
}
