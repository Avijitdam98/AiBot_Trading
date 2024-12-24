import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

class StockDataFetcher:
    def __init__(self):
        self.cache = {}
        
    def get_stock_data(self, symbol: str, period: str = "1mo", interval: str = "1d"):
        """
        Fetch stock data from Yahoo Finance
        
        Args:
            symbol (str): Stock symbol (e.g., 'AAPL')
            period (str): Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval (str): Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
            
        Returns:
            pd.DataFrame: DataFrame with stock data
        """
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            self.cache[symbol] = df
            return df
        except Exception as e:
            print(f"Error fetching data for {symbol}: {str(e)}")
            return None
    
    def get_live_price(self, symbol: str) -> float:
        """Get the current price of a stock"""
        try:
            ticker = yf.Ticker(symbol)
            return ticker.info['regularMarketPrice']
        except Exception as e:
            print(f"Error fetching live price for {symbol}: {str(e)}")
            return None
    
    def get_multiple_stocks(self, symbols: list, period: str = "1mo", interval: str = "1d"):
        """Fetch data for multiple stocks"""
        data = {}
        for symbol in symbols:
            data[symbol] = self.get_stock_data(symbol, period, interval)
        return data
