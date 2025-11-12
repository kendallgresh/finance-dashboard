import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

# Dashboard title
st.title('📈 Real-Time Finance Dashboard')
st.write('Built with Python in 45 minutes!')

# Sidebar for user input
st.sidebar.header('Settings')
ticker = st.sidebar.text_input('Enter Stock Ticker', 'AAPL').upper()
period = st.sidebar.selectbox('Time Period', ['1mo', '3mo', '6mo', '1y'])

# Get the data
@st.cache_data(ttl=300)
def load_data(ticker, period):
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period=period)
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# Load data
with st.spinner(f'Loading {ticker} data...'):
    data = load_data(ticker, period)

# Check if data exists and has the right columns
if data.empty:
    st.error(f"❌ Could not load data for {ticker}. Try: AAPL, MSFT, GOOGL, TSLA, AMZN")
    st.stop()

if len(data) < 2:
    st.error(f"❌ Not enough data for {ticker}. Try a different time period.")
    st.stop()

# Display current metrics
st.subheader(f'{ticker} Overview')

current_price = data['Close'].iloc[-1]
previous_price = data['Close'].iloc[-2]
change = current_price - previous_price
change_pct = (change / previous_price) * 100

col1, col2, col3 = st.columns(3)
col1.metric("Current Price", f"${current_price:.2f}", f"{change:.2f}")
col2.metric("Daily Change", f"{change_pct:.2f}%")
col3.metric("Volume", f"{int(data['Volume'].iloc[-1]):,}")

# Price History Chart
st.subheader('Price History')
fig = go.Figure()

# Add closing price line
fig.add_trace(go.Scatter(
    x=data.index,
    y=data['Close'],
    name='Close Price',
    line=dict(color='#00D9FF', width=2)
))

# Add 7-day moving average
if len(data) >= 7:
    ma7 = data['Close'].rolling(window=7).mean()
    fig.add_trace(go.Scatter(
        x=data.index,
        y=ma7,
        name='7-Day MA',
        line=dict(color='#FF6B35', width=2, dash='dash')
    ))

fig.update_layout(
    xaxis_title='Date',
    yaxis_title='Price ($)',
    hovermode='x unified',
    template='plotly_dark',
    height=400
)

st.plotly_chart(fig, use_container_width=True)

# Daily Returns Chart
st.subheader('Daily Returns (%)')
daily_returns = data['Close'].pct_change() * 100

# Create color for bars (green for positive, red for negative)
colors = ['#00FF00' if x > 0 else '#FF0000' for x in daily_returns]

fig2 = go.Figure()
fig2.add_trace(go.Bar(
    x=data.index,
    y=daily_returns,
    name='Daily Return',
    marker_color=colors
))

fig2.update_layout(
    xaxis_title='Date',
    yaxis_title='Return (%)',
    template='plotly_dark',
    height=400
)

st.plotly_chart(fig2, use_container_width=True)

# Investment Calculator
st.subheader('💰 Investment Calculator')
investment = st.slider('Initial Investment ($)', 100, 10000, 1000, step=100)

first_price = data['Close'].iloc[0]
shares = investment / first_price
current_value = shares * current_price
profit = current_value - investment
profit_pct = (profit / investment) * 100

col1, col2 = st.columns(2)

with col1:
    st.metric("Shares Purchased", f"{shares:.4f}")
    st.metric("Initial Investment", f"${investment:,.2f}")

with col2:
    st.metric("Current Value", f"${current_value:,.2f}")
    st.metric("Profit/Loss", f"${profit:,.2f}", f"{profit_pct:.2f}%")

if profit > 0:
    st.success(f"📈 You would have made ${profit:,.2f} ({profit_pct:.2f}%)")
else:
    st.error(f"📉 You would have lost ${abs(profit):,.2f} ({profit_pct:.2f}%)")

# Key Insights
st.subheader('🧠 Key Insights')

# Clean the daily returns (remove NaN)
clean_returns = daily_returns.dropna()

if len(clean_returns) > 0:
    volatility = clean_returns.std()
    avg_return = clean_returns.mean()
    max_gain = clean_returns.max()
    max_loss = clean_returns.min()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Volatility (Std Dev)", f"{volatility:.2f}%")
        st.metric("Average Daily Return", f"{avg_return:.2f}%")
    
    with col2:
        st.metric("Best Day", f"+{max_gain:.2f}%")
        st.metric("Worst Day", f"{max_loss:.2f}%")
    
    # Risk assessment
    st.write("---")
    if volatility > 4:
        st.warning("⚠️ **High Volatility**: This stock has significant price swings. Higher risk, higher potential reward.")
    elif volatility > 2:
        st.info("📊 **Moderate Volatility**: This stock has average price fluctuations. Balanced risk-reward.")
    else:
        st.success("✅ **Low Volatility**: This stock has stable price movements. Lower risk, lower potential reward.")

# Statistics Summary
with st.expander('📊 View Detailed Statistics'):
    st.write("**Price Statistics:**")
    stats_df = pd.DataFrame({
        'Metric': ['Highest Price', 'Lowest Price', 'Average Price', 'Current Price', 'Total Return'],
        'Value': [
            f"${data['Close'].max():.2f}",
            f"${data['Close'].min():.2f}",
            f"${data['Close'].mean():.2f}",
            f"${current_price:.2f}",
            f"{((current_price - first_price) / first_price * 100):.2f}%"
        ]
    })
    st.table(stats_df)

# Raw Data
with st.expander('📈 View Raw Data'):
    st.dataframe(data, use_container_width=True)

# Footer
st.markdown("---")
st.caption(f"Data provided by Yahoo Finance via yfinance library • Last updated: {data.index[-1].strftime('%Y-%m-%d %H:%M')}")



