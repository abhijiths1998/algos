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

# Step 1: Scrape BSE 200 tickers
@st.cache_data
def fetch_bse_200():
    url = "https://www.screener.in/screens/1/the-bse-200-companies/"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")

    stock_elements = soup.select("a[href*='/company/']")
    symbols = []
    for tag in stock_elements:
        name = tag.text.strip().upper().replace(" ", "")
        if name and name.isalpha():
            symbols.append(name + ".BO")
        if len(symbols) >= 200:
            break
    return list(set(symbols))[:200]

tickers = fetch_bse_200()

st.markdown(f"🔎 <b>{len(tickers)}</b> BSE stocks fetched from Screener.in", unsafe_allow_html=True)

# Set date range
today = datetime.date.today()
last_week = today - datetime.timedelta(days=7)
st.markdown(f"📅 Comparing prices from <b>{last_week}</b> to <b>{today}</b>", unsafe_allow_html=True)

buy_list, sell_list = [], []

# Step 2: Run analysis
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

        except Exception as e:
            continue

# Summary Cards
st.markdown("### 🧾 Summary")
colA, colB, colC = st.columns(3)
colA.metric("📦 Total Stocks Processed", f"{len(tickers)}")
colB.metric("🟢 BUY Signals", f"{len(buy_list)}")
colC.metric("🔴 SELL Signals", f"{len(sell_list)}")

# Step 3: Display recommendations
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
