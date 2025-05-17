import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import io

st.set_page_config(page_title="📊 NSE 7-Week Summary", layout="wide")
st.title("📊 NSE Stock Price Analysis (Last 7 Weeks)")

# List of top 50 NSE symbols
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

st.info("📥 Downloading 3-month price history from Yahoo Finance...")
df_stocks = yf.download(symbols, period="3mo", group_by="ticker", progress=False)

# Make sure index is datetime
if not isinstance(df_stocks.index, pd.DatetimeIndex):
    st.error("Date index missing. Cannot proceed.")
    st.stop()

# Filter last 7 weeks
latest_date = df_stocks.index.max()
start_date = latest_date - datetime.timedelta(weeks=7)
df_filtered = df_stocks[df_stocks.index >= start_date]
st.markdown(f"📅 **Date Range**: {start_date.date()} → {latest_date.date()}")

# Show raw data
st.subheader("🧾 Filtered 7-Week Raw Data")
st.dataframe(df_filtered)

# Show DataFrame info safely
st.subheader("ℹ️ DataFrame Info")
buffer = io.StringIO()
df_filtered.info(buf=buffer)
st.text(buffer.getvalue())

# 🧮 Null summary
st.subheader("🕳️ Null Value Summary (Top 10 columns with NaNs)")
null_summary = df_filtered.isna().sum().sort_values(ascending=False)
st.dataframe(null_summary[null_summary > 0].head(10))

# 📈 Weekly % Change for each symbol
st.subheader("📉 Weekly Performance Summary")
results = []
for symbol in symbols:
    try:
        data = df_filtered[symbol]['Close'].dropna()
        if len(data) < 2:
            continue
        start_price = data.iloc[0]
        end_price = data.iloc[-1]
        change = ((end_price - start_price) / start_price) * 100
        results.append({
            "Symbol": symbol,
            "Start Price": round(start_price, 2),
            "End Price": round(end_price, 2),
            "Change (%)": round(change, 2)
        })
    except Exception as e:
        continue

df_perf = pd.DataFrame(results).sort_values(by="Change (%)", ascending=True)
st.dataframe(df_perf)

# 🟢 Top Gainers / 🔴 Top Losers
col1, col2 = st.columns(2)
with col1:
    st.subheader("🔼 Top 5 Gainers")
    st.dataframe(df_perf.sort_values(by="Change (%)", ascending=False).head(5))

with col2:
    st.subheader("🔽 Top 5 Losers")
    st.dataframe(df_perf.sort_values(by="Change (%)").head(5))

# 📊 Chart toggle
if st.checkbox("📈 Show line chart for Top 3 Gainers"):
    top_symbols = df_perf.sort_values(by="Change (%)", ascending=False).head(3)["Symbol"].tolist()
    for symbol in top_symbols:
        try:
            chart_data = df_filtered[symbol]['Close'].dropna()
            st.line_chart(chart_data.rename(symbol))
        except Exception:
            st.warning(f"Couldn't chart {symbol}")
