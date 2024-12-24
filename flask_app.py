from flask import Flask, render_template_string, request
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import json
from datetime import datetime, timedelta
import numpy as np

app = Flask(__name__)

def calculate_signals(data):
    # Calculate technical indicators
    data['SMA20'] = data['Close'].rolling(window=20).mean()
    data['SMA50'] = data['Close'].rolling(window=50).mean()
    
    # Generate trading signals
    signals = []
    for i in range(1, len(data)):
        if data['SMA20'].iloc[i] > data['SMA50'].iloc[i] and data['SMA20'].iloc[i-1] <= data['SMA50'].iloc[i-1]:
            signals.append('BUY')
        elif data['SMA20'].iloc[i] < data['SMA50'].iloc[i] and data['SMA20'].iloc[i-1] >= data['SMA50'].iloc[i-1]:
            signals.append('SELL')
        else:
            signals.append('HOLD')
    
    signals.insert(0, 'HOLD')  # Add HOLD for the first day
    return signals

def create_chart(data, symbol):
    # Create candlestick chart
    fig = go.Figure(data=[go.Candlestick(x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name='Price')])
    
    # Add moving averages
    fig.add_trace(go.Scatter(x=data.index, y=data['SMA20'],
                            line=dict(color='blue', width=1),
                            name='20-day MA'))
    fig.add_trace(go.Scatter(x=data.index, y=data['SMA50'],
                            line=dict(color='orange', width=1),
                            name='50-day MA'))
    
    # Add buy/sell markers
    buy_signals = data[data['Signal'] == 'BUY'].index
    sell_signals = data[data['Signal'] == 'SELL'].index
    
    fig.add_trace(go.Scatter(x=buy_signals, y=data.loc[buy_signals, 'Low'] * 0.99,
                            mode='markers',
                            marker=dict(symbol='triangle-up', size=15, color='green'),
                            name='Buy Signal'))
    
    fig.add_trace(go.Scatter(x=sell_signals, y=data.loc[sell_signals, 'High'] * 1.01,
                            mode='markers',
                            marker=dict(symbol='triangle-down', size=15, color='red'),
                            name='Sell Signal'))
    
    fig.update_layout(
        title=f'{symbol} Price Chart with Trading Signals',
        yaxis_title='Price',
        xaxis_title='Date',
        template='plotly_white'
    )
    
    return json.dumps(fig.to_dict())

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>AI Trading Bot Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 20px;
            background-color: #f5f5f5;
        }
        .container { 
            max-width: 1200px; 
            margin: auto;
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        .search-box {
            margin: 20px 0;
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #ddd;
            width: 200px;
            font-size: 16px;
        }
        .analyze-btn {
            background-color: #007bff;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }
        .analyze-btn:hover {
            background-color: #0056b3;
        }
        .chart-container {
            margin-top: 20px;
            padding: 20px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .metric-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        .metric-value {
            font-size: 24px;
            font-weight: bold;
            margin: 10px 0;
        }
        .positive { color: #28a745; }
        .negative { color: #dc3545; }
        .signal-box {
            background: #e9ecef;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
            text-align: center;
            font-size: 18px;
            font-weight: bold;
        }
        .signal-BUY { color: #28a745; }
        .signal-SELL { color: #dc3545; }
        .signal-HOLD { color: #6c757d; }
    </style>
</head>
<body>
    <div class="container">
        <h1>AI Trading Bot Dashboard</h1>
        
        <form method="GET" style="display: flex; gap: 10px; align-items: center;">
            <input type="text" name="symbol" class="search-box" 
                   placeholder="Enter stock symbol" 
                   value="{{ symbol if symbol else '' }}"
                   required>
            <button type="submit" class="analyze-btn">Analyze</button>
        </form>

        {% if error %}
        <div class="error-message">{{ error }}</div>
        {% endif %}

        {% if stock_data %}
        <div class="signal-box signal-{{ latest_signal }}">
            Current Signal: {{ latest_signal }}
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <h3>Current Price</h3>
                <div class="metric-value">${{ "%.2f"|format(stock_data.current_price) }}</div>
            </div>
            <div class="metric-card">
                <h3>Price Change</h3>
                <div class="metric-value {{ 'positive' if stock_data.price_change >= 0 else 'negative' }}">
                    {{ '+' if stock_data.price_change >= 0 else '' }}${{ "%.2f"|format(stock_data.price_change) }}
                </div>
            </div>
            <div class="metric-card">
                <h3>Return</h3>
                <div class="metric-value {{ 'positive' if stock_data.returns >= 0 else 'negative' }}">
                    {{ '+' if stock_data.returns >= 0 else '' }}{{ "%.2f"|format(stock_data.returns) }}%
                </div>
            </div>
            <div class="metric-card">
                <h3>Volume</h3>
                <div class="metric-value">{{ "{:,}".format(stock_data.volume) }}</div>
            </div>
        </div>

        <div class="chart-container">
            <div id="chart"></div>
        </div>
        
        <script>
            var chartData = {{ chart_data | safe }};
            Plotly.newPlot('chart', chartData.data, chartData.layout);
        </script>
        {% endif %}
    </div>

    <script>
        document.querySelector('input[name="symbol"]').addEventListener('input', function(e) {
            this.value = this.value.toUpperCase();
        });
    </script>
</body>
</html>
'''

def get_stock_data(symbol):
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)  # Get 90 days of data for better analysis
        
        data = yf.download(symbol, start=start_date, end=end_date, progress=False)
        
        if data.empty:
            return None, None, None, "Invalid stock symbol. Please check and try again."
        
        # Calculate trading signals
        signals = calculate_signals(data)
        data['Signal'] = signals
        latest_signal = signals[-1]
        
        stock_data = {
            'current_price': data['Close'].iloc[-1],
            'price_change': data['Close'].iloc[-1] - data['Close'].iloc[0],
            'returns': ((data['Close'].iloc[-1] / data['Close'].iloc[0]) - 1) * 100,
            'volume': int(data['Volume'].iloc[-1])
        }
        
        # Create interactive chart
        chart_data = create_chart(data, symbol)
        
        return stock_data, chart_data, latest_signal, None
            
    except Exception as e:
        print(f"Error fetching {symbol}: {str(e)}")
        return None, None, None, "Error fetching data. Please try again."

@app.route('/')
def index():
    symbol = request.args.get('symbol', '').upper().strip()
    
    if symbol:
        stock_data, chart_data, latest_signal, error = get_stock_data(symbol)
        return render_template_string(HTML_TEMPLATE,
                                   symbol=symbol,
                                   stock_data=stock_data,
                                   chart_data=chart_data,
                                   latest_signal=latest_signal,
                                   error=error)
    
    return render_template_string(HTML_TEMPLATE,
                                symbol='',
                                stock_data=None,
                                chart_data=None,
                                latest_signal=None,
                                error=None)

if __name__ == '__main__':
    print("Starting AI Trading Bot...")
    print("Access the dashboard at http://localhost:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)
