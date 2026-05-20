import { Line } from "react-chartjs-2";

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

export default function MultiStrategyChart({ strategies }) {
  if (!strategies || strategies.length === 0) {
    return <div className="text-terminal-muted text-xs font-mono">No strategy data</div>;
  }

  if (!strategies[0] || !strategies[0].data || strategies[0].data.length === 0) {
    return <div className="text-terminal-muted text-xs font-mono">Invalid strategy data</div>;
  }

  const chartData = {
    labels: strategies[0].data.map(d =>
      d.timestamp ? new Date(d.timestamp).toLocaleDateString() : ""
    ),
    datasets: strategies.map((s, i) => ({
      label: s.name || `Strategy ${i + 1}`,
      data: s.data ? s.data.map(d => d.equity) : [],
      borderColor: ["#22c55e", "#3b82f6", "#f59e0b"][i % 3],
      tension: 0.4
    }))
  };

  return (
    <div className="bg-terminal-surface/60 border border-terminal-border/60 p-4 rounded-sm">
      <h2 className="text-terminal-cyan mb-3 font-semibold text-sm tracking-tight">Strategy Comparison</h2>
      <div className="border border-terminal-border/40 bg-terminal-surface/40 rounded-sm p-3">
        <Line data={chartData} />
      </div>
    </div>
  );
}