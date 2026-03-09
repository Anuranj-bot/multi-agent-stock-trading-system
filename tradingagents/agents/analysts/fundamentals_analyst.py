from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from tradingagents.agents.utils.agent_utils import (
    get_balance_sheet,
    get_cashflow,
    get_income_statement,
)


def create_fundamentals_analyst(llm):

    def fundamentals_analyst_node(state):

        current_date = state["trade_date"]
        ticker = state["company_of_interest"]

        # --------------------------------------------------
        # STEP 1: Fetch financial data directly (NO LLM loop)
        # --------------------------------------------------

        balance_sheet = get_balance_sheet.invoke({
            "ticker": ticker
        })

        cashflow = get_cashflow.invoke({
            "ticker": ticker
        })

        income_statement = get_income_statement.invoke({
            "ticker": ticker
        })

        # --------------------------------------------------
        # STEP 2: Prompt for analysis
        # --------------------------------------------------

        system_message = """
You are a financial fundamentals analyst.

Your job is to analyze the company's financial statements and provide insights useful for traders and investors.

Focus on:

• revenue growth trends
• profitability and margins
• cash flow health
• balance sheet strength
• debt levels
• financial risks
• long-term sustainability

Provide detailed but concise analysis.

At the end include a Markdown table summarizing:

| Financial Area | Key Insight | Trading Implication |
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
                    "Balance Sheet:\n{balance_sheet}\n\n"
                    "Cash Flow:\n{cashflow}\n\n"
                    "Income Statement:\n{income_statement}"
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(
            current_date=current_date,
            ticker=ticker,
            balance_sheet=balance_sheet,
            cashflow=cashflow,
            income_statement=income_statement,
        )

        chain = prompt | llm

        result = chain.invoke(state["messages"])

        return {
            "messages": [result],
            "fundamentals_report": result.content,
        }

    return fundamentals_analyst_node