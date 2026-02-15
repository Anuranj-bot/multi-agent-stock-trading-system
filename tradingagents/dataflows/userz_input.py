from tradingagents.dataflows.nifty50 import NIFTY50_MAP

def list_nifty50_companies():
    """Return sorted list of NIFTY 50 companies"""
    return sorted(NIFTY50_MAP.keys())

def validate_company_input(company: str) -> str:
    """
    Validate user input company name.
    Returns normalized company name.
    """
    if not company:
        raise ValueError("Company name cannot be empty")

    company = company.upper().strip()

    if company not in NIFTY50_MAP:
        available = ", ".join(sorted(NIFTY50_MAP.keys()))
        raise ValueError(
            f"❌ '{company}' is not a NIFTY 50 company.\n\n"
            f"✅ Available options:\n{available}"
        )

    return company
