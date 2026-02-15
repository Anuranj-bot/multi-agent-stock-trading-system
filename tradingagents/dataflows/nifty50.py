# tradingagents/dataflows/nifty50.py

NIFTY_50 = {
    "ADANIENT",
    "ADANIPORTS",
    "APOLLOHOSP",
    "ASIANPAINT",
    "AXISBANK",
    "BAJAJ-AUTO",
    "BAJFINANCE",
    "BAJAJFINSV",
    "BHARTIARTL",
    "BPCL",
    "BRITANNIA",
    "CIPLA",
    "COALINDIA",
    "DIVISLAB",
    "DRREDDY",
    "EICHERMOT",
    "GRASIM",
    "HCLTECH",
    "HDFCBANK",
    "HDFCLIFE",
    "HEROMOTOCO",
    "HINDALCO",
    "HINDUNILVR",
    "ICICIBANK",
    "INDUSINDBK",
    "INFY",
    "ITC",
    "JSWSTEEL",
    "KOTAKBANK",
    "LT",
    "M&M",
    "MARUTI",
    "NESTLEIND",
    "NTPC",
    "ONGC",
    "POWERGRID",
    "RELIANCE",
    "SBILIFE",
    "SBIN",
    "SUNPHARMA",
    "TATACONSUM",
    "TATAMOTORS",
    "TATASTEEL",
    "TCS",
    "TECHM",
    "TITAN",
    "ULTRACEMCO",
    "UPL",
    "WIPRO",
}


def normalize_nifty_symbol(symbol: str) -> str:
    """
    Normalize Indian stock symbols to Yahoo Finance NSE format.
    Examples:
        RELIANCE -> RELIANCE.NS
        TCS -> TCS.NS
        INFY.NS -> INFY.NS
    """
    if not symbol or not isinstance(symbol, str):
        return symbol

    symbol = symbol.upper().strip()

    if symbol.endswith(".NS"):
        return symbol

    return f"{symbol}.NS"
