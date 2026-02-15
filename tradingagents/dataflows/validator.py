from tradingagents.dataflows.nifty50 import NIFTY_50, normalize_nifty_symbol


class InvalidStockSymbol(ValueError):
    pass


def validate_nifty50_symbol(symbol: str) -> str:
    """
    Validate and normalize a user-selected NIFTY-50 stock symbol.
    Returns Yahoo Finance compatible symbol (e.g. RELIANCE.NS)
    """

    if not symbol or not isinstance(symbol, str):
        raise InvalidStockSymbol("Stock symbol must be a non-empty string")

    symbol = symbol.upper().strip()

    # Normalize → RELIANCE → RELIANCE.NS
    normalized = normalize_nifty_symbol(symbol)

    base_symbol = normalized.replace(".NS", "")

    if base_symbol not in NIFTY_50:
        raise InvalidStockSymbol(
            f"'{symbol}' is not a valid NIFTY-50 stock.\n"
            f"Please choose from official NIFTY-50 companies."
        )

    return normalized
