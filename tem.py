# from typing import Annotated
# from datetime import datetime
# from dateutil.relativedelta import relativedelta
import yfinance as yf
# import os
# import pandas as pd
# from stockstats import wrap
# from .tradingagents.dataflows.stockstats_utils import StockstatsUtils
# from .tradingagents.dataflows.config import get_config

def get_YFin_data_online( symbol):
    """
    Fetch live stock price data using yfinance.
    Returns a DataFrame.
    """

    # Validate date format
    



    data = yf.download(
        symbol.upper(),
        period= "1mo",
        
        auto_adjust=True,
    
    )
    print(data)

get_YFin_data_online ('AXISBANK.NS')
 