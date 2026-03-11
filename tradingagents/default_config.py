DEFAULT_CONFIG = {
    # ======================
    # PROJECT
    # ======================
    "project_dir": ".",

    # ======================
    # LLM CONFIG (FREE)
    # ======================
    "llm_provider": "groq",
    "backend_url": "http://localhost:11434",

    # Use phi3 for speed
    "deep_think_llm": "llama-3.1-70b-versatile",
    "quick_think_llm": "llama-3.1-8b-instant",

    # ======================
    # DATA DIRECTORY
    # ======================
    "data_dir": "dataflows/data_cache",

    # DATA VENDORS (VERY IMPORTANT)

    "data_vendors": {
        "core_stock_apis": "yfinance",
        "technical_indicators": "yfinance",
        "fundamental_data": "yfinance",
        "news_data": "google,local"
    },
    # LIMITS
    "max_debate_rounds": 1,
}