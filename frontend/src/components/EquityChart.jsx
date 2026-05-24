import { Line } from "react-chartjs-2";
import { useEffect, useRef, useState } from "react";
import { getEquity } from "../api/api";
import {
  formatChartLabel,
  getApiErrorMessage,
  parseEquityResponse,
} from "../utils/apiHelpers";
import {
  buildEquityGradient,
  getEquityChartOptions,
  TERMINAL_CHART_COLORS,
} from "../utils/chartTheme";
import { formatReturn } from "../utils/formatters";

import {
  Chart as ChartJS,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Filler,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Filler,
  Tooltip,
  Legend
);

const MAX_POLLS = 20;

function ChartState({ children, embedded }) {
  const height = embedded ? "h-[260px]" : "h-[420px]";
  return (
    <div
      className={`${height} flex items-center justify-center text-xs font-mono text-terminal-muted`}
    >
      {children}
    </div>
  );
}

export default function EquityChart({ runId, embedded = false }) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const pollCountRef = useRef(0);
  const stableCountRef = useRef(0);
  const lastLengthRef = useRef(0);
  const chartRef = useRef(null);

  useEffect(() => {
    if (!runId) {
      return;
    }

    let isMounted = true;
    const intervalRef = { id: null };

    pollCountRef.current = 0;
    stableCountRef.current = 0;
    lastLengthRef.current = 0;

    queueMicrotask(() => {
      if (!isMounted) {
        return;
      }
      setLoading(true);
      setError(null);
      setData([]);
    });

    const fetchData = async () => {
      try {
        const res = await getEquity(runId);

        if (!isMounted) {
          return;
        }

        const points = parseEquityResponse(res.data);
        setData(points);
        setError(null);

        if (points.length === lastLengthRef.current && points.length > 0) {
          stableCountRef.current += 1;
        } else {
          stableCountRef.current = 0;
        }

        lastLengthRef.current = points.length;
        pollCountRef.current += 1;

        if (
          stableCountRef.current >= 3 ||
          pollCountRef.current >= MAX_POLLS
        ) {
          if (intervalRef.id) {
            clearInterval(intervalRef.id);
          }
        }
      } catch (err) {
        if (import.meta.env.DEV) {
          console.error("Equity API error:", err);
        }

        if (intervalRef.id) {
          clearInterval(intervalRef.id);
          intervalRef.id = null;
        }

        if (!isMounted) {
          return;
        }

        setError(
          getApiErrorMessage(err, "Failed to load equity curve")
        );
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    fetchData();
    intervalRef.id = setInterval(fetchData, 4000);

    return () => {
      isMounted = false;
      if (intervalRef.id) {
        clearInterval(intervalRef.id);
      }
    };
  }, [runId]);

  if (!runId) {
    return (
      <ChartState embedded={embedded}>
        Run a backtest to stream equity
      </ChartState>
    );
  }

  if (loading && data.length === 0) {
    return (
      <ChartState embedded={embedded}>
        <span className="text-terminal-cyan animate-pulse">
          Loading curve…
        </span>
      </ChartState>
    );
  }

  if (error && data.length === 0) {
    return (
      <ChartState embedded={embedded}>
        <span className="text-terminal-negative">{error}</span>
      </ChartState>
    );
  }

  if (!data.length) {
    return (
      <ChartState embedded={embedded}>
        Waiting for equity ticks…
      </ChartState>
    );
  }

  const startEquity = data[0]?.equity || 0;
  const endEquity = data[data.length - 1]?.equity || 0;
  const pnlPct = startEquity
    ? ((endEquity - startEquity) / startEquity) * 100
    : 0;
  const pnlFmt = formatReturn(pnlPct);

  const chartData = {
    labels: data.map((point) => formatChartLabel(point.timestamp)),
    datasets: [
      {
        label: "Equity",
        data: data.map((point) => point.equity),
        borderColor: TERMINAL_CHART_COLORS.positive,
        backgroundColor: (context) => {
          const chart = context.chart;
          return buildEquityGradient(chart);
        },
        tension: 0.4,
        fill: true,
        pointRadius: 0,
        pointHoverRadius: 3,
        pointHoverBackgroundColor: TERMINAL_CHART_COLORS.cyan,
        borderWidth: 2,
      },
    ],
  };

  const chartHeight = embedded ? "h-[220px]" : "h-[350px]";

  return (
    <div className={`w-full ${embedded ? "px-2 pb-2" : "p-4"}`}>
      {!embedded && (
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-sm font-semibold text-terminal-positive tracking-tight">
              Equity Curve
            </h2>
            <p className="text-[11px] text-terminal-muted mt-0.5">
              Portfolio mark-to-market
            </p>
          </div>
          <div className="text-right">
            <p className="text-[10px] font-mono uppercase tracking-wider text-terminal-muted">
              Net Return
            </p>
            <p className={`font-mono text-lg font-semibold ${pnlFmt.className}`}>
              {pnlFmt.text}
            </p>
          </div>
        </div>
      )}

      {embedded && (
        <div className="flex justify-end mb-2 pr-1">
          <span className={`font-mono text-sm font-semibold ${pnlFmt.className}`}>
            {pnlFmt.text}
          </span>
        </div>
      )}

      {error && (
        <p className="text-[10px] font-mono text-terminal-negative mb-2 px-1">
          {error}
        </p>
      )}

      <div className={`border border-terminal-border/60 bg-terminal-surface/40 rounded-sm p-3 ${chartHeight}`}>
        <Line
          ref={chartRef}
          data={chartData}
          options={getEquityChartOptions()}
        />
      </div>
    </div>
  );
}
