from typing import Annotated
import pandas as pd
import os
from .config import DATA_DIR
from datetime import datetime
from dateutil.relativedelta import relativedelta
import json
from .reddit_utils import fetch_top_from_category
from tqdm import tqdm


# ===============================
# YFINANCE (LOCAL CSV ONLY)
# ===============================

def get_YFin_data_window(
    symbol: Annotated[str, "ticker symbol of the company"],
    curr_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    look_back_days: Annotated[int, "how many days to look back"],
) -> str:

    date_obj = datetime.strptime(curr_date, "%Y-%m-%d")
    start_date = (date_obj - relativedelta(days=look_back_days)).strftime("%Y-%m-%d")

    csv_path = os.path.join(
        DATA_DIR,
        f"market_data/price_data/{symbol}-YFin-data-2015-01-01-2025-03-25.csv",
    )

    if not os.path.exists(csv_path):
        return ""

    data = pd.read_csv(csv_path)
    data["DateOnly"] = data["Date"].str[:10]

    filtered_data = data[
        (data["DateOnly"] >= start_date) & (data["DateOnly"] <= curr_date)
    ].drop(columns=["DateOnly"])

    return (
        f"## Raw Market Data for {symbol} from {start_date} to {curr_date}:\n\n"
        + filtered_data.to_string()
    )


def get_YFin_data(
    symbol: Annotated[str, "ticker symbol"],
    start_date: Annotated[str, "Start date yyyy-mm-dd"],
    end_date: Annotated[str, "End date yyyy-mm-dd"],
):

    csv_path = os.path.join(
        DATA_DIR,
        f"market_data/price_data/{symbol}-YFin-data-2015-01-01-2025-03-25.csv",
    )

    if not os.path.exists(csv_path):
        return ""

    data = pd.read_csv(csv_path)
    data["DateOnly"] = data["Date"].str[:10]

    filtered = data[
        (data["DateOnly"] >= start_date) & (data["DateOnly"] <= end_date)
    ].drop(columns=["DateOnly"])

    return filtered.reset_index(drop=True)


# ===============================
# FINNHUB (OFFLINE JSON ONLY)
# ===============================

def get_data_in_range(ticker, start_date, end_date, data_type, data_dir, period=None):

    if period:
        data_path = os.path.join(
            data_dir, "finnhub_data", data_type, f"{ticker}_{period}_data_formatted.json"
        )
    else:
        data_path = os.path.join(
            data_dir, "finnhub_data", data_type, f"{ticker}_data_formatted.json"
        )

    if not os.path.exists(data_path):
        return {}

    with open(data_path, "r") as f:
        data = json.load(f)

    return {
        k: v
        for k, v in data.items()
        if start_date <= k <= end_date and v
    }


def get_finnhub_news(query, start_date, end_date):

    result = get_data_in_range(query, start_date, end_date, "news_data", DATA_DIR)

    if not result:
        return ""

    output = ""
    for day, items in result.items():
        for entry in items:
            output += f"### {entry['headline']} ({day})\n{entry['summary']}\n\n"

    return f"## {query} News ({start_date} → {end_date})\n{output}"


def get_finnhub_company_insider_sentiment(ticker, curr_date):

    before = (datetime.strptime(curr_date, "%Y-%m-%d") - relativedelta(days=15)).strftime("%Y-%m-%d")
    data = get_data_in_range(ticker, before, curr_date, "insider_senti", DATA_DIR)

    if not data:
        return ""

    seen = set()
    report = ""

    for _, entries in data.items():
        for e in entries:
            key = (e["year"], e["month"])
            if key not in seen:
                seen.add(key)
                report += (
                    f"### {e['year']}-{e['month']}\n"
                    f"Change: {e['change']}\n"
                    f"MSPR: {e['mspr']}\n\n"
                )

    return f"## Insider Sentiment ({before} → {curr_date})\n{report}"


def get_finnhub_company_insider_transactions(ticker, curr_date):

    before = (datetime.strptime(curr_date, "%Y-%m-%d") - relativedelta(days=15)).strftime("%Y-%m-%d")
    data = get_data_in_range(ticker, before, curr_date, "insider_trans", DATA_DIR)

    if not data:
        return ""

    report = ""
    seen = set()

    for _, entries in data.items():
        for e in entries:
            key = e["filingDate"]
            if key not in seen:
                seen.add(key)
                report += (
                    f"### {e['name']} ({e['filingDate']})\n"
                    f"Shares: {e['share']}, Change: {e['change']}, Price: {e['transactionPrice']}\n\n"
                )

    return f"## Insider Transactions ({before} → {curr_date})\n{report}"


# ===============================
# REDDIT (OFFLINE ONLY)
# ===============================

def get_reddit_global_news(curr_date, look_back_days=7, limit=5):

    start = datetime.strptime(curr_date, "%Y-%m-%d") - relativedelta(days=look_back_days)
    posts = []

    curr = start
    while curr <= datetime.strptime(curr_date, "%Y-%m-%d"):
        posts.extend(
            fetch_top_from_category(
                "global_news",
                curr.strftime("%Y-%m-%d"),
                limit,
                data_path=os.path.join(DATA_DIR, "reddit_data"),
            )
        )
        curr += relativedelta(days=1)

    if not posts:
        return ""

    text = ""
    for p in posts:
        text += f"### {p['title']}\n{p.get('content','')}\n\n"

    return f"## Global News ({start.date()} → {curr_date})\n{text}"


def get_reddit_company_news(query, start_date, end_date):

    posts = []
    curr = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    while curr <= end:
        posts.extend(
            fetch_top_from_category(
                "company_news",
                curr.strftime("%Y-%m-%d"),
                10,
                query,
                data_path=os.path.join(DATA_DIR, "reddit_data"),
            )
        )
        curr += relativedelta(days=1)

    if not posts:
        return ""

    text = ""
    for p in posts:
        text += f"### {p['title']}\n{p.get('content','')}\n\n"

    return f"## {query} Reddit News ({start_date} → {end_date})\n{text}"
def get_simfin_balance_sheet(*args, **kwargs):
    return ""

def get_simfin_cashflow(*args, **kwargs):
    return ""

def get_simfin_income_statements(*args, **kwargs):
    return ""

def get_simfin_fundamentals(*args, **kwargs):
    return ""
