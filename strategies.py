import pandas as pd
import numpy as np

class TradingStrategy:
    def __init__(self):
        self.position = 0  # 1 for long, -1 for short, 0 for neutral
        
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals. To be implemented by specific strategies."""
        raise NotImplementedError

class MovingAverageCrossover(TradingStrategy):
    def __init__(self, short_window: int = 20, long_window: int = 50):
        super().__init__()
        self.short_window = short_window
        self.long_window = long_window
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals based on Moving Average Crossover strategy
        
        Args:
            data (pd.DataFrame): DataFrame with 'Close' prices
            
        Returns:
            pd.DataFrame: DataFrame with signals
        """
        signals = data.copy()
        signals['SMA_short'] = signals['Close'].rolling(window=self.short_window).mean()
        signals['SMA_long'] = signals['Close'].rolling(window=self.long_window).mean()
        
        # Generate signals
        signals['Signal'] = 0
        signals.loc[signals['SMA_short'] > signals['SMA_long'], 'Signal'] = 1
        signals.loc[signals['SMA_short'] < signals['SMA_long'], 'Signal'] = -1
        
        return signals

class RSIStrategy(TradingStrategy):
    def __init__(self, period: int = 10, overbought: int = 65, oversold: int = 35):
        super().__init__()
        self.period = period
        self.overbought = overbought
        self.oversold = oversold
    
    def calculate_rsi(self, data: pd.Series) -> pd.Series:
        """Calculate RSI indicator"""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals based on RSI strategy"""
        signals = data.copy()
        signals['RSI'] = self.calculate_rsi(signals['Close'])
        
        # Generate signals
        signals['Signal'] = 0
        signals.loc[signals['RSI'] < self.oversold, 'Signal'] = 1  # Oversold - Buy
        signals.loc[signals['RSI'] > self.overbought, 'Signal'] = -1  # Overbought - Sell
        
        return signals

class MACDStrategy(TradingStrategy):
    def __init__(self, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9):
        super().__init__()
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
    
    def calculate_macd(self, data: pd.Series) -> tuple:
        """Calculate MACD line and signal line"""
        exp1 = data.ewm(span=self.fast_period, adjust=False).mean()
        exp2 = data.ewm(span=self.slow_period, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=self.signal_period, adjust=False).mean()
        return macd, signal
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals based on MACD crossovers"""
        signals = data.copy()
        
        # Calculate MACD and signal line
        signals['MACD'], signals['Signal_Line'] = self.calculate_macd(signals['Close'])
        signals['MACD_Hist'] = signals['MACD'] - signals['Signal_Line']
        
        # Generate signals
        signals['Signal'] = 0
        # Buy when MACD crosses above signal line
        signals.loc[signals['MACD_Hist'] > 0, 'Signal'] = 1
        # Sell when MACD crosses below signal line
        signals.loc[signals['MACD_Hist'] < 0, 'Signal'] = -1
        
        return signals

class BollingerBandsStrategy(TradingStrategy):
    def __init__(self, window: int = 20, num_std: float = 2.0):
        super().__init__()
        self.window = window
        self.num_std = num_std
    
    def calculate_bollinger_bands(self, data: pd.Series) -> tuple:
        """Calculate Bollinger Bands"""
        middle_band = data.rolling(window=self.window).mean()
        std = data.rolling(window=self.window).std()
        upper_band = middle_band + (std * self.num_std)
        lower_band = middle_band - (std * self.num_std)
        return upper_band, middle_band, lower_band
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals based on Bollinger Bands"""
        signals = data.copy()
        
        # Calculate Bollinger Bands
        signals['Upper_Band'], signals['Middle_Band'], signals['Lower_Band'] = \
            self.calculate_bollinger_bands(signals['Close'])
        
        # Generate signals
        signals['Signal'] = 0
        # Buy when price crosses below lower band
        signals.loc[signals['Close'] < signals['Lower_Band'], 'Signal'] = 1
        # Sell when price crosses above upper band
        signals.loc[signals['Close'] > signals['Upper_Band'], 'Signal'] = -1
        
        return signals

class VWAPStrategy(TradingStrategy):
    def __init__(self, window: int = 14):
        super().__init__()
        self.window = window
    
    def calculate_vwap(self, data: pd.DataFrame) -> pd.Series:
        """Calculate VWAP"""
        typical_price = (data['High'] + data['Low'] + data['Close']) / 3
        vwap = (typical_price * data['Volume']).rolling(window=self.window).sum() / \
               data['Volume'].rolling(window=self.window).sum()
        return vwap
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals based on VWAP"""
        signals = data.copy()
        
        # Calculate VWAP
        signals['VWAP'] = self.calculate_vwap(signals)
        
        # Generate signals
        signals['Signal'] = 0
        # Buy when price crosses above VWAP
        signals.loc[signals['Close'] > signals['VWAP'], 'Signal'] = 1
        # Sell when price crosses below VWAP
        signals.loc[signals['Close'] < signals['VWAP'], 'Signal'] = -1
        
        return signals

class SupportResistanceStrategy(TradingStrategy):
    def __init__(self, window: int = 20, num_touches: int = 2):
        super().__init__()
        self.window = window
        self.num_touches = num_touches
    
    def find_support_resistance(self, data: pd.DataFrame) -> tuple:
        """Find support and resistance levels"""
        highs = data['High'].rolling(window=self.window, center=True).max()
        lows = data['Low'].rolling(window=self.window, center=True).min()
        
        # Count touches of price to levels
        resistance_touches = (abs(data['High'] - highs) < (highs * 0.01)).rolling(window=self.window).sum()
        support_touches = (abs(data['Low'] - lows) < (lows * 0.01)).rolling(window=self.window).sum()
        
        return highs[resistance_touches >= self.num_touches], lows[support_touches >= self.num_touches]
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals based on Support/Resistance levels"""
        signals = data.copy()
        
        # Find support and resistance levels
        resistance, support = self.find_support_resistance(signals)
        signals['Resistance'] = resistance
        signals['Support'] = support
        
        # Generate signals
        signals['Signal'] = 0
        # Buy near support
        signals.loc[signals['Close'] < signals['Support'] * 1.02, 'Signal'] = 1
        # Sell near resistance
        signals.loc[signals['Close'] > signals['Resistance'] * 0.98, 'Signal'] = -1
        
        return signals
