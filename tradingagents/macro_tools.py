# tradingagents/agents/utils/macro_tools.py

import yfinance as yf
import pandas as pd

def get_nifty_index_trend(
    start_date: str,
    end_date: str,
    window: int = 20,
) -> str:
    """
    Fetch NIFTY-50 index data and compute macro trend.
    Uses Yahoo Finance symbol: ^NSEI
    """

    df = yf.download("^NSEI", start=start_date, end=end_date, progress=False)

    if df.empty:
        return "NIFTY-50 index data unavailable."

    df["SMA"] = df["Close"].rolling(window).mean()

    latest = df.iloc[-1]
    trend = "Bullish" if latest["Close"] > latest["SMA"] else "Bearish"

    volatility = df["Close"].pct_change().std() * 100

    return f"""
NIFTY-50 Index Macro Analysis:
- Latest Close: {latest['Close']:.2f}
- {window}-day SMA: {latest['SMA']:.2f}
- Trend: {trend}
- Volatility (std %): {volatility:.2f}
"""
