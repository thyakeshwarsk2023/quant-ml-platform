import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
} from "recharts";
import TerminalPanel from "./ui/TerminalPanel";
import SafeResponsiveContainer from "./ui/SafeResponsiveContainer";
import { FEATURE_CHART_THEME } from "../utils/chartTheme";

const data = [
  { feature: "Momentum", value: 3228 },
  { feature: "Volume", value: 3212 },
  { feature: "Volatility", value: 3152 },
  { feature: "BB Width", value: 3095 },
  { feature: "Trend", value: 3022 },
];

const maxVal = Math.max(...data.map((d) => d.value));

export default function FeatureImportance({ embedded = false }) {
  const h = embedded ? 220 : 320;

  return (
    <TerminalPanel
      title="Feature Importance"
      subtitle="Model attribution · static demo"
      badge="ML"
      className={embedded ? "" : "min-h-[360px]"}
      bodyClassName="!pb-2"
    >
      <div className="w-full" style={{ height: h, minHeight: h }}>
        <SafeResponsiveContainer minHeight={h}>
          <BarChart
            data={data}
            layout="vertical"
            margin={{ top: 4, right: 12, left: 4, bottom: 4 }}
          >
            <XAxis
              type="number"
              domain={[0, maxVal]}
              stroke="transparent"
              tick={{ fill: FEATURE_CHART_THEME.tick, fontSize: 10 }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              dataKey="feature"
              type="category"
              width={88}
              stroke="transparent"
              tick={{
                fill: "#94a3b8",
                fontSize: 10,
                fontFamily: "'IBM Plex Mono', monospace",
              }}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip
              cursor={{ fill: "rgba(34, 211, 238, 0.06)" }}
              contentStyle={{
                background: FEATURE_CHART_THEME.tooltip.background,
                border: `1px solid ${FEATURE_CHART_THEME.tooltip.border}`,
                borderRadius: 2,
                fontSize: 11,
                fontFamily: "'IBM Plex Mono', monospace",
              }}
              labelStyle={{ color: "#22d3ee" }}
              formatter={(value) => [value, "Importance"]}
            />
            <defs>
              {data.map((_, index) => (
                <linearGradient
                  key={index}
                  id={`featureGrad-${index}`}
                  x1="0"
                  y1="0"
                  x2="1"
                  y2="0"
                >
                  <stop offset="0%" stopColor="#0891b2" />
                  <stop offset="100%" stopColor="#22d3ee" />
                </linearGradient>
              ))}
            </defs>
            <Bar dataKey="value" radius={[0, 2, 2, 0]} barSize={14}>
              {data.map((_, index) => (
                <Cell key={index} fill={`url(#featureGrad-${index})`} />
              ))}
            </Bar>
          </BarChart>
        </SafeResponsiveContainer>
      </div>
    </TerminalPanel>
  );
}
