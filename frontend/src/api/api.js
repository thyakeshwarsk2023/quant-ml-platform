import axios from "axios";
import {
  API_BASE_URL,
  resolveApiBaseUrl,
  isProductionApiConfigured,
} from "../config/api.js";

const DEFAULT_TIMEOUT_MS = 15000;
const LONG_TIMEOUT_MS = 45000;
const RETRY_STATUSES = new Set([408, 425, 429, 500, 502, 503, 504]);
const IDEMPOTENT_METHODS = new Set(["get", "head", "options"]);

const API = axios.create({
  baseURL: "",
  timeout: DEFAULT_TIMEOUT_MS,
  headers: {
    "Content-Type": "application/json",
  },
});

API.interceptors.request.use((config) => {
  if (import.meta.env.PROD && !API_BASE_URL) {
    const err = new Error("VITE_API_BASE_URL_NOT_SET");
    err.code = "NO_API_BASE";
    return Promise.reject(err);
  }
  config.baseURL = resolveApiBaseUrl();
  config.metadata = {
    startedAt: Date.now(),
    requestId:
      globalThis.crypto?.randomUUID?.() ??
      `${Date.now()}-${Math.random().toString(16).slice(2)}`,
  };
  config.headers["X-Request-ID"] = config.metadata.requestId;
  return config;
});

function shouldRetry(error) {
  const config = error?.config ?? {};
  const method = String(config.method ?? "get").toLowerCase();
  const status = error?.response?.status;
  const retryCount = config.__retryCount ?? 0;
  const maxRetries = config.retry ?? 0;

  if (retryCount >= maxRetries || !IDEMPOTENT_METHODS.has(method)) {
    return false;
  }

  return (
    error?.code === "ECONNABORTED" ||
    error?.code === "ERR_NETWORK" ||
    !error?.response ||
    RETRY_STATUSES.has(status)
  );
}

function retryDelayMs(attempt) {
  return Math.min(400 * 2 ** attempt, 3000);
}

API.interceptors.response.use(
  (response) => response,
  async (error) => {
    const config = error?.config ?? {};

    if (shouldRetry(error)) {
      config.__retryCount = (config.__retryCount ?? 0) + 1;
      await new Promise((resolve) =>
        setTimeout(resolve, retryDelayMs(config.__retryCount - 1))
      );
      return API(config);
    }

    const elapsedMs = config.metadata?.startedAt
      ? Date.now() - config.metadata.startedAt
      : undefined;

    console.error("API request failed", {
      method: config.method?.toUpperCase(),
      url: `${config.baseURL ?? ""}${config.url ?? ""}`,
      status: error?.response?.status,
      code: error?.code,
      message: error?.message,
      elapsedMs,
      requestId: config.metadata?.requestId,
      response: error?.response?.data,
    });

    return Promise.reject(error);
  }
);

export { isProductionApiConfigured };

export const getHealth = () => API.get("/health", { timeout: 8000, retry: 1 });

export const getDatabaseStatus = () =>
  API.get("/test-db", { timeout: 8000, retry: 1 });

export const runBacktest = (symbol) =>
  API.get("/run-backtest", { params: { symbol }, timeout: 12000, retry: 0 });

export const getEquity = (runId) =>
  API.get(`/equity/${runId}`, { timeout: 10000, retry: 1 });

export const getLeaderboard = () =>
  API.get("/leaderboard", { timeout: 10000, retry: 1 });

export const getRankings = (topK = 10) =>
  API.get("/rankings", { params: { top_k: topK }, timeout: 12000, retry: 1 });

export const getPortfolio = (topK = 10) =>
  API.get("/portfolio", { params: { top_k: topK }, timeout: 12000, retry: 1 });

export const startScan = () => API.post("/scan/start", undefined, { timeout: 8000 });

export const getScanStatus = (jobId) =>
  API.get(`/scan/status/${jobId}`, { timeout: 8000, retry: 1 });

export const getScanResults = (jobId) =>
  API.get(`/scan/results/${jobId}`, { timeout: 8000, retry: 1 });

export const getStockAnalytics = (symbol, period = "1y") =>
  API.get("/analytics", {
    params: { symbol, period },
    timeout: LONG_TIMEOUT_MS,
    retry: 1,
  });

export const getStockForecast = (symbol, period = "6mo") =>
  API.get("/forecast", {
    params: { symbol, period },
    timeout: LONG_TIMEOUT_MS,
    retry: 1,
  });

export const getModelMetrics = () =>
  API.get("/model/evaluate", { timeout: 8000, retry: 1 });

export default API;
