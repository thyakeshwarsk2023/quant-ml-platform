import {
  ComposedChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

import ChartFrame from "./ChartFrame";
import {
  ANALYTICS_SERIES,
  getRechartsAxisProps,
  getRechartsGridProps,
  getRechartsTooltipStyle,
  TERMINAL_CHART_COLORS,
} from "../../utils/chartTheme";
import { shortDate } from "../../utils/analyticsHelpers";

export default function CandlestickChart({ bars = [], overlays = {} }) {
  if (!bars.length) {
    return (
      <ChartFrame title="Price" badge="OHLC">
        <div className="h-full flex items-center justify-center text-xs font-mono text-terminal-muted">
          No price data
        </div>
      </ChartFrame>
    );
  }

  const chartData = bars.map((b) => {
    const up = b.close >= b.open;
    return {
      ...b,
      label: shortDate(b.date),
      wick: [b.low, b.high],
      body: [Math.min(b.open, b.close), Math.max(b.open, b.close)],
      up,
    };
  });

  return (
    <ChartFrame title="Price" subtitle="Candlestick + overlays" badge="OHLC" height="h-[340px]">
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={chartData} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
          <CartesianGrid {...getRechartsGridProps()} />
          <XAxis dataKey="label" {...getRechartsAxisProps()} minTickGap={40} />
          <YAxis
            domain={["auto", "auto"]}
            {...getRechartsAxisProps()}
            width={52}
            tickFormatter={(v) => Number(v).toFixed(0)}
          />
          <Tooltip
            {...getRechartsTooltipStyle()}
            labelFormatter={(_, items) => items?.[0]?.payload?.date ?? ""}
            formatter={(_, name, item) => {
              const p = item?.payload;
              if (!p || name === "wick" || name === "body") {
                if (p && (name === "wick" || name === "body")) {
                  return null;
                }
              }
              if (p && name === "O") {
                return [
                  `O ${p.open} H ${p.high} L ${p.low} C ${p.close}`,
                  p.up ? "Up" : "Down",
                ];
              }
              return [Number(_).toFixed(2), name];
            }}
            content={({ active, payload, label }) => {
              if (!active || !payload?.length) {
                return null;
              }
              const p = payload[0]?.payload;
              if (!p) {
                return null;
              }
              return (
                <div
                  style={{
                    background: TERMINAL_CHART_COLORS.tooltipBg,
                    border: `1px solid ${TERMINAL_CHART_COLORS.tooltipBorder}`,
                    padding: 8,
                    fontSize: 11,
                    fontFamily: "monospace",
                  }}
                >
                  <p style={{ color: "#e2e8f0", margin: 0 }}>{p.date}</p>
                  <p style={{ color: p.up ? "#10b981" : "#ef4444", margin: "4px 0 0" }}>
                    O {p.open} · H {p.high} · L {p.low} · C {p.close}
                  </p>
                </div>
              );
            }}
          />
          <Bar dataKey="wick" barSize={1} isAnimationActive={false} radius={0}>
            {chartData.map((entry, i) => (
              <Cell
                key={`wick-${i}`}
                fill={entry.up ? "#10b981" : "#ef4444"}
              />
            ))}
          </Bar>
          <Bar dataKey="body" barSize={6} isAnimationActive={false} radius={1}>
            {chartData.map((entry, i) => (
              <Cell
                key={`body-${i}`}
                fill={entry.up ? "#10b981" : "#ef4444"}
              />
            ))}
          </Bar>
          {overlays.sma20 && (
            <Line
              type="monotone"
              dataKey={ANALYTICS_SERIES.sma20.key}
              name={ANALYTICS_SERIES.sma20.label}
              stroke={ANALYTICS_SERIES.sma20.color}
              dot={false}
              strokeWidth={1.5}
              connectNulls
            />
          )}
          {overlays.sma50 && (
            <Line
              type="monotone"
              dataKey={ANALYTICS_SERIES.sma50.key}
              name={ANALYTICS_SERIES.sma50.label}
              stroke={ANALYTICS_SERIES.sma50.color}
              dot={false}
              strokeWidth={1.5}
              connectNulls
            />
          )}
          {overlays.ema12 && (
            <Line
              type="monotone"
              dataKey={ANALYTICS_SERIES.ema12.key}
              name={ANALYTICS_SERIES.ema12.label}
              stroke={ANALYTICS_SERIES.ema12.color}
              dot={false}
              strokeWidth={1.5}
              connectNulls
            />
          )}
          {overlays.ema26 && (
            <Line
              type="monotone"
              dataKey={ANALYTICS_SERIES.ema26.key}
              name={ANALYTICS_SERIES.ema26.label}
              stroke={ANALYTICS_SERIES.ema26.color}
              dot={false}
              strokeWidth={1.5}
              connectNulls
            />
          )}
          {overlays.bollinger && (
            <>
              <Line
                type="monotone"
                dataKey="bb_upper"
                name="BB Upper"
                stroke={TERMINAL_CHART_COLORS.tick}
                strokeDasharray="4 3"
                dot={false}
                strokeWidth={1}
                connectNulls
              />
              <Line
                type="monotone"
                dataKey="bb_middle"
                name="BB Mid"
                stroke="rgba(100,116,139,0.5)"
                dot={false}
                strokeWidth={1}
                connectNulls
              />
              <Line
                type="monotone"
                dataKey="bb_lower"
                name="BB Lower"
                stroke={TERMINAL_CHART_COLORS.tick}
                strokeDasharray="4 3"
                dot={false}
                strokeWidth={1}
                connectNulls
              />
            </>
          )}
        </ComposedChart>
      </ResponsiveContainer>
    </ChartFrame>
  );
}
