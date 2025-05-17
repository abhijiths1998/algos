import streamlit as st
import yfinance as yf
import pandas as pd
import datetime

st.set_page_config(page_title="📊 NSE Last 7 Weeks Data", layout="wide")
st.title("📊 NSE 7-Week Stock Price History")

# Stock symbols
symbols = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "ICICIBANK.NS", "HDFCBANK.NS",
    "SBIN.NS", "ITC.NS", "BAJFINANCE.NS", "LT.NS", "AXISBANK.NS",
    "KOTAKBANK.NS", "ASIANPAINT.NS", "SUNPHARMA.NS", "WIPRO.NS", "NESTLEIND.NS",
    "TITAN.NS", "TECHM.NS", "MARUTI.NS", "POWERGRID.NS", "NTPC.NS",
    "ULTRACEMCO.NS", "HCLTECH.NS", "BHARTIARTL.NS", "ADANIENT.NS", "COALINDIA.NS",
    "JSWSTEEL.NS", "HINDUNILVR.NS", "CIPLA.NS", "BAJAJFINSV.NS", "INDUSINDBK.NS",
    "HDFCLIFE.NS", "TATACONSUM.NS", "BPCL.NS", "DIVISLAB.NS", "DRREDDY.NS",
    "EICHERMOT.NS", "GRASIM.NS", "HEROMOTOCO.NS", "M&M.NS", "SHREECEM.NS",
    "ONGC.NS", "BRITANNIA.NS", "SBILIFE.NS", "UPL.NS", "ICICIPRULI.NS",
    "HINDALCO.NS", "TATASTEEL.NS", "APOLLOHOSP.NS", "DMART.NS", "PIDILITIND.NS"
]

# Download data
st.info("Fetching data for the last 3 months from Yahoo Finance...")
df_stocks = yf.download(symbols, period="3mo", group_by='ticker', progress=False)

# Ensure datetime index
if not isinstance(df_stocks.index, pd.DatetimeIndex):
    st.warning("Index is not a DatetimeIndex. Cannot proceed.")
    st.stop()

# Filter last 7 weeks
latest_date = df_stocks.index.max()
start_date = latest_date - datetime.timedelta(weeks=7)
df_last_7_weeks = df_stocks[df_stocks.index >= start_date]

st.markdown(f"📅 Showing data from **{start_date.date()}** to **{latest_date.date()}**")

# View full multiindex DataFrame
st.subheader("🧾 Raw Stock Data (7 Weeks)")
st.dataframe(df_last_7_weeks)

# Show info like .info()
st.subheader("ℹ️ DataFrame Info")
buffer = []
df_last_7_weeks.info(buf=buffer)
st.text("\n".join(map(str, buffer)))

# Optional: View by stock
st.subheader("🔍 View Individual Stock (Close Prices)")
selected = st.selectbox("Choose a symbol", symbols)
try:
    df_single = df_last_7_weeks[selected]['Close'].dropna()
    st.line_chart(df_single)
    st.dataframe(df_single)
except Exception as e:
    st.warning(f"Could not retrieve data for {selected}: {e}")
