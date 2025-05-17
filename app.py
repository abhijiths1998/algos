import streamlit as st
import yfinance as yf
import pandas as pd
import datetime

st.set_page_config(page_title="📉 NSE Stock Drop Scanner", layout="wide")
st.title("📉 NSE Weekly Stock Price Comparison")
st.markdown("Compare **latest closing price** with **last week's closing** for multiple stocks.")

# Load stock list
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

# Step 1: Download 3 months of stock data
st.info("Fetching stock data for last 3 months from Yahoo Finance...")
df_stocks = yf.download(symbols, period="3mo", group_by="ticker", progress=False)

# Step 2: Filter last 7 weeks
latest_date = df_stocks.index.max()
start_date = latest_date - datetime.timedelta(weeks=7)
df_filtered = df_stocks[df_stocks.index >= start_date]

# Step 3: Compare last week's close vs latest close
comparison_data = []

for symbol in symbols:
    try:
        close_prices = df_filtered[symbol]['Close'].dropna()
        if len(close_prices) < 2:
            continue

        current_price = close_prices.iloc[-1]
        last_week_price = close_prices.iloc[-6] if len(close_prices) >= 6 else close_prices.iloc[0]

        change = current_price - last_week_price
        pct_change = (change / last_week_price) * 100

        row = {
            "Symbol": symbol,
            "Last Week Close": round(last_week_price, 2),
            "Current Close": round(current_price, 2),
            "Change (₹)": round(change, 2),
            "Change (%)": round(pct_change, 2)
        }

        comparison_data.append(row)

    except Exception as e:
        st.warning(f"{symbol} skipped due to error: {e}")

# Step 4: Store in session state
df_all = pd.DataFrame(comparison_data)
st.session_state.df_all = df_all

# Step 5: Show all stock price differences
st.subheader("📊 All Stock Price Differences")
if df_all.empty:
    st.warning("No data available.")
else:
    st.dataframe(df_all.sort_values(by="Change (%)"), use_container_width=True)

# Step 6: Buy recommendations
st.subheader("🟢 Buy Recommendations (Drop > 5%)")
df_buy = df_all[df_all["Change (%)"] <= -5]
if df_buy.empty:
    st.info("No stocks dropped more than 5%.")
else:
    st.dataframe(df_buy.sort_values(by="Change (%)"), use_container_width=True)

# Step 7: Search by symbol
st.subheader("🔍 Search a Stock")
search = st.text_input("Enter symbol (e.g., TCS.NS)").upper()
if search:
    result = st.session_state.df_all[st.session_state.df_all["Symbol"].str.contains(search)]
    if not result.empty:
        st.dataframe(result, use_container_width=True)
    else:
        st.warning("No match found.")

# Step 8: Download option
if not df_all.empty:
    csv = df_all.to_csv(index=False)
    st.download_button("📥 Download All Data", data=csv, file_name="stock_diff.csv", mime="text/csv")
