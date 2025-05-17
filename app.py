import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import time

# Page config
st.set_page_config(page_title="NSE Top 100 Recommender", layout="wide")
st.title("📈 NSE Top 100 - Weekly Stock Recommendations")
st.markdown("Automatically updated BUY/SELL signals based on *real 7-day price change* using Yahoo Finance")

# Adjust 'today' to most recent trading day if weekend
today = datetime.date.today()
if today.weekday() >= 5:
    today -= datetime.timedelta(days=today.weekday() - 4)

start_date = today - datetime.timedelta(days=7)
st.markdown(f"📅 Comparing prices from **{start_date}** to **{today}**")

# Top NSE tickers (sample of 20 — replace with full 100 as needed)
symbols = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "ICICIBANK.NS", "HDFCBANK.NS",
    "SBIN.NS", "ITC.NS", "BAJFINANCE.NS", "LT.NS", "AXISBANK.NS",
    "KOTAKBANK.NS", "ASIANPAINT.NS", "SUNPHARMA.NS", "WIPRO.NS", "NESTLEIND.NS",
    "TITAN.NS", "TECHM.NS", "MARUTI.NS", "POWERGRID.NS", "NTPC.NS"
]

buy_list = []
sell_list = []
skipped = []

with st.spinner("Fetching and analyzing price data..."):
    for symbol in symbols:
        try:
            data = yf.download(symbol, start=start_date, end=today, progress=False)

            if data is None or data.shape[0] < 2:
                skipped.append((symbol, "No price data"))
                continue

            start_price = round(data['Close'].iloc[0], 2)
            current_price = round(data['Close'].iloc[-1], 2)
            change = round(((current_price - start_price) / start_price) * 100, 2)
            emoji = "📉" if change < 0 else "📈"

            record = (symbol, start_price, current_price, f"{emoji} {change}%")

            if change <= -5:
                buy_list.append(record)
            elif change > 0:
                sell_list.append(record)

            time.sleep(0.2)

        except Exception as e:
            skipped.append((symbol, str(e)))
            continue

# Layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("🟢 BUY Recommendations (Dropped > 5%)")
    if buy_list:
        df_buy = pd.DataFrame(buy_list, columns=["Symbol", "Start Price", "Current Price", "% Change"])
        st.dataframe(df_buy.sort_values(by="% Change"), use_container_width=True)
    else:
        st.success("No BUY signals found.")

with col2:
    st.subheader("🔴 SELL Recommendations (Price Increased)")
    if sell_list:
        df_sell = pd.DataFrame(sell_list, columns=["Symbol", "Start Price", "Current Price", "% Change"])
        st.dataframe(df_sell.sort_values(by="% Change", ascending=False), use_container_width=True)
    else:
        st.success("No SELL signals found.")

# Skipped
if skipped:
    with st.expander("⚠️ Skipped Stocks"):
        for symbol, reason in skipped:
            st.write(f"{symbol}: {reason}")
