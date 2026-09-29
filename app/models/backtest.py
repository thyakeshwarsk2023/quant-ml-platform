from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from app.db.base import Base


class BacktestRun(Base):
    __tablename__ = "backtest_runs"

    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, nullable=True)
    symbol = Column(String, index=True)
    initial_capital = Column(Float, default=100000)
    final_capital = Column(Float, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    status = Column(String, default="pending")  # pending / running / completed / failed


class Metrics(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("backtest_runs.id"), index=True)

    # =========================
    # PERFORMANCE METRICS
    # =========================
    return_pct = Column(Float)
    sharpe = Column(Float)
    max_drawdown = Column(Float)
    volatility = Column(Float)
    win_rate = Column(Float)
    profit_factor = Column(Float)
    ml_score = Column(Float, default=0)


class EquityCurve(Base):
    __tablename__ = "equity_curve"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("backtest_runs.id"), index=True)
    timestamp = Column(Date)
    equity = Column(Float)