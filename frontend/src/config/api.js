/**
 * API base URL for all backend requests.
 * Set VITE_API_BASE_URL in Vercel (production) or .env.local (local dev).
 */
const raw = import.meta.env.VITE_API_BASE_URL?.trim() ?? "";

export const API_BASE_URL = raw.replace(/\/$/, "");

export function resolveApiBaseUrl() {
  if (API_BASE_URL) {
    return API_BASE_URL;
  }
  if (import.meta.env.DEV) {
    return "http://127.0.0.1:8000";
  }
  console.error(
    "[Quant] VITE_API_BASE_URL is not set. Configure it in Vercel project settings."
  );
  return "";
}
