import pandas as pd
import numpy as np
from data_fetcher import StockDataFetcher
from strategies import (MovingAverageCrossover, RSIStrategy, MACDStrategy,
                      BollingerBandsStrategy, VWAPStrategy, SupportResistanceStrategy)
import matplotlib.pyplot as plt
import seaborn as sns

class TradingBot:
    def __init__(self, symbols: list, strategy: str = 'MA', initial_capital: float = 10000):
        self.symbols = symbols
        self.data_fetcher = StockDataFetcher()
        self.strategy = self._get_strategy(strategy)
        self.capital = initial_capital
        self.positions = {symbol: 0 for symbol in symbols}
        self.trades = []
    
    def _get_strategy(self, strategy_name: str):
        """Initialize the selected trading strategy"""
        if strategy_name.upper() == 'MA':
            return MovingAverageCrossover()
        elif strategy_name.upper() == 'RSI':
            return RSIStrategy()
        elif strategy_name.upper() == 'MACD':
            return MACDStrategy()
        elif strategy_name.upper() == 'BB':
            return BollingerBandsStrategy()
        elif strategy_name.upper() == 'VWAP':
            return VWAPStrategy()
        elif strategy_name.upper() == 'SR':
            return SupportResistanceStrategy()
        else:
            raise ValueError(f"Unknown strategy: {strategy_name}")
    
    def run(self, period: str = "1mo", interval: str = "1d"):
        """Run the trading bot"""
        for symbol in self.symbols:
            # Fetch data
            data = self.data_fetcher.get_stock_data(symbol, period, interval)
            if data is None:
                continue
            
            # Generate signals
            signals = self.strategy.generate_signals(data)
            
            # Execute trades
            self._execute_trades(symbol, signals)
            
            # Plot results
            self._plot_results(symbol, signals)
    
    def _execute_trades(self, symbol: str, signals: pd.DataFrame):
        """Execute trades based on signals"""
        position = 0
        for index, row in signals.iterrows():
            if row['Signal'] == 1 and position <= 0:  # Buy signal
                price = row['Close']
                shares = int(self.capital * 0.1 / price)  # Use 10% of capital
                if shares > 0:
                    cost = shares * price
                    self.capital -= cost
                    self.positions[symbol] += shares
                    self.trades.append({
                        'date': index,
                        'symbol': symbol,
                        'type': 'BUY',
                        'shares': shares,
                        'price': price,
                        'cost': cost
                    })
                    position = 1
                    
            elif row['Signal'] == -1 and position >= 0:  # Sell signal
                if self.positions[symbol] > 0:
                    price = row['Close']
                    shares = self.positions[symbol]
                    revenue = shares * price
                    self.capital += revenue
                    self.positions[symbol] = 0
                    self.trades.append({
                        'date': index,
                        'symbol': symbol,
                        'type': 'SELL',
                        'shares': shares,
                        'price': price,
                        'revenue': revenue
                    })
                    position = -1
    
    def _plot_results(self, symbol: str, signals: pd.DataFrame):
        """Plot trading results with strategy-specific indicators"""
        plt.figure(figsize=(12, 8))
        
        # Create subplots based on strategy type
        if isinstance(self.strategy, RSIStrategy):
            # Main price plot
            ax1 = plt.subplot(2, 1, 1)
            ax1.plot(signals.index, signals['Close'], label='Price')
            
            # Plot buy/sell signals
            buy_signals = signals[signals['Signal'] == 1]
            sell_signals = signals[signals['Signal'] == -1]
            ax1.scatter(buy_signals.index, buy_signals['Close'], marker='^', color='g', label='Buy')
            ax1.scatter(sell_signals.index, sell_signals['Close'], marker='v', color='r', label='Sell')
            ax1.set_title(f'{symbol} Price and Signals')
            ax1.legend()
            
            # RSI plot
            ax2 = plt.subplot(2, 1, 2)
            ax2.plot(signals.index, signals['RSI'], label='RSI')
            ax2.axhline(y=70, color='r', linestyle='--')
            ax2.axhline(y=30, color='g', linestyle='--')
            ax2.set_title('RSI Indicator')
            ax2.legend()
            
        elif isinstance(self.strategy, MACDStrategy):
            # Main price plot
            ax1 = plt.subplot(2, 1, 1)
            ax1.plot(signals.index, signals['Close'], label='Price')
            
            # Plot buy/sell signals
            buy_signals = signals[signals['Signal'] == 1]
            sell_signals = signals[signals['Signal'] == -1]
            ax1.scatter(buy_signals.index, buy_signals['Close'], marker='^', color='g', label='Buy')
            ax1.scatter(sell_signals.index, sell_signals['Close'], marker='v', color='r', label='Sell')
            ax1.set_title(f'{symbol} Price and Signals')
            ax1.legend()
            
            # MACD plot
            ax2 = plt.subplot(2, 1, 2)
            ax2.plot(signals.index, signals['MACD'], label='MACD')
            ax2.plot(signals.index, signals['Signal_Line'], label='Signal Line')
            ax2.bar(signals.index, signals['MACD_Hist'], label='MACD Histogram')
            ax2.set_title('MACD Indicator')
            ax2.legend()
            
        elif isinstance(self.strategy, BollingerBandsStrategy):
            # Main price plot
            ax1 = plt.subplot(2, 1, 1)
            ax1.plot(signals.index, signals['Close'], label='Price')
            ax1.plot(signals.index, signals['BB_Middle'], label='Middle Band')
            ax1.plot(signals.index, signals['BB_Upper'], label='Upper Band')
            ax1.plot(signals.index, signals['BB_Lower'], label='Lower Band')
            
            # Plot buy/sell signals
            buy_signals = signals[signals['Signal'] == 1]
            sell_signals = signals[signals['Signal'] == -1]
            ax1.scatter(buy_signals.index, buy_signals['Close'], marker='^', color='g', label='Buy')
            ax1.scatter(sell_signals.index, sell_signals['Close'], marker='v', color='r', label='Sell')
            ax1.set_title(f'{symbol} Price and Signals')
            ax1.legend()
            
            # Bollinger Bands plot
            ax2 = plt.subplot(2, 1, 2)
            ax2.plot(signals.index, signals['BB_Width'], label='Band Width')
            ax2.set_title('Bollinger Bands Indicator')
            ax2.legend()
            
        elif isinstance(self.strategy, VWAPStrategy):
            # Main price plot
            ax1 = plt.subplot(2, 1, 1)
            ax1.plot(signals.index, signals['Close'], label='Price')
            ax1.plot(signals.index, signals['VWAP'], label='VWAP')
            
            # Plot buy/sell signals
            buy_signals = signals[signals['Signal'] == 1]
            sell_signals = signals[signals['Signal'] == -1]
            ax1.scatter(buy_signals.index, buy_signals['Close'], marker='^', color='g', label='Buy')
            ax1.scatter(sell_signals.index, sell_signals['Close'], marker='v', color='r', label='Sell')
            ax1.set_title(f'{symbol} Price and Signals')
            ax1.legend()
            
            # VWAP plot
            ax2 = plt.subplot(2, 1, 2)
            ax2.plot(signals.index, signals['VWAP'], label='VWAP')
            ax2.set_title('VWAP Indicator')
            ax2.legend()
            
        elif isinstance(self.strategy, SupportResistanceStrategy):
            # Main price plot
            ax1 = plt.subplot(2, 1, 1)
            ax1.plot(signals.index, signals['Close'], label='Price')
            
            # Plot buy/sell signals
            buy_signals = signals[signals['Signal'] == 1]
            sell_signals = signals[signals['Signal'] == -1]
            ax1.scatter(buy_signals.index, buy_signals['Close'], marker='^', color='g', label='Buy')
            ax1.scatter(sell_signals.index, sell_signals['Close'], marker='v', color='r', label='Sell')
            ax1.set_title(f'{symbol} Price and Signals')
            ax1.legend()
            
            # Support/Resistance plot
            ax2 = plt.subplot(2, 1, 2)
            ax2.plot(signals.index, signals['Support'], label='Support')
            ax2.plot(signals.index, signals['Resistance'], label='Resistance')
            ax2.set_title('Support/Resistance Indicator')
            ax2.legend()
            
        else:  # Moving Average strategy
            plt.plot(signals.index, signals['Close'], label='Price')
            if 'SMA_short' in signals.columns:
                plt.plot(signals.index, signals['SMA_short'], label='Short MA')
                plt.plot(signals.index, signals['SMA_long'], label='Long MA')
            
            # Plot buy/sell signals
            buy_signals = signals[signals['Signal'] == 1]
            sell_signals = signals[signals['Signal'] == -1]
            plt.scatter(buy_signals.index, buy_signals['Close'], marker='^', color='g', label='Buy')
            plt.scatter(sell_signals.index, sell_signals['Close'], marker='v', color='r', label='Sell')
            
            plt.title(f'{symbol} Trading Signals')
            plt.legend()
        
        plt.tight_layout()
        plt.savefig(f'{symbol}_trading_signals.png')
        plt.close()
    
    def get_portfolio_status(self):
        """Get current portfolio status"""
        total_value = self.capital
        for symbol, shares in self.positions.items():
            if shares > 0:
                try:
                    current_price = self.data_fetcher.get_live_price(symbol)
                    if current_price:
                        total_value += shares * current_price
                except Exception as e:
                    print(f"Error fetching live price for {symbol}: {str(e)}")
        
        return {
            'cash': self.capital,
            'positions': self.positions,
            'total_value': total_value
        }

if __name__ == "__main__":
    # Test with multiple tech stocks using RSI strategy
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'META']
    bot = TradingBot(symbols, strategy='RSI', initial_capital=10000)
    
    # Use 10 days of data with 1-hour intervals
    bot.run(period="10d", interval="1h")
    
    # Print final portfolio status
    portfolio = bot.get_portfolio_status()
    print("\nFinal Portfolio Status:")
    print(f"Cash: ${portfolio['cash']:.2f}")
    print("\nPositions:")
    for symbol, shares in portfolio['positions'].items():
        print(f"{symbol}: {shares} shares")
    print(f"\nTotal Portfolio Value: ${portfolio['total_value']:.2f}")
