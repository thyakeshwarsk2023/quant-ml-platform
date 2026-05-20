import { Routes, Route } from "react-router-dom";

import Dashboard from "./pages/Dashboard";
import RankingsPage from "./pages/Rankingspage";
import PortfolioPage from "./pages/Portfoliopage";
import BacktestsPage from "./pages/Backtestspage";
import ScannerPage from "./pages/Scannerpage";
import AnalyticsPage from "./pages/AnalyticsPage";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/rankings" element={<RankingsPage />} />
      <Route path="/portfolio" element={<PortfolioPage />} />
      <Route path="/backtests" element={<BacktestsPage />} />
      <Route path="/scanner" element={<ScannerPage />} />
      <Route path="/analytics" element={<AnalyticsPage />} />
    </Routes>
  );
}
