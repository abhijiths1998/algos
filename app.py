import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import requests
from bs4 import BeautifulSoup

# Page config
st.set_page_config(page_title="BSE 200 Stock Recommender", layout="wide")

# Custom title
st.markdown("""
    <h1 style='text-align: center; color: #1f77b4;'>📈 BSE 200 - Weekly Stock Recommendations</h1>
    <p style='text-align: center; color: grey;'>Automatically updated BUY/SELL signals based on 1-week % change from Yahoo Finance</p>
""", unsafe_allow_html=True)

# Step 1: Scrape & validate BSE 200 tickers
@st.cache_data(show_spinner=False)
def fetch_bse_200():
    url = "https://www.screener.in/screens/1/the-bse-200-companies/"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    tickers = []
    company_links = soup.select("a[href^='/company/']")

    for link in company_links:
        symbol = link['href'].split("/")[2].upper() + ".BO"

        try:
            info = yf.Ticker(symbol).info
            if "longName" in info and info["regularMarketPrice"] is not None:
                tickers.append(symbol)
        except Exception:
            continue

        if len(tickers) >= 200:
            break

    return tickers

tickers = fetch_bse_200()
st.markdown(f"🔎 <b>{len(tickers)}</b> BSE stocks fetched from Screener.in and validated", unsafe_allow_html=True)

# Step 2: Adjust date to recent Friday if weekend
today = datetime.date.today()
if today.weekday() == 5:  # Saturday
    today -= datetime.timedelta(days=1)
elif today.weekday() == 6:  # Sunday
    today -= datetime.timedelta(days=2)

last_week = today - datetime.timedelta(days=7)
st.markdown(f"📅 Comparing prices from <b>{last_week}</b> to <b>{today}</b>", unsafe_allow_html=True)

# Step 3: Analyze stocks
buy_list, sell_list = [], []

with st.spinner("Analyzing weekly stock performance..."):
    for ticker in tickers:
        try:
            df = yf.download(ticker, start=last_week - datetime.timedelta(days=2), end=today, progress=False)
            if df.empty or len(df) < 2:
                continue

            last_close = round(df['Close'].iloc[0], 2)
            current_close = round(df['Close'].iloc[-1], 2)
            change = round(((current_close - last_close) / last_close) * 100, 2)
            emoji = "📉" if change < 0 else "📈"
            stock_data = (ticker, last_close, current_close, f"{emoji} {change}%")

            if change <= -5:
                buy_list.append(stock_data)
            elif change > 0:
                sell_list.append(stock_data)
        except Exception:
            continue

# Step 4: Summary cards
st.markdown("### 🧾 Summary")
colA, colB, colC = st.columns(3)
colA.metric("📦 Total Stocks Processed", f"{len(tickers)}")
colB.metric("🟢 BUY Signals", f"{len(buy_list)}")
colC.metric("🔴 SELL Signals", f"{len(sell_list)}")

# Step 5: Display recommendations
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🟢 BUY Recommendations (Dropped > 5%)")
    if buy_list:
        buy_df = pd.DataFrame(buy_list, columns=["Ticker", "Last Week Price", "Current Price", "% Change"])
        st.dataframe(buy_df.sort_values(by="% Change"), use_container_width=True)
    else:
        st.success("No BUY recommendations this week.")

with col2:
    st.markdown("### 🔴 SELL Recommendations (Price Increased)")
    if sell_list:
        sell_df = pd.DataFrame(sell_list, columns=["Ticker", "Last Week Price", "Current Price", "% Change"])
        st.dataframe(sell_df.sort_values(by="% Change", ascending=False), use_container_width=True)
    else:
        st.success("No SELL recommendations this week.")

# Footer
st.markdown("<hr><p style='text-align:center; color:grey;'>Built with ❤️ using Streamlit and Yahoo Finance</p>", unsafe_allow_html=True)
