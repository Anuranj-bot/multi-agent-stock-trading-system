from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.dataflows.selector import select_nifty50_company

# =========================
# STEP 1: Build SAFE config
# =========================

config = DEFAULT_CONFIG.copy()

# Force FREE + LOCAL LLM (Ollama)
config["llm_provider"] = "ollama"
config["backend_url"] = "http://localhost:11434"
config["deep_think_llm"] = "llama3"
config["quick_think_llm"] = "llama3"

# Required directories
config["project_dir"] = "."
config["data_dir"] = "./data"

# Reduce load (important)
config["max_debate_rounds"] = 1
config["enable_reflection"] = False

# FREE data sources only
config["data_vendors"] = {
    "core_stock_apis": "yfinance",
    "technical_indicators": "yfinance",
    "fundamental_data": "yfinance",
    "news_data": "google",
}

# =========================
# STEP 2: Initialize system
# =========================

ta = TradingAgentsGraph(
    debug=True,
    config=config
)

# =========================
# STEP 3: Select company
# =========================

company = select_nifty50_company()

# =========================
# STEP 4: Run agents
# =========================

state, decision = ta.propagate(
    company_name=company,
    trade_date="2024-05-10"
)

print("\n================ FINAL DECISION ================\n")
print(decision)
