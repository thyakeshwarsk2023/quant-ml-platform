/**
 * API base URL for all backend requests.
 * Set VITE_API_BASE_URL in Vercel (production) or .env.local (local dev).
 * For a same-origin Vercel API deployment, set VITE_API_BASE_URL=/api.
 */
const raw = import.meta.env.VITE_API_BASE_URL?.trim() ?? "";

export const API_BASE_URL = raw.replace(/\/$/, "");

let loggedMissingProdApi = false;

/** True when production build has a non-empty API base or is self-hosted on same origin. */
export function isProductionApiConfigured() {
  if (import.meta.env.DEV) {
    return true;
  }
  if (API_BASE_URL) {
    return true;
  }
  // In a full-stack unified deployment (FastAPI serving dist), relative requests work directly.
  if (typeof window !== "undefined") {
    const host = window.location.hostname;
    if (!host.includes("vercel.app") && !host.includes("netlify.app")) {
      return true;
    }
  }
  return false;
}

export function resolveApiBaseUrl() {
  if (API_BASE_URL) {
    return API_BASE_URL;
  }
  if (import.meta.env.DEV) {
    return "http://127.0.0.1:8000";
  }
  if (!loggedMissingProdApi) {
    loggedMissingProdApi = true;
  }
  return "";
}
