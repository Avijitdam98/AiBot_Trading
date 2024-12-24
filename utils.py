import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

def calculate_returns(prices: pd.Series) -> float:
    """Calculate percentage returns"""
    return (prices[-1] / prices[0] - 1) * 100

def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.01) -> float:
    """Calculate Sharpe ratio"""
    excess_returns = returns - risk_free_rate
    return np.sqrt(252) * excess_returns.mean() / excess_returns.std()

def calculate_max_drawdown(prices: pd.Series) -> float:
    """Calculate maximum drawdown"""
    rolling_max = prices.expanding().max()
    drawdowns = prices / rolling_max - 1.0
    return drawdowns.min() * 100

def calculate_volatility(returns: pd.Series) -> float:
    """Calculate annualized volatility"""
    return returns.std() * np.sqrt(252) * 100

def calculate_beta(returns: pd.Series, market_returns: pd.Series) -> float:
    """Calculate beta relative to market"""
    covariance = returns.cov(market_returns)
    market_variance = market_returns.var()
    return covariance / market_variance

def calculate_risk_metrics(prices: pd.Series, market_prices: pd.Series = None) -> dict:
    """Calculate comprehensive risk metrics"""
    returns = prices.pct_change().dropna()
    
    metrics = {
        'total_return': calculate_returns(prices),
        'volatility': calculate_volatility(returns),
        'max_drawdown': calculate_max_drawdown(prices),
        'sharpe_ratio': calculate_sharpe_ratio(returns)
    }
    
    if market_prices is not None:
        market_returns = market_prices.pct_change().dropna()
        metrics['beta'] = calculate_beta(returns, market_returns)
    
    return metrics

def save_trade_log(trades: list, filename: str = 'trade_log.json'):
    """Save trade history to a JSON file"""
    with open(filename, 'w') as f:
        json.dump(trades, f, indent=4, default=str)

def load_trade_log(filename: str = 'trade_log.json') -> list:
    """Load trade history from a JSON file"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def calculate_trade_metrics(trades: list) -> dict:
    """Calculate comprehensive trading metrics"""
    if not trades:
        return {}
    
    total_trades = len(trades)
    profitable_trades = len([t for t in trades if t['type'] == 'SELL' and 
                           t.get('revenue', 0) > t.get('cost', 0)])
    
    # Calculate profit metrics
    total_profit = sum([t.get('revenue', 0) - t.get('cost', 0) 
                       for t in trades if t['type'] == 'SELL'])
    
    # Calculate average trade metrics
    avg_profit_per_trade = total_profit / total_trades if total_trades > 0 else 0
    win_rate = profitable_trades / total_trades if total_trades > 0 else 0
    
    return {
        'total_trades': total_trades,
        'profitable_trades': profitable_trades,
        'total_profit': total_profit,
        'avg_profit_per_trade': avg_profit_per_trade,
        'win_rate': win_rate
    }

def format_currency(amount: float) -> str:
    """Format amount as currency string"""
    return f"${amount:,.2f}"

def format_percentage(value: float) -> str:
    """Format value as percentage string"""
    return f"{value:.2f}%"
