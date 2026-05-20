import { useState, useEffect } from "react";
import { startScan, getScanStatus, getScanResults } from "../api/api";

export default function ScanPanel() {
  const [jobId, setJobId] = useState(null);
  const [progress, setProgress] = useState(0);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // 🔥 START SCAN
  const handleScan = async () => {
    try {
      setLoading(true);
      setError(null);
      setResults([]);
      setProgress(0);

      const res = await startScan();
      setJobId(res.data.job_id);
    } catch (e) {
      console.error(e);
      const status = e?.response?.status;
      setError(
        status === 404
          ? "Scanner API is not enabled on the server yet."
          : "Failed to start scan"
      );
      setLoading(false);
    }
  };

  // 🔥 POLLING
  useEffect(() => {
    if (!jobId) return;

    let stopped = false;

    const interval = setInterval(async () => {
      try {
        const res = await getScanStatus(jobId);

        if (stopped) return;

        setProgress(res.data.progress ?? 0);

        if (res.data.status === "completed") {
          clearInterval(interval);

          const resultsRes = await getScanResults(jobId);
          setResults(resultsRes.data || []);
          setLoading(false);
        }

        if (res.data.status === "failed") {
          clearInterval(interval);
          setError("Scan failed");
          setLoading(false);
        }

      } catch (e) {
        console.error(e);
        clearInterval(interval);
        setError("Scan error");
        setLoading(false);
      }
    }, 1500);

    return () => {
      stopped = true;
      clearInterval(interval);
    };
  }, [jobId]);

  return (
    <div className="bg-terminal-surface/80 border border-terminal-border p-5 rounded-xl">
      <button
        onClick={handleScan}
        disabled={loading}
        className="terminal-btn px-4 py-2 rounded disabled:opacity-50"
      >
        {loading ? "Scanning..." : "🔍 Scan Market"}
      </button>

      {jobId && (
        <p className="mt-2 text-terminal-muted font-mono text-xs">
          Progress: {progress}%
        </p>
      )}

      {error && <p className="text-terminal-negative mt-2 font-mono text-xs">{error}</p>}

      {/* EMPTY STATE */}
      {!loading && results.length === 0 && (
        <p className="text-terminal-muted mt-4 font-mono text-xs">No results yet</p>
      )}

      {/* RESULTS */}
      <div className="mt-4">
        {results.map((r, i) => (
          <div key={i} className="border-b border-terminal-border py-2 text-terminal-text font-mono text-xs">
            <b className="text-terminal-cyan">{r.symbol}</b> | Score: {(r.score ?? 0).toFixed(2)} | Sharpe: {(r.sharpe ?? 0).toFixed(2)} | Return: {(r.return ?? 0).toFixed(2)}
          </div>
        ))}
      </div>
    </div>
  );
}