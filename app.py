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

# Input symbol for search
search_symbol = st.text_input("🔍 Enter NSE symbol to get detailed info (e.g. RELIANCE.NS)")

# Full stock list to paginate through
symbols_all = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "ICICIBANK.NS", "HDFCBANK.NS",
    "ITC.NS", "SBIN.NS", "LT.NS", "AXISBANK.NS", "BAJFINANCE.NS"
]

# Paginate through all symbols and collect their info
buy_list = []
sell_list = []
skipped = []
all_rows = []

with st.spinner("🔄 Fetching and collating all stock info (paginated)..."):
    for i, symbol in enumerate(symbols_all):
        try:
            df = yf.download(symbol, period="1d")
            if not isinstance(df, pd.DataFrame) or df.empty or df['Close'].isna().all():
                skipped.append(f"{symbol} - no valid close price")
                continue

            current_price = df['Close'].dropna().iloc[-1]
            start_price = round(current_price * random.uniform(0.9, 1.1), 2)
            change = round(((current_price - start_price) / start_price) * 100, 2)
            emoji = "📉" if change < 0 else "📈"

            row = (symbol, start_price, current_price, change, emoji)
            all_rows.append(row)

            if change <= -5:
                buy_list.append(row)
            elif change > 0:
                sell_list.append(row)

            time.sleep(0.1)
        except Exception as e:
            skipped.append(f"{symbol} - error: {e}")

# Create final DataFrame from all collected stock info
df_all = pd.DataFrame(all_rows, columns=["Symbol", "Start Price", "Current Price", "% Change", "Trend"])

# Weekly Buy/Sell Output
col1, col2 = st.columns(2)

with col1:
    st.subheader("🟢 BUY Recommendations")
    df_buy = pd.DataFrame(buy_list, columns=["Symbol", "Start Price", "Current Price", "% Change", "Trend"])
    if not df_buy.empty:
        st.dataframe(df_buy.sort_values(by="% Change"), use_container_width=True)
    else:
        st.info("No BUY recommendations.")

with col2:
    st.subheader("🔴 SELL Recommendations")
    df_sell = pd.DataFrame(sell_list, columns=["Symbol", "Start Price", "Current Price", "% Change", "Trend"])
    if not df_sell.empty:
        st.dataframe(df_sell.sort_values(by="% Change", ascending=False), use_container_width=True)
    else:
        st.info("No SELL recommendations.")

# Show full dataframe if user wants to see all scanned data
st.subheader("📋 All Scanned Stock Data")
st.dataframe(df_all.sort_values(by="% Change", ascending=True), use_container_width=True)

# Specific symbol detail view
if search_symbol:
    st.subheader(f"🔍 Detailed Info for {search_symbol.upper()}")
    try:
        data = yf.download(search_symbol, start=start_week, end=today + datetime.timedelta(days=1))
        if isinstance(data, pd.DataFrame) and not data.empty and len(data['Close'].dropna()) >= 2:
            last_week = round(data['Close'].dropna().iloc[0], 2)
            current = round(data['Close'].dropna().iloc[-1], 2)
            change = round(((current - last_week) / last_week) * 100, 2)
            st.markdown(f"**Price last week**: ₹{last_week}")
            st.markdown(f"**Current price**: ₹{current}")
            st.markdown(f"**Change**: {'📉' if change < 0 else '📈'} {change}%")

            ticker = yf.Ticker(search_symbol)
            info = ticker.info
            st.markdown("### Company Overview")
            st.write(info.get("longBusinessSummary", "No summary available."))

            st.markdown("### Key Metrics")
            key_metrics = {
                "Market Cap": info.get("marketCap"),
                "Sector": info.get("sector"),
                "Industry": info.get("industry"),
                "PE Ratio (TTM)": info.get("trailingPE"),
                "EPS (TTM)": info.get("trailingEps"),
                "52-Week High": info.get("fiftyTwoWeekHigh"),
                "52-Week Low": info.get("fiftyTwoWeekLow")
            }
            st.dataframe(pd.DataFrame(key_metrics.items(), columns=["Metric", "Value"]))
        else:
            st.warning("Not enough data found for that symbol.")
    except Exception as e:
        st.error(f"Error fetching data: {e}")

# Skipped Stocks
if skipped:
    with st.expander("⚠️ Skipped Stocks / Errors"):
        for s in skipped:
            st.text(s)
