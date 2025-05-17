import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import time
import random

# Config
st.set_page_config(page_title="📊 NSE Stock Dashboard", layout="wide")
st.title("📈 NSE Stock Intelligence Dashboard")
st.markdown("""
This dashboard provides:
- ✅ Simulated **Weekly Buy/Sell recommendations**
- ✅ **Top 10 Daily Movers** (gainers/losers)
- ✅ **7-Day Price History**
- ✅ **Live price search tool**
- ✅ Export options (CSV)
""")

# Adjust dates
today = datetime.date.today()
if today.weekday() >= 5:
    today -= datetime.timedelta(days=today.weekday() - 4)
start_history = today - datetime.timedelta(days=14)

# Top 50 NSE Stocks (can be expanded)
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

# Caches
@st.cache_data(show_spinner=False)
def fetch_data(symbol, start, end):
    return yf.download(symbol, start=start, end=end, interval="1d", progress=False)

# Containers
buy_list, sell_list, daily_data, history_data, skipped = [], [], [], {}, []

# MAIN DATA LOOP
with st.spinner("🔄 Fetching data for NSE top stocks..."):
    for symbol in symbols:
        try:
            df = fetch_data(symbol, start_history, today + datetime.timedelta(days=1))
            if not isinstance(df, pd.DataFrame) or df.empty or df.shape[0] < 2:
                skipped.append(f"{symbol} - no valid data")
                continue

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

            time.sleep(0.1)

        except Exception as e:
            skipped.append(f"{symbol} - error: {e}")

# Weekly BUY/SELL
col1, col2 = st.columns(2)

with col1:
    st.subheader("🟢 BUY Recommendations (Dropped > 5%)")
    if buy_list:
        buy_df = pd.DataFrame(buy_list, columns=["Symbol", "Start Price", "Current Price", "% Change"])
        st.dataframe(buy_df.sort_values(by="% Change"), use_container_width=True)
        st.download_button("⬇ Download BUY list", buy_df.to_csv(index=False), "buy_recommendations.csv")
    else:
        st.info("No BUY recommendations.")

with col2:
    st.subheader("🔴 SELL Recommendations (Price Increased)")
    if sell_list:
        sell_df = pd.DataFrame(sell_list, columns=["Symbol", "Start Price", "Current Price", "% Change"])
        st.dataframe(sell_df.sort_values(by="% Change", ascending=False), use_container_width=True)
        st.download_button("⬇ Download SELL list", sell_df.to_csv(index=False), "sell_recommendations.csv")
    else:
        st.info("No SELL recommendations.")

# Daily movers
st.subheader("📊 Top Daily Price Movers")
if daily_data:
    daily_df = pd.DataFrame(daily_data, columns=["Symbol", "Yesterday", "Today", "% Change"])
    st.markdown("### 🔼 Top 10 Gainers")
    st.dataframe(daily_df.sort_values(by="% Change", ascending=False).head(10), use_container_width=True)

    st.markdown("### 🔽 Top 10 Losers")
    st.dataframe(daily_df.sort_values(by="% Change").head(10), use_container_width=True)
else:
    st.warning("No daily price data available.")

# 7-day price history
st.subheader("📅 7-Day Closing Price History")
if history_data:
    history_df = pd.concat(history_data.values(), axis=1)
    history_df.columns = history_data.keys()
    st.dataframe(history_df.transpose(), use_container_width=True)
    st.download_button("⬇ Download 7-Day History", history_df.transpose().to_csv(), "price_history.csv")
else:
    st.warning("No historical data available.")

# Live price checker
st.subheader("🔍 Live Stock Price Checker")
user_input = st.text_input("Enter NSE Symbol (e.g., RELIANCE.NS, TCS.NS):")
if user_input:
    try:
        live = yf.Ticker(user_input)
        live_price = live.history(period="1d")
        if not live_price.empty:
            st.success(f"✅ Current Price for {user_input}: ₹{round(live_price['Close'].iloc[-1], 2)}")
        else:
            st.error("Symbol found but no current price available.")
    except Exception as e:
        st.error(f"Failed to fetch data for {user_input}: {e}")

# Skipped info
if skipped:
    with st.expander("⚠️ Skipped Stocks / Errors"):
        for item in skipped:
            st.text(item)
