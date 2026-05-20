/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        terminal: {
          bg: "#04070d",
          surface: "#0a0f18",
          panel: "#0d1420",
          border: "#1a2332",
          muted: "#64748b",
          text: "#e2e8f0",
          cyan: "#22d3ee",
          blue: "#3b82f6",
          positive: "#22c55e",
          negative: "#ef4444",
          slate: "#94a3b8",
        },
      },
      fontFamily: {
        terminal: [
          "IBM Plex Mono",
          "ui-monospace",
          "SFMono-Regular",
          "Menlo",
          "monospace",
        ],
        sans: [
          "IBM Plex Sans",
          "Inter",
          "system-ui",
          "sans-serif",
        ],
      },
      boxShadow: {
        "glow-cyan": "0 0 24px rgba(34, 211, 238, 0.12)",
        "glow-green": "0 0 20px rgba(34, 197, 94, 0.15)",
        "glow-red": "0 0 20px rgba(239, 68, 68, 0.12)",
        panel: "inset 0 1px 0 rgba(255,255,255,0.04), 0 4px 24px rgba(0,0,0,0.4)",
      },
    },
  },
  plugins: [],
};
