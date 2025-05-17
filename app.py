import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import time
import random

# Streamlit config
st.set_page_config(page_title="NSE Mini Signal App", layout="wide")
st.title("📈 NSE Stock Signal Dashboard")
st.markdown("""
This dashboard gives you:
- ✅ Simulated **Buy/Sell signals** based on random historical price shifts
- ✅ Choose how many stocks to scan (top N)
- ✅ Search for specific stock symbol and get weekly price change & company financials
""")

# Today's date (adjust if weekend)
today = datetime.date.today()
if today.weekday() >= 5:
    today -= datetime.timedelta(days=today.weekday() - 4)
start_week = today - datetime.timedelta(days=7)

st.markdown(f"📅 Today (adjusted): **{today}**")

# Select number of top stocks to process
count = st.number_input("🔢 Enter how many top NSE stocks to scan (up to 50)", min_value=1, max_value=50, value=10)

# Input symbol for search
search_symbol = st.text_input("🔍 Enter NSE symbol to get detailed info (e.g. RELIANCE.NS)")

# Top NSE 50 stocks (static but can later be fetched dynamically)
symbols_all = [
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
symbols = symbols_all[:count]

buy_list = []
sell_list = []
skipped = []

with st.spinner("🔄 Fetching stock prices..."):
    for symbol in symbols:
        try:
            df = yf.download(symbol, period="1d")
            if not isinstance(df, pd.DataFrame) or df.empty:
                skipped.append(f"{symbol} - no data")
                continue

            current_price = round(df['Close'].iloc[-1], 2)
            start_price = round(current_price * random.uniform(0.9, 1.1), 2)
            change = round(((current_price - start_price) / start_price) * 100, 2)
            emoji = "📉" if change < 0 else "📈"

            row = (symbol, start_price, current_price, f"{emoji} {change}%")
            if change <= -5:
                buy_list.append(row)
            elif change > 0:
                sell_list.append(row)

            time.sleep(0.1)

        except Exception as e:
            skipped.append(f"{symbol} - error: {e}")

# Weekly Buy/Sell Output
col1, col2 = st.columns(2)

with col1:
    st.subheader("🟢 BUY Recommendations")
    if buy_list:
        df_buy = pd.DataFrame(buy_list, columns=["Symbol", "Start Price", "Current Price", "% Change"])
        st.dataframe(df_buy.sort_values(by="% Change"), use_container_width=True)
    else:
        st.info("No BUY recommendations.")

with col2:
    st.subheader("🔴 SELL Recommendations")
    if sell_list:
        df_sell = pd.DataFrame(sell_list, columns=["Symbol", "Start Price", "Current Price", "% Change"])
        st.dataframe(df_sell.sort_values(by="% Change", ascending=False), use_container_width=True)
    else:
        st.info("No SELL recommendations.")

# Specific symbol detail view
if search_symbol:
    st.subheader(f"🔍 Detailed Info for {search_symbol.upper()}")
    try:
        data = yf.download(search_symbol, start=start_week, end=today + datetime.timedelta(days=1))
        if not data.empty:
            last_week = round(data['Close'].iloc[0], 2)
            current = round(data['Close'].iloc[-1], 2)
            change = round(((current - last_week) / last_week) * 100, 2)
            st.markdown(f"**Price last week**: ₹{last_week}")
            st.markdown(f"**Current price**: ₹{current}")
            st.markdown(f"**Change**: {'📉' if change < 0 else '📈'} {change}%")

            ticker = yf.Ticker(search_symbol)
            info = ticker.info
            st.markdown("### Company Overview")
            st.write(info.get("longBusinessSummary", "No summary available."))
            st.markdown("### Key Metrics")
            st.write({
                "Market Cap": info.get("marketCap"),
                "Sector": info.get("sector"),
                "Industry": info.get("industry"),
                "PE Ratio (TTM)": info.get("trailingPE"),
                "EPS (TTM)": info.get("trailingEps"),
                "52-Week High": info.get("fiftyTwoWeekHigh"),
                "52-Week Low": info.get("fiftyTwoWeekLow")
            })
        else:
            st.warning("No data found for that symbol.")
    except Exception as e:
        st.error(f"Error fetching data: {e}")

# Skipped Stocks
if skipped:
    with st.expander("⚠️ Skipped Stocks / Errors"):
        for s in skipped:
            st.text(s)
