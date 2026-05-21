import { useState } from "react";

import Sidebar from "../components/Sidebar";
import CandlestickChart from "../components/analytics/CandlestickChart";
import VolumeChart from "../components/analytics/VolumeChart";
import RsiChart from "../components/analytics/RsiChart";
import MacdChart from "../components/analytics/MacdChart";
import IndicatorToggles from "../components/analytics/IndicatorToggles";
import AiForecastSection from "../components/analytics/AiForecastSection";
import RecommendationCard from "../components/analytics/RecommendationCard";
import useStockAnalytics from "../hooks/useStockAnalytics";
import { DEFAULT_OVERLAYS, formatPrice } from "../utils/analyticsHelpers";
import { isProductionApiConfigured } from "../api/api";

const PERIODS = [
  { id: "6mo", label: "6M" },
  { id: "1y", label: "1Y" },
  { id: "2y", label: "2Y" },
];

export default function AnalyticsPage() {
  const [inputSymbol, setInputSymbol] = useState("AAPL");
  const [overlays, setOverlays] = useState(DEFAULT_OVERLAYS);
  const { symbol, period, setPeriod, data, loading, error, fetchAnalytics } =
    useStockAnalytics("AAPL");

  const apiOff = import.meta.env.PROD && !isProductionApiConfigured();

  const quote = data?.quote ?? {};
  const bars = data?.bars ?? [];
  const changePct = quote.change_pct ?? 0;
  const changeClass =
    changePct > 0
      ? "text-terminal-positive"
      : changePct < 0
        ? "text-terminal-negative"
        : "text-terminal-muted";

  const handleSubmit = (e) => {
    e.preventDefault();
    fetchAnalytics(inputSymbol, period);
  };

  return (
    <div className="terminal-shell terminal-grid-bg min-h-screen">
      <Sidebar />

      <main className="ml-56 px-4 py-4 max-w-[calc(100vw-14rem)]">
        <header className="border-b border-terminal-border pb-3 mb-4">
          <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-terminal-muted">
            Markets
          </p>
          <div className="flex flex-wrap items-end justify-between gap-3 mt-1">
            <h1 className="text-lg font-semibold text-terminal-text tracking-tight">
              Stock Analytics
            </h1>
            {data && (
              <div className="text-right font-mono tabular-nums">
                <span className="text-terminal-cyan font-semibold text-lg">
                  {symbol}
                </span>
                <span className="text-terminal-text text-lg ml-2">
                  {formatPrice(quote.last)}
                </span>
                <span className={`text-sm ml-2 ${changeClass}`}>
                  {changePct >= 0 ? "+" : ""}
                  {changePct}%
                </span>
              </div>
            )}
          </div>
        </header>

        {apiOff && (
          <div className="mb-4 rounded-sm border border-terminal-gold/30 bg-terminal-gold/5 px-3 py-2 text-xs font-mono text-terminal-muted">
            Live analytics disabled: set <span className="text-terminal-cyan">VITE_API_BASE_URL</span> to
            your API URL.
          </div>
        )}

        <form
          onSubmit={handleSubmit}
          className="flex flex-wrap items-end gap-2 mb-4"
        >
          <div className="flex flex-col gap-1">
            <label className="kpi-label" htmlFor="analytics-symbol">
              Symbol
            </label>
            <input
              id="analytics-symbol"
              value={inputSymbol}
              onChange={(e) => setInputSymbol(e.target.value.toUpperCase())}
              className="terminal-input w-28 uppercase"
              placeholder="AAPL"
            />
          </div>
          <div className="flex flex-col gap-1">
            <span className="kpi-label">Period</span>
            <div className="flex gap-1">
              {PERIODS.map((p) => (
                <button
                  key={p.id}
                  type="button"
                  onClick={() => {
                    setPeriod(p.id);
                    if (data) {
                      fetchAnalytics(symbol, p.id);
                    }
                  }}
                  className={`font-mono text-[9px] uppercase px-2 py-1.5 rounded-sm border ${
                    period === p.id
                      ? "border-terminal-cyan/40 bg-terminal-cyan/10 text-terminal-cyan"
                      : "border-terminal-border text-terminal-muted"
                  }`}
                >
                  {p.label}
                </button>
              ))}
            </div>
          </div>
          <button type="submit" disabled={loading} className="terminal-btn">
            {loading ? "Loading…" : "Load"}
          </button>
          <IndicatorToggles overlays={overlays} onChange={setOverlays} />
        </form>

        {error && (
          <div className="mb-4 rounded-sm border border-terminal-negative/40 bg-terminal-negative/10 px-3 py-2 text-xs font-mono text-terminal-negative">
            {error}
          </div>
        )}

        {loading && !data && (
          <div className="py-16 text-center font-mono text-xs text-terminal-cyan animate-pulse">
            Fetching market data…
          </div>
        )}

        {data && (
          <div className="grid grid-cols-1 xl:grid-cols-[1fr_320px] gap-4">
            <div className="space-y-3 min-w-0">
              <CandlestickChart bars={bars} overlays={overlays} />
              <VolumeChart bars={bars} />
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <RsiChart bars={bars} />
                <MacdChart bars={bars} />
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-[10px] font-mono">
                <div className="kpi-card">
                  <p className="kpi-label">52W High</p>
                  <p className="kpi-value text-terminal-positive text-base">
                    {formatPrice(quote.high_52w)}
                  </p>
                </div>
                <div className="kpi-card">
                  <p className="kpi-label">52W Low</p>
                  <p className="kpi-value text-terminal-negative text-base">
                    {formatPrice(quote.low_52w)}
                  </p>
                </div>
                <div className="kpi-card">
                  <p className="kpi-label">Volume</p>
                  <p className="kpi-value text-terminal-cyan text-base">
                    {(quote.volume ?? 0).toLocaleString()}
                  </p>
                </div>
                <div className="kpi-card">
                  <p className="kpi-label">As of</p>
                  <p className="kpi-value text-terminal-muted text-xs mt-2">
                    {data.asOf?.slice(0, 10) ?? "—"}
                  </p>
                </div>
              </div>
            </div>

            <aside className="space-y-4">
              <RecommendationCard recommendation={data.recommendation} />
              <AiForecastSection forecast={data.forecast} symbol={symbol} />
            </aside>
          </div>
        )}
      </main>
    </div>
  );
}
