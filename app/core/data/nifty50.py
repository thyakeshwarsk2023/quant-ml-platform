"""
Compact NIFTY_50 subset for production-friendly inference.

This intentionally uses 15 liquid large-cap symbols to reduce:
- yfinance network calls on Render free tier
- model scoring loop time
- request latency for rankings/portfolio endpoints
"""

NIFTY_50 = [
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "SBIN.NS",
    "LT.NS",
    "ITC.NS",
    "BHARTIARTL.NS",
    "ASIANPAINT.NS",
    "KOTAKBANK.NS",
    "HCLTECH.NS",
    "AXISBANK.NS",
    "TITAN.NS",
    "MARUTI.NS",
]
