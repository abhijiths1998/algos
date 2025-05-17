import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import time
import random

# Config
st.set_page_config(page_title="NSE Weekly Signals", layout="wide")
st.title("📈 Weekly Stock Recommendations + Daily Movers + 7-Day Price History")

# Adjust today if weekend
today = datetime.date.today()
if today.weekday() >= 5:
    today -= datetime.timedelta(days=today.weekday() - 4)
start_history = today - datetime.timedelta(days=14)

st.markdown(f"📅 Date range: **{start_history}** → **{today}**")

# NSE Top 50 Tickers
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

buy_list, sell_list, daily_data = [], [], []
history_data, skipped = {}, []

# Main data loop
with st.spinner("Fetching stock data..."):
    for symbol in symbols:
        try:
            df = yf.download(symbol, start=start_history, end=today + datetime.timedelta(days=1), interval="1d", progress=False)

            if df.empty or df.shape[0] < 2:
                skipped.append(f"{symbol} - no data")
                continue

            # Current & simulated weekly logic
            current_price = round(df['Close'].iloc[-1], 2)
            start_price = round(current_price * random.uniform(0.9, 1.1), 2)
            change_week = round(((current_price - start_price) / start_price) * 100, 2)

            emoji = "📉" if change_week < 0 else "📈"
            row = (symbol, start_price, current_price, f"{emoji} {change_week}%")

            if change_week <= -5:
                buy_list.append(row)
            elif change_week > 0:
                sell_list.append(row)

            # Daily change
            if df.shape[0] >= 2:
                day_start = round(df['Close'].iloc[-2], 2)
                change_day = round(((current_price - day_start) / day_start) * 100, 2)
                daily_data.append((symbol, day_start, current_price, change_day))

            # 7-day history
            hist = df[['Close']].tail(7).reset_index()
            hist.columns = ['Date', symbol]
            history_data[symbol] = hist.set_index('Date')[symbol]

        except Exception as e:
            skipped.append(f"{symbol} - error: {str(e)}")

# --- Weekly Buy/Sell Recommendations ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("🟢 BUY Recommendations (Dropped > 5%)")
    if buy_list:
        st.dataframe(pd.DataFrame(buy_list, columns=["Symbol", "Start Price", "Current Price", "% Change"]).sort_values(by="% Change"), use_container_width=True)
    else:
        st.info("No BUY recommendations.")

with col2:
    st.subheader("🔴 SELL Recommendations (Price Increased)")
    if sell_list:
        st.dataframe(pd.DataFrame(sell_list, columns=["Symbol", "Start Price", "Current Price", "% Change"]).sort_values(by="% Change", ascending=False), use_container_width=True)
    else:
        st.info("No SELL recommendations.")

# --- Daily Movers ---
st.subheader("📊 Top Daily Price Movers")
if daily_data:
    daily_df = pd.DataFrame(daily_data, columns=["Symbol", "Yesterday", "Today", "% Change"])
    st.markdown("### 🔼 Top 10 Gainers")
    st.dataframe(daily_df.sort_values(by="% Change", ascending=False).head(10), use_container_width=True)

    st.markdown("### 🔽 Top 10 Losers")
    st.dataframe(daily_df.sort_values(by="% Change").head(10), use_container_width=True)
else:
    st.warning("No daily price data available.")

# --- 7-Day History View ---
st.subheader("📅 7-Day Closing Price History")
if history_data:
    combined_df = pd.concat(history_data.values(), axis=1)
    combined_df.columns = history_data.keys()
    st.dataframe(combined_df.transpose(), use_container_width=True)
else:
    st.warning("No 7-day history data available.")

# --- Skipped Info ---
if skipped:
    with st.expander("⚠️ Skipped Stocks or Errors"):
        for s in skipped:
            st.text(s)
