from typing import Annotated
from tradingagents.dataflows.nifty50 import normalize_nifty_symbol


# Import from vendor-specific modules

from .local import (
    get_YFin_data,
    get_finnhub_news,
    get_finnhub_company_insider_sentiment,
    get_finnhub_company_insider_transactions,
    get_simfin_balance_sheet,
    get_simfin_cashflow,
    get_simfin_income_statements,
    get_reddit_global_news,
    get_reddit_company_news,
)
from .y_finance import (
    get_YFin_data_online,
    get_stock_stats_indicators_window,
    get_balance_sheet as get_yfinance_balance_sheet,
    get_cashflow as get_yfinance_cashflow,
    get_income_statement as get_yfinance_income_statement,
    get_insider_transactions as get_yfinance_insider_transactions,
)
from .google import get_google_news


# Configuration and routing logic
from .config import get_config


# =========================================================
# STEP 4: Indian ticker normalization helper
# =========================================================



# =========================================================
# Tool categories
# =========================================================
TOOLS_CATEGORIES = {
    "core_stock_apis": {
        "description": "OHLCV stock price data",
        "tools": ["get_stock_data"],
    },
    "technical_indicators": {
        "description": "Technical analysis indicators",
        "tools": ["get_indicators"],
    },
    "fundamental_data": {
        "description": "Company fundamentals",
        "tools": [
            "get_fundamentals",
            "get_balance_sheet",
            "get_cashflow",
            "get_income_statement",
        ],
    },
    "news_data": {
        "description": "News (public/insiders, original/processed)",
        "tools": [
            "get_news",
            "get_global_news",
            "get_insider_sentiment",
            "get_insider_transactions",
        ],
    },
}

VENDOR_LIST = ["local", "yfinance",  "google"]

# =========================================================
# Vendor implementations
# =========================================================
VENDOR_METHODS = {
    "get_stock_data": {
        "yfinance": get_YFin_data_online,
        "local": get_YFin_data,
    },
    "get_indicators": {
        "yfinance": get_stock_stats_indicators_window,
        "local": get_stock_stats_indicators_window,
    },

    # ❌ REMOVE get_fundamentals COMPLETELY

    "get_balance_sheet": {
        "yfinance": get_yfinance_balance_sheet,
        "local": get_simfin_balance_sheet,
    },
    "get_cashflow": {
        "yfinance": get_yfinance_cashflow,
        "local": get_simfin_cashflow,
    },
    "get_income_statement": {
        "yfinance": get_yfinance_income_statement,
        "local": get_simfin_income_statements,
    },
    "get_news": {
        "google": get_google_news,
        "local": [
            get_google_news,
            get_reddit_company_news,
        ],
    },
    "get_global_news": {
        "local": get_reddit_global_news,
    },
    "get_insider_sentiment": {
        "local": get_finnhub_company_insider_sentiment,
    },
    "get_insider_transactions": {
        "yfinance": get_yfinance_insider_transactions,
        "local": get_finnhub_company_insider_transactions,
    },
}



# =========================================================
# Helper functions
# =========================================================
def get_category_for_method(method: str) -> str:
    for category, info in TOOLS_CATEGORIES.items():
        if method in info["tools"]:
            return category
    raise ValueError(f"Method '{method}' not found in any category")


def get_vendor(category: str, method: str = None) -> str:
    config = get_config()

    # Tool-level override
    if method:
        tool_vendors = config.get("tool_vendors", {})
        if method in tool_vendors:
            return tool_vendors[method]

    # Category-level default
    return config.get("data_vendors", {}).get(category, "default")


# =========================================================
# ROUTER (ONLY PLACE WE MODIFY INPUTS)
# =========================================================
STOCK_SYMBOL_METHODS = {
    "get_stock_data",
    "get_indicators",
    "get_balance_sheet",
    "get_cashflow",
    "get_income_statement",
    "get_insider_transactions",
}

def route_to_vendor(method: str, *args, **kwargs):
    """Route method calls to appropriate vendor implementation with fallback support."""

    # =====================================================
    # STEP 7.3 — Normalize NIFTY-50 stock symbols (SAFE)
    # =====================================================
    if method in STOCK_SYMBOL_METHODS and len(args) > 0:
        symbol = args[0]

        if isinstance(symbol, str):
            try:
                normalized_symbol = normalize_nifty_symbol(symbol)
                args = (normalized_symbol,) + args[1:]
            except ValueError as e:
                raise RuntimeError(str(e))

    # =====================================================
    # Existing routing logic (UNCHANGED)
    # =====================================================
    category = get_category_for_method(method)
    vendor_config = get_vendor(category, method)

    primary_vendors = [v.strip() for v in vendor_config.split(",")]

    if method not in VENDOR_METHODS:
        raise ValueError(f"Method '{method}' not supported")

    all_available_vendors = list(VENDOR_METHODS[method].keys())

    fallback_vendors = primary_vendors.copy()
    for vendor in all_available_vendors:
        if vendor not in fallback_vendors:
            fallback_vendors.append(vendor)

    results = []

    for vendor in fallback_vendors:
        if vendor not in VENDOR_METHODS[method]:
            continue

        vendor_impl = VENDOR_METHODS[method][vendor]
        implementations = (
            vendor_impl if isinstance(vendor_impl, list) else [vendor_impl]
        )

    for impl in implementations:
      try:
        result = impl(*args, **kwargs)
        results.append(result)

        # If only one primary vendor is configured, return immediately
        if len(primary_vendors) == 1:
            return result

      except Exception as e:
        # Log error if you want, otherwise silently fallback
        print(f"Vendor implementation failed: {e}")
        continue

    if not results:
        raise RuntimeError(f"All vendor implementations failed for method '{method}'")

    return results[0] if len(results) == 1 else "\n".join(map(str, results))