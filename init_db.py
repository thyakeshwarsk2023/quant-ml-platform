from app.db.session import engine
from app.db.base import Base

# Import all models so Base.metadata knows about them
from app.models.backtest import BacktestRun, Metrics, EquityCurve

def init():
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")

if __name__ == "__main__":
    init()