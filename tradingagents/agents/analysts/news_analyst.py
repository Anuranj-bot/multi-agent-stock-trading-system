from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


def create_news_analyst(llm):

    def news_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]

        system_message = (
            """You are a financial news analyst.

Your task:
- Analyze recent company-specific news
- Analyze broader macroeconomic and global news
- Identify market-moving events, policy changes, earnings sentiment, and risks
- Explain how current news may impact stock price, volatility, and sector trends

Guidelines:
- Be detailed and structured
- Avoid vague conclusions like "news is mixed"
- Clearly distinguish short-term vs long-term impact
- End with a Markdown table summarizing key news themes and market implications

Do NOT mention tools, APIs, or how data was retrieved.
"""
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    system_message
                    + f"\nCurrent date: {current_date}\n"
                    + f"Company of interest: {ticker}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        chain = prompt | llm
        result = chain.invoke(state["messages"])

        return {
            "messages": [result],
            "news_report": result.content,
        }

    return news_analyst_node
