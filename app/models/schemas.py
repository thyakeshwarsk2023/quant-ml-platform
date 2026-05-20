from pydantic import BaseModel, Field
from typing import List, Literal


class BacktestRequest(BaseModel):
    symbols: List[str] = Field(..., example=["AAPL", "TSLA"])
    strategy: Literal["ma", "rsi"] = "ma"
    capital: float = Field(100000, gt=0)

