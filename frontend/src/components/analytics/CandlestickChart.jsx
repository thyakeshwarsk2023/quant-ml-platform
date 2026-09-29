import {
  ComposedChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";

import ChartFrame from "./ChartFrame";
import SafeResponsiveContainer from "../ui/SafeResponsiveContainer";
import {
  ANALYTICS_SERIES,
  getRechartsAxisProps,
  getRechartsGridProps,
  TERMINAL_CHART_COLORS,
} from "../../utils/chartTheme";
import { shortDate } from "../../utils/analyticsHelpers";

// Custom concentric Candlestick shape rendering centered wick and body on a single bar slot
const CandlestickShape = (props) => {
  const { x, y, width, height, payload } = props;
  if (!payload || payload.high == null || payload.low == null) return null;

  const isUp = payload.close >= payload.open;
  const color = isUp ? "#10b981" : "#ef4444";

  const priceRange = payload.high - payload.low;
  const pixelPerPrice = priceRange > 0 ? height / priceRange : 0;

  const centerX = x + width / 2;
  const bodyTopPrice = Math.max(payload.open, payload.close);
  const bodyBottomPrice = Math.min(payload.open, payload.close);

  const bodyY = pixelPerPrice > 0 ? y + (payload.high - bodyTopPrice) * pixelPerPrice : y;
  const rawBodyHeight = pixelPerPrice > 0 ? (bodyTopPrice - bodyBottomPrice) * pixelPerPrice : 2;
  const bodyHeight = Math.max(rawBodyHeight, 2); // Ensure Doji candles remain visible

  const candleWidth = Math.max(Math.min(width * 0.75, 12), 3);
  const bodyX = centerX - candleWidth / 2;

  return (
    <g>
      {/* Wick line */}
      <line
        x1={centerX}
        y1={y}
        x2={centerX}
        y2={y + height}
        stroke={color}
        strokeWidth={1.2}
      />
      {/* Candle body */}
      <rect
        x={bodyX}
        y={bodyY}
        width={candleWidth}
        height={bodyHeight}
        fill={color}
        stroke={color}
        strokeWidth={0.5}
        rx={0.5}
      />
    </g>
  );
};

export default function CandlestickChart({ bars = [], overlays = {} }) {
  if (!bars.length) {
    return (
      <ChartFrame title="Price" badge="OHLC" chartHeightPx={300}>
        <div className="h-full flex items-center justify-center text-xs font-mono text-terminal-muted">
          No price data
        </div>
      </ChartFrame>
    );
  }

  // Calculate explicit Y-domain from price bars and active overlays
  const allValues = [];
  bars.forEach((b) => {
    const sma20 = b.sma_20 ?? b.sma20;
    const sma50 = b.sma_50 ?? b.sma50;
    const ema12 = b.ema_12 ?? b.ema12;
    const ema26 = b.ema_26 ?? b.ema26;
    if (b.low != null && Number.isFinite(b.low)) allValues.push(b.low);
    if (b.high != null && Number.isFinite(b.high)) allValues.push(b.high);
    if (overlays.sma20 && sma20 != null && Number.isFinite(sma20)) allValues.push(sma20);
    if (overlays.sma50 && sma50 != null && Number.isFinite(sma50)) allValues.push(sma50);
    if (overlays.ema12 && ema12 != null && Number.isFinite(ema12)) allValues.push(ema12);
    if (overlays.ema26 && ema26 != null && Number.isFinite(ema26)) allValues.push(ema26);
    if (overlays.bollinger) {
      if (b.bb_upper != null && Number.isFinite(b.bb_upper)) allValues.push(b.bb_upper);
      if (b.bb_lower != null && Number.isFinite(b.bb_lower)) allValues.push(b.bb_lower);
    }
  });

  const minVal = allValues.length ? Math.min(...allValues) : 0;
  const maxVal = allValues.length ? Math.max(...allValues) : 100;
  const range = maxVal - minVal;
  const padding = range > 0 ? range * 0.05 : maxVal * 0.05;
  const yDomain = [
    Math.max(0, Math.floor(minVal - padding)),
    Math.ceil(maxVal + padding),
  ];

  const chartData = bars.map((b) => {
    const up = b.close >= b.open;
    const sma20 = b.sma_20 ?? b.sma20;
    const sma50 = b.sma_50 ?? b.sma50;
    const ema12 = b.ema_12 ?? b.ema12;
    const ema26 = b.ema_26 ?? b.ema26;
    return {
      ...b,
      sma_20: sma20,
      sma20,
      sma_50: sma50,
      sma50,
      ema_12: ema12,
      ema12,
      ema_26: ema26,
      ema26,
      label: shortDate(b.date),
      wick: [b.low, b.high],
      up,
    };
  });

  return (
    <ChartFrame
      title="Price"
      subtitle="Candlestick + overlays"
      badge="OHLC"
      chartHeightPx={300}
    >
      <SafeResponsiveContainer minHeight={260}>
        <ComposedChart data={chartData} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
          <CartesianGrid {...getRechartsGridProps()} />
          <XAxis dataKey="label" {...getRechartsAxisProps()} minTickGap={40} />
          <YAxis
            domain={yDomain}
            {...getRechartsAxisProps()}
            width={52}
            tickFormatter={(v) => Number(v).toFixed(0)}
          />
          <Tooltip
            content={({ active, payload }) => {
              if (!active || !payload?.length) {
                return null;
              }
              const p = payload[0]?.payload;
              if (!p) {
                return null;
              }
              const isUp = p.close >= p.open;
              const change = p.close - p.open;
              const changePct = p.open ? (change / p.open) * 100 : 0;
              const sign = change >= 0 ? "+" : "";

              return (
                <div
                  className="rounded border p-2.5 shadow-xl font-mono text-xs backdrop-blur-md"
                  style={{
                    background: TERMINAL_CHART_COLORS.tooltipBg,
                    borderColor: TERMINAL_CHART_COLORS.tooltipBorder,
                    minWidth: 175,
                  }}
                >
                  <div className="flex items-center justify-between pb-1.5 mb-1.5 border-b border-terminal-border/50">
                    <span className="text-terminal-text font-semibold">{p.date}</span>
                    <span className={`text-[11px] font-bold ${isUp ? "text-terminal-positive" : "text-terminal-negative"}`}>
                      {sign}{change.toFixed(2)} ({sign}{changePct.toFixed(2)}%)
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-x-3 gap-y-1 text-[11px]">
                    <div>
                      <span className="text-terminal-muted">Open: </span>
                      <span className="text-terminal-text font-medium">{Number(p.open).toFixed(2)}</span>
                    </div>
                    <div>
                      <span className="text-terminal-muted">High: </span>
                      <span className="text-terminal-text font-medium">{Number(p.high).toFixed(2)}</span>
                    </div>
                    <div>
                      <span className="text-terminal-muted">Low: </span>
                      <span className="text-terminal-text font-medium">{Number(p.low).toFixed(2)}</span>
                    </div>
                    <div>
                      <span className="text-terminal-muted">Close: </span>
                      <span className={`font-semibold ${isUp ? "text-terminal-positive" : "text-terminal-negative"}`}>
                        {Number(p.close).toFixed(2)}
                      </span>
                    </div>
                    {p.volume != null && (
                      <div className="col-span-2 text-[10px] text-terminal-muted pt-0.5">
                        <span>Vol: </span>
                        <span className="text-terminal-text font-mono">{Number(p.volume).toLocaleString()}</span>
                      </div>
                    )}
                  </div>

                  {(overlays.sma20 || overlays.sma50 || overlays.ema12 || overlays.ema26 || overlays.bollinger) && (
                    <div className="mt-2 pt-1.5 border-t border-terminal-border/40 space-y-0.5 text-[10px]">
                      {overlays.sma20 && (p.sma_20 != null || p.sma20 != null) && (
                        <div className="flex justify-between">
                          <span style={{ color: ANALYTICS_SERIES.sma20.color }}>SMA 20:</span>
                          <span className="text-terminal-text">{Number(p.sma_20 ?? p.sma20).toFixed(2)}</span>
                        </div>
                      )}
                      {overlays.sma50 && (p.sma_50 != null || p.sma50 != null) && (
                        <div className="flex justify-between">
                          <span style={{ color: ANALYTICS_SERIES.sma50.color }}>SMA 50:</span>
                          <span className="text-terminal-text">{Number(p.sma_50 ?? p.sma50).toFixed(2)}</span>
                        </div>
                      )}
                      {overlays.ema12 && (p.ema_12 != null || p.ema12 != null) && (
                        <div className="flex justify-between">
                          <span style={{ color: ANALYTICS_SERIES.ema12.color }}>EMA 12:</span>
                          <span className="text-terminal-text">{Number(p.ema_12 ?? p.ema12).toFixed(2)}</span>
                        </div>
                      )}
                      {overlays.ema26 && (p.ema_26 != null || p.ema26 != null) && (
                        <div className="flex justify-between">
                          <span style={{ color: ANALYTICS_SERIES.ema26.color }}>EMA 26:</span>
                          <span className="text-terminal-text">{Number(p.ema_26 ?? p.ema26).toFixed(2)}</span>
                        </div>
                      )}
                      {overlays.bollinger && p.bb_upper != null && (
                        <div className="flex justify-between text-terminal-muted">
                          <span>BB [U/M/L]:</span>
                          <span className="text-terminal-text">
                            {Number(p.bb_upper).toFixed(1)} / {Number(p.bb_middle).toFixed(1)} / {Number(p.bb_lower).toFixed(1)}
                          </span>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            }}
          />
          {/* Single Bar slot using custom CandlestickShape: zero grouping offset */}
          <Bar
            dataKey="wick"
            shape={<CandlestickShape />}
            isAnimationActive={false}
          />
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
      </SafeResponsiveContainer>
    </ChartFrame>
  );
}
