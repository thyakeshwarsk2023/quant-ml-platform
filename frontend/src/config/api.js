/**
 * API base URL for all backend requests.
 * Set VITE_API_BASE_URL in Vercel (production) or .env.local (local dev).
 */
const raw = import.meta.env.VITE_API_BASE_URL?.trim() ?? "";

export const API_BASE_URL = raw.replace(/\/$/, "");

let loggedMissingProdApi = false;

/** True when production build has a non-empty API base (avoids 404s to Vercel host). */
export function isProductionApiConfigured() {
  if (import.meta.env.DEV) {
    return true;
  }
  return Boolean(API_BASE_URL);
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
