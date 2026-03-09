from tradingagents.database.db_service import fetch_pending_request, save_agent_output
from tradingagents.agents.analysts.fundamentals_analyst import create_fundamentals_analyst

from langchain_ollama import ChatOllama


# Initialize LLM
llm = ChatOllama(
    model="llama3",
    base_url="http://localhost:11434",
    temperature=0.2
)

# Create the fundamental analyst
fundamental_agent = create_fundamentals_analyst(llm)

# Fetch request from database
request = fetch_pending_request()

if not request:
    print("No pending request found.")
    exit()

company = request["stock_symbol"]
report_date = request["trade_date"]

print(f"Running fundamentals analyst for {company}")

# Create state similar to graph
state = {
    "messages": [("human", company)],
    "company_of_interest": company,
    "trade_date": report_date,
    "fundamentals_report": ""
}

# Run agent
result = fundamental_agent(state)

report = result["fundamentals_report"]

print("\nReport generated successfully\n")

# Save to database
save_agent_output(
    company_name=company,
    report_date=report_date,
    agent_name="fundamentals",
    report=report
)

print("Report saved to database successfully.")