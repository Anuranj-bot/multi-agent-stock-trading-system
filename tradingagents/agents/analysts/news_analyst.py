from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from tradingagents.agents.utils.agent_utils import get_news, get_global_news


def create_news_analyst(llm):

    def news_analyst_node(state):

        current_date = state["trade_date"]
        ticker = state["company_of_interest"]

        # Fetch company news
        company_news = get_news.invoke({
            "ticker": ticker,
            "start_date": "2024-01-01",
            "end_date": current_date
        })

        # Fetch global news
        global_news = get_global_news.invoke({
            "curr_date": current_date,
            "look_back_days": 7,
            "limit": 10
        })

        system_message = """
You are a financial news analyst.

Analyze the company news and global macroeconomic news.

Focus on:
• earnings announcements
• policy changes
• sector trends
• geopolitical impacts
• macroeconomic signals

Explain how these news events may influence stock price and volatility.

End with a Markdown table summarizing key news insights.
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
                    "Company News:\n{company_news}\n\nGlobal News:\n{global_news}"
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(
            current_date=current_date,
            ticker=ticker,
            company_news=company_news,
            global_news=global_news
        )

        chain = prompt | llm
        result = chain.invoke(state["messages"])

        return {
            "messages": [result],
            "news_report": result.content,
        }

    return news_analyst_node