from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from tradingagents.agents.utils.agent_utils import get_stock_data, get_indicators


def create_market_analyst(llm):

    def market_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]

        # Predefined indicators (fast and stable)
        indicators = [
            "close_50_sma",
            "close_200_sma",
            "macd",
            "rsi",
            "boll",
            "atr",
            "vwma"
        ]

        # -----------------------------
        # Fetch stock data
        # -----------------------------
        stock_data = get_stock_data.invoke({
            "symbol": ticker,
            "start_date": "2023-01-01",
            "end_date": current_date
        })

        # -----------------------------
        # Fetch indicator data
        # -----------------------------
        indicator_reports = []

        for indicator in indicators:
            result = get_indicators.invoke({
                "symbol": ticker,
                "indicator": indicator,
                "curr_date": current_date,
                "look_back_days": 30
            })
            indicator_reports.append(result)

        indicator_data = "\n".join(indicator_reports)

        # -----------------------------
        # Optimized prompt (smaller)
        # -----------------------------
        system_message = """
You are a financial market analyst.

Analyze the stock using the provided market data and technical indicators.

Focus on:
• trend direction
• momentum signals
• volatility behavior
• volume confirmation
• potential trading opportunities

Provide a structured market analysis.

End the report with a Markdown table summarizing the key insights.
"""

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    system_message
                    + "\nCurrent Date: {current_date}"
                    + "\nCompany: {ticker}"
                ),
                (
                    "human",
                    "Stock Data:\n{stock_data}\n\nIndicators:\n{indicator_data}"
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(
            current_date=current_date,
            ticker=ticker,
            stock_data=stock_data,
            indicator_data=indicator_data,
        )

        chain = prompt | llm

        result = chain.invoke(state["messages"])

        report = result.content

        return {
            "messages": [result],
            "market_report": report,
        }

    return market_analyst_node