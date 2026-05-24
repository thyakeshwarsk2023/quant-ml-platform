import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Cell,
} from "recharts";

import ChartFrame from "./ChartFrame";
import SafeResponsiveContainer from "../ui/SafeResponsiveContainer";
import {
  getRechartsAxisProps,
  getRechartsGridProps,
  getRechartsTooltipStyle,
} from "../../utils/chartTheme";
import { formatVolume, shortDate } from "../../utils/analyticsHelpers";

export default function VolumeChart({ bars = [] }) {
  if (!bars.length) {
    return (
      <ChartFrame title="Volume" badge="VOL" chartHeightPx={120}>
        <div className="h-full flex items-center justify-center text-xs font-mono text-terminal-muted">
          No volume data
        </div>
      </ChartFrame>
    );
  }

  const chartData = bars.map((b) => ({
    label: shortDate(b.date),
    date: b.date,
    volume: b.volume,
    up: b.close >= b.open,
  }));

  return (
    <ChartFrame title="Volume" badge="VOL" chartHeightPx={120}>
      <SafeResponsiveContainer minHeight={100}>
        <BarChart data={chartData} margin={{ top: 4, right: 8, left: 0, bottom: 0 }}>
          <CartesianGrid {...getRechartsGridProps()} />
          <XAxis dataKey="label" {...getRechartsAxisProps()} minTickGap={50} />
          <YAxis
            {...getRechartsAxisProps()}
            width={44}
            tickFormatter={formatVolume}
          />
          <Tooltip
            {...getRechartsTooltipStyle()}
            formatter={(v) => [formatVolume(v), "Volume"]}
            labelFormatter={(_, items) => items?.[0]?.payload?.date ?? ""}
          />
          <Bar dataKey="volume" isAnimationActive={false}>
            {chartData.map((entry, i) => (
              <Cell
                key={`vol-${i}`}
                fill={entry.up ? "rgba(16,185,129,0.55)" : "rgba(239,68,68,0.55)"}
              />
            ))}
          </Bar>
        </BarChart>
      </SafeResponsiveContainer>
    </ChartFrame>
  );
}
