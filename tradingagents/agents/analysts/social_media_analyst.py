from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


def create_social_media_analyst(llm):

    def social_media_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]

        system_message = (
            """You are a social media and public sentiment analyst.

Your task:
- Analyze public sentiment, social media discussions, and company-related buzz
- Infer investor psychology, hype, fear, optimism, or skepticism
- Highlight narrative trends (retail enthusiasm, fear, controversy, speculation)
- Explain how sentiment may affect short-term volatility and momentum

Guidelines:
- Be detailed and structured
- Avoid vague statements like "sentiment is mixed"
- Clearly distinguish bullish vs bearish sentiment drivers
- End with a Markdown table summarizing sentiment signals and trading implications

Do NOT mention tools, APIs, or data sources.
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
            "sentiment_report": result.content,
        }

    return social_media_analyst_node
