import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import io

st.set_page_config(page_title="📊 NSE Dashboard", layout="wide")
st.title("📊 NSE Stock Price Analysis Dashboard")

# -----------------------------
# Symbol list: Top 50 NSE stocks
# -----------------------------
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

# -------------------------------
# 🔄 Download 3-months stock data
# -------------------------------
st.info("📥 Downloading stock data...")
df_stocks = yf.download(symbols, period="3mo", group_by="ticker", progress=False)

if not isinstance(df_stocks.index, pd.DatetimeIndex):
    st.error("❌ Index is not datetime. Cannot proceed.")
    st.stop()

# -------------------------------
# 📅 Filter last 7 weeks
# -------------------------------
latest_date = df_stocks.index.max()
start_date = latest_date - datetime.timedelta(weeks=7)
df_filtered = df_stocks[df_stocks.index >= start_date]

st.markdown(f"🗓️ Showing data from **{start_date.date()}** to **{latest_date.date()}**")

# -------------------------------
# 📦 Raw Data
# -------------------------------
st.subheader("📦 Filtered 7-Week Raw Data")
st.dataframe(df_filtered)

# -------------------------------
# ℹ️ DataFrame Info
# -------------------------------
st.subheader("ℹ️ DataFrame Info")
buffer = io.StringIO()
df_filtered.info(buf=buffer)
st.text(buffer.getvalue())

# -------------------------------
# 🕳️ Null Summary
# -------------------------------
st.subheader("🕳️ Null Value Summary (Top 10)")
nulls = df_filtered.isna().sum().sort_values(ascending=False)
st.dataframe(nulls[nulls > 0].head(10))

# -------------------------------
# 📈 Weekly Performance
# -------------------------------
st.subheader("📉 Weekly Stock Performance Summary")
performance = []
for symbol in symbols:
    try:
        data = df_filtered[symbol]['Close'].dropna()
        if len(data) < 2:
            continue
        start_price = data.iloc[0]
        end_price = data.iloc[-1]
        change = ((end_price - start_price) / start_price) * 100
        performance.append({
            "Symbol": symbol,
            "Start Price": round(start_price, 2),
            "End Price": round(end_price, 2),
            "Change (%)": round(change, 2)
        })
    except:
        continue

df_perf = pd.DataFrame(performance).sort_values(by="Change (%)")
st.dataframe(df_perf)

# -------------------------------
# 🔼 Gainers / 🔽 Losers
# -------------------------------
col1, col2 = st.columns(2)
with col1:
    st.subheader("🔼 Top 5 Gainers")
    st.dataframe(df_perf.sort_values(by="Change (%)", ascending=False).head(5))
with col2:
    st.subheader("🔽 Top 5 Losers")
    st.dataframe(df_perf.sort_values(by="Change (%)").head(5))

# -------------------------------
# 📈 Combined Chart - Gainers
# -------------------------------
st.subheader("📈 Compare Top Gainers")
top_n = st.slider("Select number of top gainers", 1, 10, 3)
top_symbols = df_perf.sort_values(by="Change (%)", ascending=False).head(top_n)["Symbol"].tolist()

gainer_data = pd.DataFrame()
for symbol in top_symbols:
    try:
        close_series = df_filtered[symbol]['Close'].dropna()
        if not close_series.empty:
            gainer_data[symbol] = close_series
    except:
        continue

if not gainer_data.empty:
    st.line_chart(gainer_data)
else:
    st.info("No valid data for gainers.")

# -------------------------------
# 📉 Combined Chart - Losers
# -------------------------------
st.subheader("📉 Compare Top Losers")
bottom_n = st.slider("Select number of top losers", 1, 10, 3)
bottom_symbols = df_perf.sort_values(by="Change (%)").head(bottom_n)["Symbol"].tolist()

loser_data = pd.DataFrame()
for symbol in bottom_symbols:
    try:
        close_series = df_filtered[symbol]['Close'].dropna()
        if not close_series.empty:
            loser_data[symbol] = close_series
    except:
        continue

if not loser_data.empty:
    st.line_chart(loser_data)
else:
    st.info("No valid data for losers.")

# -------------------------------
# 🕵️ Explore Stock by Time Period
# -------------------------------
st.markdown("---")
st.subheader("🕵️ Explore Stock Trends by Period")

selected_symbol = st.selectbox("🔍 Select a stock", symbols)
selected_period = st.selectbox("🗓️ Select time range", ["1mo", "6mo", "1y", "ytd", "5y"])

try:
    st.info(f"Loading `{selected_symbol}` for `{selected_period}`...")
    stock_df = yf.download(selected_symbol, period=selected_period, interval="1d", progress=False)

    if stock_df.empty or "Close" not in stock_df:
        st.warning("⚠️ No data found.")
    else:
        st.line_chart(stock_df["Close"], use_container_width=True)
        st.dataframe(stock_df.tail(10))
except Exception as e:
    st.error(f"Error: {e}")
