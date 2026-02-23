from typing import Annotated
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import os
import pandas as pd
from stockstats import wrap
from .stockstats_utils import StockstatsUtils
from .config import get_config
from tradingagents.db import get_connection

# =========================================================
# LIVE YFINANCE DATA (SAFE + DYNAMIC)
# =========================================================
    
def get_YFin_data_online(symbol, start_date, end_date):
    """
    Fetch stock data from TimescaleDB instead of yfinance.
    """

    try:
        conn = get_connection()
        cur = conn.cursor()

        query = """
            SELECT time, open, high, low, close
            FROM stock_data
            WHERE symbol = %s
            AND time BETWEEN %s AND %s
            ORDER BY time ASC;
        """

        cur.execute(query, (symbol.upper(), start_date, end_date))

        rows = cur.fetchall()

        if not rows:
            return f"No data found for symbol '{symbol}'"

        # Convert to DataFrame
        import pandas as pd

        df = pd.DataFrame(rows, columns=["Date", "Open", "High", "Low", "Close"])

        cur.close()
        conn.close()

        return df

    except Exception as e:
        return f"Database fetch error: {str(e)}"


# =========================================================
# BULK INDICATOR CALCULATION (AUTO REFRESH CACHE)
# =========================================================

def _get_stock_stats_bulk(
    symbol: Annotated[str, "ticker symbol"],
    indicator: Annotated[str, "technical indicator"],
    curr_date: Annotated[str, "current date YYYY-MM-DD"]
) -> dict:

    config = get_config()
    cache_dir = config.get("data_dir", "dataflows/data_cache")
    os.makedirs(cache_dir, exist_ok=True)

    today = datetime.today()
    start_date = today - relativedelta(years=15)

    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = today.strftime("%Y-%m-%d")

    data_file = os.path.join(cache_dir, f"{symbol}_latest_cache.csv")

    refresh_required = True

    # ---------------------------
    # Check Cache Freshness
    # ---------------------------
    if os.path.exists(data_file):
        file_modified_time = datetime.fromtimestamp(os.path.getmtime(data_file))

        # If file modified today, don't refresh
        if file_modified_time.date() == today.date():
            refresh_required = False

    # ---------------------------
    # Fetch / Refresh Data
    # ---------------------------
    if refresh_required:
        data = yf.download(
            symbol.upper(),
            start=start_date_str,
            end=end_date_str,
            progress=False,
            auto_adjust=True,
        )

        if data.empty:
            raise ValueError("No price data available from yfinance.")

        data.reset_index(inplace=True)

        if "Date" not in data.columns:
            data.rename(columns={data.columns[0]: "Date"}, inplace=True)

        data.to_csv(data_file, index=False)

    else:
        data = pd.read_csv(data_file)
        data["Date"] = pd.to_datetime(data["Date"])

    # ---------------------------
    # Calculate Indicator
    # ---------------------------
    df = wrap(data)

    if indicator not in df.columns:
        try:
            df[indicator]
        except Exception:
            raise ValueError(f"Indicator '{indicator}' is not supported.")

    df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")

    result_dict = {}

    for _, row in df.iterrows():
        value = row.get(indicator)

        if pd.isna(value):
            result_dict[row["Date"]] = "N/A"
        else:
            result_dict[row["Date"]] = str(round(float(value), 4))

    return result_dict


# =========================================================
# WINDOWED INDICATOR REPORT
# =========================================================

def get_stock_stats_indicators_window(
    symbol: Annotated[str, "ticker symbol"],
    indicator: Annotated[str, "indicator name"],
    curr_date: Annotated[str, "YYYY-MM-DD"],
    look_back_days: Annotated[int, "days to look back"],
) -> str:

    try:
        curr_date_dt = datetime.strptime(curr_date, "%Y-%m-%d")
    except ValueError:
        return "Invalid date format."

    before = curr_date_dt - relativedelta(days=look_back_days)

    try:
        indicator_data = _get_stock_stats_bulk(symbol, indicator, curr_date)
    except Exception as e:
        return f"Indicator error: {str(e)}"

    result_lines = []
    current_dt = curr_date_dt

    while current_dt >= before:
        date_str = current_dt.strftime("%Y-%m-%d")
        value = indicator_data.get(date_str, "N/A")
        result_lines.append(f"{date_str}: {value}")
        current_dt -= relativedelta(days=1)

    return (
        f"## {indicator} values from {before.strftime('%Y-%m-%d')} to {curr_date}\n\n"
        + "\n".join(result_lines)
    )


# =========================================================
# SINGLE DAY INDICATOR (Fallback)
# =========================================================

def get_stockstats_indicator(symbol, indicator, curr_date):
    try:
        return str(
            StockstatsUtils.get_stock_stats(symbol, indicator, curr_date)
        )
    except Exception:
        return "N/A"


# =========================================================
# FUNDAMENTALS (LIVE SAFE)
# =========================================================

def get_balance_sheet(ticker, freq="quarterly", curr_date=None):
    try:
        ticker_obj = yf.Ticker(ticker.upper())
        data = (
            ticker_obj.quarterly_balance_sheet
            if freq.lower() == "quarterly"
            else ticker_obj.balance_sheet
        )

        if data is None or data.empty:
            return f"No balance sheet data found for '{ticker}'"

        return data.to_csv()

    except Exception as e:
        return f"Balance sheet error: {str(e)}"


def get_cashflow(ticker, freq="quarterly", curr_date=None):
    try:
        ticker_obj = yf.Ticker(ticker.upper())
        data = (
            ticker_obj.quarterly_cashflow
            if freq.lower() == "quarterly"
            else ticker_obj.cashflow
        )

        if data is None or data.empty:
            return f"No cash flow data found for '{ticker}'"

        return data.to_csv()

    except Exception as e:
        return f"Cash flow error: {str(e)}"


def get_income_statement(ticker, freq="quarterly", curr_date=None):
    try:
        ticker_obj = yf.Ticker(ticker.upper())
        data = (
            ticker_obj.quarterly_income_stmt
            if freq.lower() == "quarterly"
            else ticker_obj.income_stmt
        )

        if data is None or data.empty:
            return f"No income statement data found for '{ticker}'"

        return data.to_csv()

    except Exception as e:
        return f"Income statement error: {str(e)}"


def get_insider_transactions(ticker):
    try:
        ticker_obj = yf.Ticker(ticker.upper())
        data = ticker_obj.insider_transactions

        if data is None or data.empty:
            return f"No insider transactions data found for '{ticker}'"

        return data.to_csv()

    except Exception as e:
        return f"Insider transaction error: {str(e)}"
