import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page config
st.set_page_config(
    page_title="Trading Bot",
    layout="wide"
)

# Title
st.title("Trading Bot Dashboard")

# Sidebar
st.sidebar.title("Configuration")

# Stock selection
symbol = st.sidebar.text_input("Enter Stock Symbol", "AAPL")
days = st.sidebar.slider("Days of historical data", 30, 365, 180)

# Date range
end_date = datetime.now()
start_date = end_date - timedelta(days=days)

if st.sidebar.button("Analyze Stock"):
    try:
        # Fetch data
        data = yf.download(symbol, start=start_date, end=end_date)
        
        if data.empty:
            st.error(f"No data found for {symbol}")
        else:
            # Display basic info
            st.subheader(f"{symbol} Stock Analysis")
            
            # Create price chart
            fig = go.Figure(data=[go.Candlestick(x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'])])
            
            fig.update_layout(
                title=f"{symbol} Stock Price",
                yaxis_title="Price",
                xaxis_title="Date"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Display metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                current_price = data['Close'].iloc[-1]
                st.metric("Current Price", f"${current_price:.2f}")
            
            with col2:
                price_change = data['Close'].iloc[-1] - data['Close'].iloc[0]
                st.metric("Price Change", f"${price_change:.2f}")
            
            with col3:
                returns = ((data['Close'].iloc[-1] / data['Close'].iloc[0]) - 1) * 100
                st.metric("Total Return", f"{returns:.2f}%")
            
            # Display recent data
            st.subheader("Recent Data")
            st.dataframe(data.tail())
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
else:
    st.info("👈 Enter a stock symbol and click 'Analyze Stock' to begin")
