import { useCallback, useEffect, useState } from "react";
import { getStockAnalytics, isProductionApiConfigured } from "../api/api";
import { getApiErrorMessage } from "../utils/apiHelpers";
import { parseAnalyticsResponse } from "../utils/analyticsHelpers";

export default function useStockAnalytics(initialSymbol = "AAPL") {
  const [symbol, setSymbol] = useState(initialSymbol);
  const [period, setPeriod] = useState("1y");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchAnalytics = useCallback(async (sym, per) => {
    const target = (sym || symbol).trim().toUpperCase();
    const range = per || period;

    if (import.meta.env.PROD && !isProductionApiConfigured()) {
      setError("Set VITE_API_BASE_URL to load live analytics.");
      setData(null);
      return;
    }

    if (!target) {
      setError("Enter a valid symbol");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const res = await getStockAnalytics(target, range);
      const parsed = parseAnalyticsResponse(res.data);
      setData(parsed);
      setSymbol(parsed.symbol);
    } catch (err) {
      if (import.meta.env.DEV) {
        console.error("Analytics error:", err);
      }
      setError(getApiErrorMessage(err, "Failed to load analytics"));
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [symbol, period]);

  useEffect(() => {
    if (import.meta.env.PROD && !isProductionApiConfigured()) {
      setError("Set VITE_API_BASE_URL to load live analytics.");
      setLoading(false);
      return;
    }
    fetchAnalytics(initialSymbol, "1y");
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return {
    symbol,
    setSymbol,
    period,
    setPeriod,
    data,
    loading,
    error,
    fetchAnalytics,
  };
}
