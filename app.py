import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Real-Time Stock Dashboard",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Real-Time Stock Market Dashboard")

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.header("Dashboard Settings")

stocks = [
    "AAPL", "MSFT", "GOOGL", "AMZN",
    "TSLA", "META", "NFLX", "NVDA"
]

selected_stock = st.sidebar.selectbox(
    "Select Stock",
    stocks
)

period = st.sidebar.selectbox(
    "Select Time Period",
  ["1mo", "3mo", "6mo", "1y"]
)

refresh_rate = st.sidebar.slider(
    "Auto Refresh (seconds)",
    10,
    120,
    30
)

# -----------------------------
# Fetch Data
# -----------------------------
@st.cache_data(ttl=60)
def load_data(ticker, period):
    stock = yf.Ticker(ticker)
    df = stock.history(period=period)
    info = stock.info
    return df, info

df, info = load_data(selected_stock, period)

if df.empty:
    st.error("No data available.")
    st.stop()
if len(df) < 1:
    st.error("Insufficient stock data.")
    st.stop()
# -----------------------------
# Moving Averages
# -----------------------------
df["MA20"] = df["Close"].rolling(20).mean()
df["MA50"] = df["Close"].rolling(50).mean()

# -----------------------------
# Metrics
# -----------------------------
latest_close = df["Close"].iloc[-1]

if len(df) > 1:
    previous_close = df["Close"].iloc[-2]
    change = latest_close - previous_close
    percent_change = (change / previous_close) * 100
else:
    previous_close = latest_close
    change = 0
    percent_change = 0

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Current Price",
    f"${latest_close:.2f}",
    f"{percent_change:.2f}%"
)

col2.metric(
    "Volume",
    f"{int(df['Volume'].iloc[-1]):,}"
)

col3.metric(
    "Market Cap",
    f"${info.get('marketCap', 0):,}"
)

col4.metric(
    "P/E Ratio",
    round(info.get("trailingPE", 0), 2)
)

# -----------------------------
# Candlestick Chart
# -----------------------------
fig = make_subplots(
    rows=2,
    cols=1,
    shared_xaxes=True,
    vertical_spacing=0.05,
    row_heights=[0.7, 0.3]
)

fig.add_trace(
    go.Candlestick(
        x=df.index,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        name="Price"
    ),
    row=1,
    col=1
)

fig.add_trace(
    go.Scatter(
        x=df.index,
        y=df["MA20"],
        mode="lines",
        name="MA20"
    ),
    row=1,
    col=1
)

fig.add_trace(
    go.Scatter(
        x=df.index,
        y=df["MA50"],
        mode="lines",
        name="MA50"
    ),
    row=1,
    col=1
)

fig.add_trace(
    go.Bar(
        x=df.index,
        y=df["Volume"],
        name="Volume"
    ),
    row=2,
    col=1
)

fig.update_layout(
    title=f"{selected_stock} Stock Analysis",
    xaxis_rangeslider_visible=False,
    height=700
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Company Information
# -----------------------------
st.subheader("Company Information")

company_data = {
    "Company": info.get("longName"),
    "Sector": info.get("sector"),
    "Industry": info.get("industry"),
    "Country": info.get("country"),
    "Website": info.get("website")
}

st.table(pd.DataFrame(company_data.items(),
                      columns=["Field", "Value"]))

# -----------------------------
# Historical Data Table
# -----------------------------
st.subheader("Historical Data")

display_df = df.reset_index()
display_df = display_df.round(2)

st.dataframe(
    display_df,
    use_container_width=True
)

# -----------------------------
# Auto Refresh
# -----------------------------
st.caption(
    f"Dashboard refreshes every {refresh_rate} seconds"
)

st.markdown(
    f"""
    <meta http-equiv="refresh" content="{refresh_rate}">
    """,
    unsafe_allow_html=True
)