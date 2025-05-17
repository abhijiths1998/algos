import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import time
import random

# Streamlit config
st.set_page_config(page_title="NSE Mini Signal App", layout="wide")
st.title("📈 NSE Stock Signal (Simulated Weekly)")
st.markdown("""
This dashboard gives you:
- ✅ Simulated **Buy/Sell signals** based on last price vs random historical price
- ✅ Simple and fast CLI-style interface with output tables
""")

# Today's date (adjust if weekend)
today = datetime.date.today()
if today.weekday() >= 5:
    today -= datetime.timedelta(days=today.weekday() - 4)

st.markdown(f"📅 Today (adjusted): **{today}**")

# Fixed set of symbols
symbols = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "ICICIBANK.NS", "HDFCBANK.NS",
    "SBIN.NS", "ITC.NS", "BAJFINANCE.NS", "LT.NS", "AXISBANK.NS"
]

buy_list = []
sell_list = []
skipped = []

with st.spinner("Fetching current prices..."):
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d")

            if not isinstance(data, pd.DataFrame) or data.empty:
                skipped.append(f"{symbol} - no data")
                continue

            current_price = round(data['Close'].iloc[-1], 2)
            start_price = round(current_price * random.uniform(0.9, 1.1), 2)
            change = round(((current_price - start_price) / start_price) * 100, 2)
            emoji = "📉" if change < 0 else "📈"

            row = (symbol, start_price, current_price, f"{emoji} {change}%")
            if change <= -5:
                buy_list.append(row)
            elif change > 0:
                sell_list.append(row)

            time.sleep(0.2)

        except Exception as e:
            skipped.append(f"{symbol} - error: {e}")

# Display BUY/SELL tables
col1, col2 = st.columns(2)

with col1:
    st.subheader("🟢 BUY Recommendations")
    if buy_list:
        df_buy = pd.DataFrame(buy_list, columns=["Symbol", "Start Price", "Current Price", "% Change"])
        st.dataframe(df_buy.sort_values(by="% Change"), use_container_width=True)
    else:
        st.info("No BUY recommendations today.")

with col2:
    st.subheader("🔴 SELL Recommendations")
    if sell_list:
        df_sell = pd.DataFrame(sell_list, columns=["Symbol", "Start Price", "Current Price", "% Change"])
        st.dataframe(df_sell.sort_values(by="% Change", ascending=False), use_container_width=True)
    else:
        st.info("No SELL recommendations today.")

# Skipped/Error Symbols
if skipped:
    with st.expander("⚠️ Skipped Stocks / Errors"):
        for s in skipped:
            st.text(s)
