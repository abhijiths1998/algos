import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import time
import random

# Page setup
st.set_page_config(page_title="Stock Signal Simulator", layout="wide")
st.title("📈 Simulated Weekly Stock Recommendations")
st.markdown("This app simulates 1-week price change using random variation from current price for selected NSE stocks.")

# Adjust for weekends
today = datetime.date.today()
if today.weekday() >= 5:
    today -= datetime.timedelta(days=today.weekday() - 4)

st.markdown(f"📅 Today (adjusted): **{today}**")

# Expanded NSE tickers list (Top ~50)
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

buy_list = []
sell_list = []
skipped = []

with st.spinner("📊 Fetching current prices and simulating weekly change..."):
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d")

            if data.empty:
                skipped.append(symbol)
                continue

            current_price = round(data['Close'].iloc[-1], 2)

            # Simulate a 1-week-ago price
            start_price = round(current_price * random.uniform(0.9, 1.1), 2)
            change = round(((current_price - start_price) / start_price) * 100, 2)
            emoji = "📉" if change < 0 else "📈"

            result = (symbol, start_price, current_price, f"{emoji} {change}%")

            if change <= -5:
                buy_list.append(result)
            elif change > 0:
                sell_list.append(result)

            time.sleep(0.2)

        except Exception as e:
            skipped.append(f"{symbol} (error: {e})")
            continue

# Layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("🟢 BUY Recommendations (Dropped > 5%)")
    if buy_list:
        buy_df = pd.DataFrame(buy_list, columns=["Symbol", "Start Price", "Current Price", "% Change"])
        st.dataframe(buy_df.sort_values(by="% Change"), use_container_width=True)
    else:
        st.info("No BUY signals.")

with col2:
    st.subheader("🔴 SELL Recommendations (Price Increased)")
    if sell_list:
        sell_df = pd.DataFrame(sell_list, columns=["Symbol", "Start Price", "Current Price", "% Change"])
        st.dataframe(sell_df.sort_values(by="% Change", ascending=False), use_container_width=True)
    else:
        st.info("No SELL signals.")

# Show skipped
if skipped:
    with st.expander("⚠️ Skipped Stocks"):
        for s in skipped:
            st.text(s)
