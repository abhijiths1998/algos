import yfinance as yf
import pandas as pd
import datetime
import time
import random
import streamlit as st

# Streamlit setup
st.set_page_config(page_title="Top 100 NSE Stock Recommender", layout="wide")
st.title("📈 NSE Top 100 - Weekly Stock Recommendations")
st.markdown("Automatically updated BUY/SELL signals based on simulated weekly % change using Yahoo Finance")

# Adjust date for weekends
today = datetime.date.today()
if today.weekday() >= 5:
    today -= datetime.timedelta(days=today.weekday() - 4)
st.markdown(f"📅 Analyzing as of: **{today}**")

# Top 100 NSE tickers (Nifty 100)
top_100_nse = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "ICICIBANK.NS", "HDFCBANK.NS", "SBIN.NS", "ITC.NS", "BAJFINANCE.NS",
    "LT.NS", "AXISBANK.NS", "KOTAKBANK.NS", "ASIANPAINT.NS", "SUNPHARMA.NS", "WIPRO.NS", "NESTLEIND.NS", "ULTRACEMCO.NS",
    "MARUTI.NS", "POWERGRID.NS", "NTPC.NS", "TECHM.NS", "TITAN.NS", "HCLTECH.NS", "BHARTIARTL.NS", "ADANIENT.NS",
    "COALINDIA.NS", "JSWSTEEL.NS", "HINDUNILVR.NS", "ADANIGREEN.NS", "CIPLA.NS", "BAJAJFINSV.NS", "INDUSINDBK.NS",
    "HDFCLIFE.NS", "BAJAJ-AUTO.NS", "TATACONSUM.NS", "BPCL.NS", "DIVISLAB.NS", "DRREDDY.NS", "EICHERMOT.NS",
    "GRASIM.NS", "HEROMOTOCO.NS", "IOC.NS", "M&M.NS", "SHREECEM.NS", "ONGC.NS", "BRITANNIA.NS", "SBILIFE.NS",
    "UPL.NS", "ICICIPRULI.NS", "HINDALCO.NS", "TATASTEEL.NS", "APOLLOHOSP.NS", "AMBUJACEM.NS", "BAJAJHLDNG.NS",
    "DMART.NS", "CHOLAFIN.NS", "PIDILITIND.NS", "TRENT.NS", "LTI.NS", "NAUKRI.NS", "SRF.NS", "LTIM.NS", "ADANIPORTS.NS",
    "DABUR.NS", "BOSCHLTD.NS", "BERGEPAINT.NS", "GODREJCP.NS", "GLAND.NS", "HAL.NS", "ICICIGI.NS", "IDFCFIRSTB.NS",
    "INDIGO.NS", "MARICO.NS", "MRF.NS", "MUTHOOTFIN.NS", "PEL.NS", "SIEMENS.NS", "TORNTPHARM.NS", "TVSMOTOR.NS",
    "VEDL.NS", "ZOMATO.NS", "IRCTC.NS", "ABB.NS", "ADANIPOWER.NS", "BANKBARODA.NS", "BHEL.NS", "CANBK.NS", "CONCOR.NS",
    "GAIL.NS", "MANAPPURAM.NS", "RECLTD.NS", "SAIL.NS", "TATAMOTORS.NS", "VOLTAS.NS", "PNB.NS", "RAJESHEXPO.NS",
    "HAVELLS.NS", "BEL.NS", "INDUSTOWER.NS", "JSPL.NS"
]

buy_list = []
sell_list = []

with st.spinner("Fetching and analyzing stock data..."):
    for symbol in top_100_nse[:100]:
        try:
            data = yf.download(symbol, period="1d", progress=False)

            if data.empty:
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
        except Exception:
            continue

# Show results
col1, col2 = st.columns(2)

with col1:
    st.subheader("🟢 BUY Recommendations (Dropped > 5%)")
    if buy_list:
        buy_df = pd.DataFrame(buy_list, columns=["Symbol", "Start Price", "Current Price", "% Change"])
        st.dataframe(buy_df.sort_values(by="% Change"), use_container_width=True)
    else:
        st.success("No BUY signals today.")

with col2:
    st.subheader("🔴 SELL Recommendations (Price Increased)")
    if sell_list:
        sell_df = pd.DataFrame(sell_list, columns=["Symbol", "Start Price", "Current Price", "% Change"])
        st.dataframe(sell_df.sort_values(by="% Change", ascending=False), use_container_width=True)
    else:
        st.success("No SELL signals today.")
