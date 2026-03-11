from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from tradingagents.agents.utils.agent_utils import (
    get_insider_sentiment,
    get_insider_transactions
)


def create_social_media_analyst(llm):

    def social_media_analyst_node(state):

        current_date = state["trade_date"]
        ticker = state["company_of_interest"]

        # Fetch insider sentiment
        insider_sentiment = get_insider_sentiment.invoke({
            "ticker": ticker,
            "curr_date": current_date
        })

        # Fetch insider transactions
        insider_transactions = get_insider_transactions.invoke({
            "ticker": ticker,
            "curr_date": current_date
        })

        system_message = """
You are a market sentiment analyst.

Analyze insider sentiment and transaction data.

Focus on:
• insider buying vs selling
• sentiment shifts
• executive confidence
• institutional signals

Explain how this sentiment could influence market perception and trading behavior.

End with a Markdown table summarizing sentiment signals.
"""

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    system_message
                    + "\nCurrent date: {current_date}"
                    + "\nCompany: {ticker}"
                ),
                (
                    "human",
                    "Insider Sentiment:\n{insider_sentiment}\n\n"
                    "Insider Transactions:\n{insider_transactions}"
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(
            current_date=current_date,
            ticker=ticker,
            insider_sentiment=insider_sentiment,
            insider_transactions=insider_transactions
        )

        chain = prompt | llm
        result = chain.invoke(state["messages"])

        return {
            "messages": [result],
            "sentiment_report": result.content,
        }

    return social_media_analyst_node