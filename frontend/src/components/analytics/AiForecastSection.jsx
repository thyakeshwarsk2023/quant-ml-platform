import {
  ComposedChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";

import TerminalPanel from "../ui/TerminalPanel";
import SafeResponsiveContainer from "../ui/SafeResponsiveContainer";
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
    ...(lastClose != null
      ? [
          {
            label: "Spot",
            date: "Now",
            price: Number(lastClose),
            lower: Number(lastClose),
            upper: Number(lastClose),
          },
        ]
      : []),
    ...points.map((p) => ({
      label: shortDate(p.date),
      date: p.date,
      price: Number(p.price),
      lower: Number(p.lower),
      upper: Number(p.upper),
    })),
  ];

  // Calculate explicit YAxis bounds spanning price, lower, and upper
  const allValues = chartData.flatMap((d) =>
    [d.price, d.lower, d.upper].filter((v) => v != null && Number.isFinite(v))
  );
  const minVal = allValues.length ? Math.min(...allValues) : 0;
  const maxVal = allValues.length ? Math.max(...allValues) : 100;
  const pad = (maxVal - minVal) * 0.08 || maxVal * 0.04;
  const yDomain = [
    Math.max(0, Math.floor(minVal - pad)),
    Math.ceil(maxVal + pad),
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
              <SafeResponsiveContainer minHeight={140}>
                <ComposedChart
                  data={chartData}
                  margin={{ top: 8, right: 8, left: 0, bottom: 0 }}
                >
                  <CartesianGrid {...getRechartsGridProps()} />
                  <XAxis dataKey="label" {...getRechartsAxisProps()} />
                  <YAxis
                    domain={yDomain}
                    {...getRechartsAxisProps()}
                    width={48}
                    tickFormatter={(v) => Number(v).toFixed(0)}
                  />
                  <Tooltip
                    {...getRechartsTooltipStyle()}
                    formatter={(v, name) => [
                      formatPrice(v),
                      name === "price"
                        ? "Forecast"
                        : name === "upper"
                        ? "Upper Band"
                        : name === "lower"
                        ? "Lower Band"
                        : name,
                    ]}
                  />
                  {/* Upper and Lower Confidence Bounds */}
                  <Line
                    type="monotone"
                    dataKey="upper"
                    name="Upper Band"
                    stroke="rgba(34, 211, 238, 0.45)"
                    strokeDasharray="3 3"
                    dot={false}
                    strokeWidth={1}
                    isAnimationActive={false}
                  />
                  <Line
                    type="monotone"
                    dataKey="lower"
                    name="Lower Band"
                    stroke="rgba(34, 211, 238, 0.45)"
                    strokeDasharray="3 3"
                    dot={false}
                    strokeWidth={1}
                    isAnimationActive={false}
                  />
                  {/* Forecast trajectory */}
                  <Line
                    type="monotone"
                    dataKey="price"
                    name="Forecast"
                    stroke={TERMINAL_CHART_COLORS.cyan}
                    strokeWidth={2}
                    dot={{ r: 2.5, fill: TERMINAL_CHART_COLORS.cyan }}
                    isAnimationActive={false}
                  />
                </ComposedChart>
              </SafeResponsiveContainer>
            </div>
          ) : (
            <p className="text-[10px] font-mono text-terminal-muted">
              Path chart unavailable.
            </p>
          )}

          <p className="text-[10px] text-terminal-muted leading-relaxed">
            Multi-day path projected with LSTM momentum. Dashed bounds indicate ±1σ volatility corridor.
          </p>
        </div>
      </TerminalPanel>
    </div>
  );
}
