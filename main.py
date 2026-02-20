import copy
import os
from datetime import datetime

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.dataflows.selector import select_nifty50_company


# ======================================================
# STEP 1: SAFE CONFIG (DEEP COPY)
# ======================================================

config = copy.deepcopy(DEFAULT_CONFIG)

# ----- FORCE FREE + LOCAL LLM (OLLAMA) -----
config["llm_provider"] = "ollama"
config["backend_url"] = "http://localhost:11434"
config["deep_think_llm"] = "llama3"
config["quick_think_llm"] = "llama3"

# ----- PROJECT PATHS -----
config["project_dir"] = "."
config["data_dir"] = "dataflows/data_cache"

os.makedirs(config["data_dir"], exist_ok=True)

# ----- PERFORMANCE SETTINGS -----
config["max_debate_rounds"] = 1
config["enable_reflection"] = False

# ----- FREE DATA SOURCES -----
config["data_vendors"] = {
    "core_stock_apis": "yfinance",
    "technical_indicators": "yfinance",
    "fundamental_data": "yfinance",
    "news_data": "google",
}


# ======================================================
# STEP 2: INITIALIZE SYSTEM
# ======================================================

ta = TradingAgentsGraph(
    debug=True,  # set False in production
    config=config
)


# ======================================================
# STEP 3: SELECT COMPANY
# ======================================================

company = select_nifty50_company()

print(f"\nSelected Company: {company}\n")


# ======================================================
# STEP 4: RUN AGENTS
# ======================================================

today = datetime.today().strftime("%Y-%m-%d")

try:
    state, decision = ta.propagate(
        company_name=company,
        trade_date=today
    )

    print("\n================ FINAL DECISION ================\n")
    print(decision)

except Exception as e:
    print("\n❌ Error running trading agents:")
    print(str(e))
    decision = "Execution failed."


# ======================================================
# STEP 5: OPTIONAL BACKEND READY OUTPUT
# ======================================================

# If your backend friend wants JSON output,
# you can return something like this:

final_output = {
    "company": company,
    "trade_date": today,
    "decision": decision,
}

print("\n================ JSON OUTPUT ================\n")
print(final_output)
