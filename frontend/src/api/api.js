import axios from "axios";
import {
  API_BASE_URL,
  resolveApiBaseUrl,
  isProductionApiConfigured,
} from "../config/api.js";

const API = axios.create({
  baseURL: "",
  timeout: 60000,
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
  return config;
});

API.interceptors.response.use(
  (response) => response,
  (error) => {
    if (import.meta.env.DEV) {
      console.error("API ERROR:", error?.response?.data ?? error.message);
    }
    return Promise.reject(error);
  }
);

export { isProductionApiConfigured };

export const getHealth = () => API.get("/health");

export const getDatabaseStatus = () => API.get("/test-db");

export const runBacktest = (symbol) =>
  API.get("/run-backtest", { params: { symbol } });

export const getEquity = (runId) => API.get(`/equity/${runId}`);

export const getLeaderboard = () => API.get("/leaderboard");

export const getRankings = (topK = 10) =>
  API.get("/rankings", { params: { top_k: topK } });

export const getPortfolio = (topK = 10) =>
  API.get("/portfolio", { params: { top_k: topK } });

export const startScan = () => API.post("/scan/start");

export const getScanStatus = (jobId) => API.get(`/scan/status/${jobId}`);

export const getScanResults = (jobId) => API.get(`/scan/results/${jobId}`);

export const getStockAnalytics = (symbol, period = "1y") =>
  API.get("/analytics", { params: { symbol, period } });

export const getStockForecast = (symbol, period = "6mo") =>
  API.get("/forecast", { params: { symbol, period } });

export const getModelMetrics = () => API.get("/model/evaluate");

export default API;
