import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import time

# Streamlit UI setup
st.set_page_config(page_title="NSE Top 50 Weekly Analyzer", layout="wide")
st.title("📈 NSE Top 50 - Weekly Price Change Tracker")
st.markdown("Shows weekly % change using real data from the past month via Yahoo Finance.")

# Adjust for weekends
today = datetime.date.today()
if today.weekday() >= 5:
    today -= datetime.timedelta(days=today.weekday() - 4)

start_date = today - datetime.timedelta(weeks=4)
st.markdown(f"📅 Analyzing data from **{start_date}** to **{today}**")

# Top 50 NSE tickers
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

results = []

with st.spinner("📥 Downloading and analyzing..."):
    for symbol in symbols:
        try:
            df = yf.download(symbol, start=start_date, end=today, interval="1d", progress=False)

            if df.empty or df.shape[0] < 10:
                continue

            df = df[['Close']].dropna().reset_index()
            df['Week'] = df['Date'].dt.isocalendar().week
            weekly = df.groupby('Week')['Close'].agg(['first', 'last']).reset_index()
            weekly['% Change'] = ((weekly['last'] - weekly['first']) / weekly['first']) * 100
            weekly['Symbol'] = symbol

            results.append(weekly)
            time.sleep(0.2)

        except Exception as e:
            st.warning(f"{symbol} skipped: {e}")
            continue

# Combine all
if results:
    combined = pd.concat(results)
    combined = combined[['Symbol', 'Week', 'first', 'last', '% Change']]
    combined.columns = ['Symbol', 'Week', 'Start Price', 'End Price', '% Change']
    combined = combined.sort_values(by=['Symbol', 'Week'])

    st.success("✅ Data processed successfully.")
    st.dataframe(combined, use_container_width=True)
else:
    st.error("⚠️ No data was found for any symbol.")
