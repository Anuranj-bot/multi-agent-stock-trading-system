from tradingagents.database.db_service import fetch_pending_request, save_agent_output

from tradingagents.agents.analysts.market_analyst import create_market_analyst
from tradingagents.agents.analysts.news_analyst import create_news_analyst
from tradingagents.agents.analysts.social_media_analyst import create_social_media_analyst
from tradingagents.agents.analysts.fundamentals_analyst import create_fundamentals_analyst

from langchain_community.chat_models import ChatOllama


# Initialize LLM
llm = ChatOllama(
    model="llama3",
    base_url="http://localhost:11434",
    temperature=0.2
)

# Fetch request
request = fetch_pending_request()

if not request:
    print("No pending request found.")
    exit()

company = request["stock_symbol"]
report_date = request["trade_date"]

print(f"\nRunning all analysts for {company}\n")


# Create state
state = {
    "messages": [("human", company)],
    "company_of_interest": company,
    "trade_date": report_date,
    "market_report": "",
    "sentiment_report": "",
    "news_report": "",
    "fundamentals_report": ""
}


# -------- MARKET ANALYST --------
market_agent = create_market_analyst(llm)
result = market_agent(state)

save_agent_output(company, report_date, "market", result["market_report"])
print("Market report saved")


# -------- SOCIAL ANALYST --------
social_agent = create_social_media_analyst(llm)
result = social_agent(state)

save_agent_output(company, report_date, "social", result["sentiment_report"])
print("Social report saved")


# -------- NEWS ANALYST --------
news_agent = create_news_analyst(llm)
result = news_agent(state)

save_agent_output(company, report_date, "news", result["news_report"])
print("News report saved")


# -------- FUNDAMENTALS ANALYST --------
fund_agent = create_fundamentals_analyst(llm)
result = fund_agent(state)

save_agent_output(company, report_date, "fundamentals", result["fundamentals_report"])
print("Fundamentals report saved")


print("\nAll analyst reports stored successfully.")