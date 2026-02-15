# tradingagents/dataflows/selector.py

from tradingagents.dataflows.nifty50 import NIFTY_50
from tradingagents.dataflows.validator import validate_nifty50_symbol


def select_nifty50_company() -> str:
    """
    CLI-based selector for NIFTY-50 companies.
    Returns a validated + normalized Yahoo Finance symbol (e.g. RELIANCE.NS).
    """

    companies = sorted(NIFTY_50)

    print("\nSelect a NIFTY-50 company:\n")
    for idx, name in enumerate(companies, start=1):
        print(f"{idx:2d}. {name}")

    while True:
        try:
            choice = int(input("\nEnter choice (1–50): ").strip())

            if 1 <= choice <= len(companies):
                base_symbol = companies[choice - 1]

                # ✅ Validate + normalize → RELIANCE → RELIANCE.NS
                return validate_nifty50_symbol(base_symbol)

            else:
                print("Please enter a number between 1 and 50.")

        except ValueError:
            print("Invalid input. Please enter a number.")
