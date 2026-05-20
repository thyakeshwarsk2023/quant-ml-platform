from app.core.strategy.rsi import RSIStrategy
from app.core.strategy.moving_average import MovingAverageStrategy
from app.core.strategy.combined_strategy import CombinedStrategy

def get_strategies():
    return [
        ("RSI", RSIStrategy()),
        ("MA", MovingAverageStrategy()),
        ("Hybrid", CombinedStrategy())
    ]