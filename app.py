import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import io
import smtplib
from email.message import EmailMessage
import matplotlib.pyplot as plt

# Set wide layout with stylish sidebar
st.set_page_config(page_title="\U0001F4C8 NSE Dashboard", layout="wide")
st.markdown("""
    <style>
        .big-font { font-size:24px !important; }
        .stButton>button { background-color: #0072C6; color: white; }
        .stSlider>div>div>div>div { background: #0072C6; }
        .block-container { padding-top: 1rem; }
    </style>
""", unsafe_allow_html=True)

st.title("\U0001F4C8 NSE Stock Price Analysis Dashboard")
st.markdown("""
Welcome to the NSE Dashboard! Interact with the filters and visualizations to explore top Indian stocks.
---
""")

# Top 500 NSE symbols (sample subset for demo; replace with full list)
nse_500_symbols = [
    "3MINDIA.NS", "AARTIIND.NS", "AAVAS.NS", "ABB.NS", "ABBOTINDIA.NS", "ABCAPITAL.NS", "ABFRL.NS", "ACC.NS", "ADANIENT.NS",
    "ADANIPORTS.NS", "ADANIPOWER.NS", "ADANITOTGAS.NS", "ADANIENSOL.NS", "ADANIGREEN.NS", "AIAENG.NS", "AJANTPHARM.NS",
    "ALKEM.NS", "APLLTD.NS", "AMARAJABAT.NS", "AMBUJACEM.NS", "APOLLOHOSP.NS", "APOLLOTYRE.NS", "APARINDS.NS",
    "ASIANPAINT.NS", "ASTRAL.NS", "ATUL.NS", "AUBANK.NS", "AUROPHARMA.NS", "AXISBANK.NS", "BAJAJ-AUTO.NS", "BAJFINANCE.NS",
    "BAJAJFINSV.NS", "BAJAJHLDNG.NS", "BALKRISIND.NS", "BANDHANBNK.NS", "BANKBARODA.NS", "BANKINDIA.NS", "BATAINDIA.NS",
    "BAYERCROP.NS", "BERGEPAINT.NS", "BEL.NS", "BHARATFORG.NS", "BHARTIARTL.NS", "BHEL.NS", "BIOCON.NS", "BLUEDART.NS",
    "BBTC.NS", "BOSCHLTD.NS", "BPCL.NS", "BRITANNIA.NS", "CANBK.NS", "CASTROLIND.NS", "CENTRALBK.NS", "CHOLAFIN.NS",
    "CIPLA.NS", "COALINDIA.NS", "COFORGE.NS", "COLPAL.NS", "CONCOR.NS", "COROMANDEL.NS", "CROMPTON.NS", "DABUR.NS",
    "DALBHARAT.NS", "DIVISLAB.NS", "DIXON.NS", "DLF.NS", "DRREDDY.NS", "EICHERMOT.NS", "ESCORTS.NS", "GAIL.NS", "GLAND.NS",
    "GODREJCP.NS", "GODREJPROP.NS", "GRASIM.NS", "GUJGASLTD.NS", "HAVELLS.NS", "HCLTECH.NS", "HDFCAMC.NS", "HDFCBANK.NS",
    "HDFCLIFE.NS", "HEROMOTOCO.NS", "HINDALCO.NS", "HINDPETRO.NS", "HINDUNILVR.NS", "HINDZINC.NS", "HONAUT.NS",
    "IBULHSGFIN.NS", "ICICIBANK.NS", "ICICIGI.NS", "ICICIPRULI.NS", "IDBI.NS", "IDFCFIRSTB.NS", "IGL.NS", "INDHOTEL.NS",
    "INDIAMART.NS", "INDIGO.NS", "INDUSINDBK.NS", "INDUSTOWER.NS", "INFY.NS", "IOC.NS", "IRCTC.NS", "ITC.NS",
    "JINDALSTEL.NS", "JSWENERGY.NS", "JSWSTEEL.NS", "JUBLFOOD.NS", "KOTAKBANK.NS", "L&TFH.NS", "LALPATHLAB.NS",
    "LICHSGFIN.NS", "LTI.NS", "LTTS.NS", "M&M.NS", "M&MFIN.NS", "MANAPPURAM.NS", "MARICO.NS", "MARUTI.NS", "MCDOWELL-N.NS",
    "MCX.NS", "METROBRANDS.NS", "MFSL.NS", "MGL.NS", "MINDTREE.NS", "MOTILALFSL.NS", "MPHASIS.NS", "MRF.NS", "MUTHOOTFIN.NS",
    "NAM-INDIA.NS", "NATCOPHARM.NS", "NATIONALUM.NS", "NAVINFLUOR.NS", "NBCC.NS", "NESTLEIND.NS", "NETWORK18.NS", "NHPC.NS",
    "NMDC.NS", "NTPC.NS", "OBEROIRLTY.NS", "OFSS.NS", "ONGC.NS", "PAGEIND.NS", "PEL.NS", "PETRONET.NS", "PFC.NS",
    "PIDILITIND.NS", "PIIND.NS", "PNB.NS", "POLYCAB.NS", "POWERGRID.NS", "PVRINOX.NS", "RAMCOCEM.NS", "RBLBANK.NS",
    "RECLTD.NS", "RELIANCE.NS", "SBICARD.NS", "SBILIFE.NS", "SBIN.NS", "SHREECEM.NS", "SIEMENS.NS", "SRF.NS", "SRTRANSFIN.NS",
    "SUNPHARMA.NS", "SUNTV.NS", "TATACHEM.NS", "TATACONSUM.NS", "TATAMOTORS.NS", "TATAPOWER.NS", "TATASTEEL.NS", "TCS.NS",
    "TECHM.NS", "TITAN.NS", "TORNTPHARM.NS", "TORNTPOWER.NS", "TRENT.NS", "TVSMOTOR.NS", "UBL.NS", "ULTRACEMCO.NS", "UPL.NS",
    "VEDL.NS", "VGUARD.NS", "VOLTAS.NS", "WIPRO.NS", "YESBANK.NS", "ZEEL.NS", "ZYDUSLIFE.NS", "ADANIENT.NS", "ADANIPORTS.NS",
    "APLAPOLLO.NS", "ALKEM.NS", "AUBANK.NS", "ASHOKLEY.NS", "BAJAJHLDNG.NS", "BANKBARODA.NS", "BHEL.NS", "CANBK.NS", "CONCOR.NS",
    "DLF.NS", "GAIL.NS", "GODREJPROP.NS", "HCLTECH.NS", "HINDALCO.NS", "IBULHSGFIN.NS", "IDFCFIRSTB.NS", "IOC.NS", "JSWSTEEL.NS",
    "L&TFH.NS", "LICHSGFIN.NS", "LTTS.NS", "M&MFIN.NS", "MRF.NS", "NMDC.NS", "OBEROIRLTY.NS", "PEL.NS", "PNB.NS", "RECLTD.NS",
    "SBICARD.NS", "SRTRANSFIN.NS", "TATACHEM.NS", "TATAMOTORS.NS", "TATAPOWER.NS", "VEDL.NS", "YESBANK.NS", "AARTIIND.NS",
    "ABFRL.NS", "ACC.NS", "ADANIPOWER.NS", "ADANITOTGAS.NS", "AIAENG.NS", "AMBUJACEM.NS", "APOLLOTYRE.NS", "ASIANPAINT.NS",
    "ASTRAL.NS", "ATUL.NS", "AUROPHARMA.NS", "BAJAJ-AUTO.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS", "BALKRISIND.NS", "BANDHANBNK.NS",
    "BANKINDIA.NS", "BATAINDIA.NS", "BAYERCROP.NS", "BERGEPAINT.NS", "BEL.NS", "BHARATFORG.NS", "BHARTIARTL.NS", "BIOCON.NS",
    "BLUEDART.NS", "BBTC.NS", "BOSCHLTD.NS", "BPCL.NS", "BRITANNIA.NS", "CASTROLIND.NS", "CENTRALBK.NS", "CHOLAFIN.NS", "CIPLA.NS",
    "COALINDIA.NS", "COFORGE.NS", "COLPAL.NS", "COROMANDEL.NS", "CROMPTON.NS", "DABUR.NS", "DALBHARAT.NS", "DIVISLAB.NS", "DIXON.NS",
    "DRREDDY.NS", "EICHERMOT.NS", "ESCORTS.NS", "GLAND.NS", "GODREJCP.NS", "GRASIM.NS", "GUJGASLTD.NS", "HAVELLS.NS", "HDFCAMC.NS",
    "HDFCBANK.NS", "HDFCLIFE.NS", "HEROMOTOCO.NS", "HINDPETRO.NS", "HINDUNILVR.NS", "HINDZINC.NS", "HONAUT.NS", "ICICIBANK.NS",
    "ICICIGI.NS", "ICICIPRULI.NS", "IDBI.NS", "IGL.NS", "INDHOTEL.NS", "INDIAMART.NS", "INDIGO.NS", "INDUSINDBK.NS", "INDUSTOWER.NS",
    "INFY.NS", "IRCTC.NS", "ITC.NS", "JINDALSTEL.NS", "JSWENERGY.NS", "JUBLFOOD.NS", "KOTAKBANK.NS", "LALPATHLAB.NS", "LTI.NS", "M&M.NS",
    "MANAPPURAM.NS", "MARICO.NS", "MARUTI.NS", "MCDOWELL-N.NS", "MCX.NS", "METROBRANDS.NS", "MFSL.NS", "MGL.NS", "MINDTREE.NS", "MOTILALFSL.NS",
    "MPHASIS.NS", "MRF.NS", "MUTHOOTFIN.NS", "NAM-INDIA.NS", "NATCOPHARM.NS", "NATIONALUM.NS", "NAVINFLUOR.NS", "NBCC.NS", "NESTLEIND.NS",
    "NETWORK18.NS", "NHPC.NS", "NTPC.NS", "OFSS.NS", "ONGC.NS", "PAGEIND.NS", "PETRONET.NS", "PFC.NS", "PIDILITIND.NS", "PIIND.NS", "POLYCAB.NS",
    "POWERGRID.NS", "PVRINOX.NS", "RAMCOCEM.NS", "RBLBANK.NS", "RELIANCE.NS", "SBILIFE.NS", "SBIN.NS", "SHREECEM.NS", "SIEMENS.NS", "SRF.NS",
    "SUNPHARMA.NS", "SUNTV.NS", "TATACONSUM.NS", "TATASTEEL.NS", "TCS.NS", "TECHM.NS", "TITAN.NS", "TORNTPHARM.NS", "TORNTPOWER.NS", "TRENT.NS",
    "TVSMOTOR.NS", "UBL.NS", "ULTRACEMCO.NS", "UPL.NS", "VGUARD.NS", "VOLTAS.NS", "WIPRO.NS", "ZEEL.NS", "ZYDUSLIFE.NS", "AAVAS.NS", "ABB.NS",
    "ABBOTINDIA.NS", "ABCAPITAL.NS", "ADANIENSOL.NS", "AJANTPHARM.NS", "AMARAJABAT.NS", "APOLLOHOSP.NS", "APARINDS.NS", "AXISBANK.NS", "BALKRISIND.NS",
    "BATAINDIA.NS", "BHARATFORG.NS", "BHEL.NS", "BPCL.NS", "BRITANNIA.NS", "CANBK.NS", "CASTROLIND.NS", "CENTRALBK.NS", "CIPLA.NS", "COALINDIA.NS",
    "COFORGE.NS", "COLPAL.NS", "CONCOR.NS", "COROMANDEL.NS", "CROMPTON.NS", "DABUR.NS", "DALBHARAT.NS", "DIVISLAB.NS", "DIXON.NS", "DRREDDY.NS",
    "EICHERMOT.NS", "ESCORTS.NS", "GAIL.NS", "GLAND.NS", "GODREJCP.NS", "GRASIM.NS", "GUJGASLTD.NS", "HAVELLS.NS", "HDFCAMC.NS", "HDFCBANK.NS",
    "HDFCLIFE.NS", "HEROMOTOCO.NS", "HINDALCO.NS", "HINDPETRO.NS", "HINDUNILVR.NS", "HINDZINC.NS", "HONAUT.NS", "ICICIBANK.NS", "ICICIGI.NS",
    "ICICIPRULI.NS", "IDBI.NS", "IGL.NS", "INDHOTEL.NS", "INDIAMART.NS", "INDIGO.NS", "INDUSINDBK.NS", "INDUSTOWER.NS", "INFY.NS", "IOC.NS", "IRCTC.NS",
    "ITC.NS", "JINDALSTEL.NS", "JSWENERGY.NS", "JUBLFOOD.NS", "KOTAKBANK.NS", "LALPATHLAB.NS", "LTI.NS", "M&M.NS", "M&MFIN.NS", "MANAPPURAM.NS", "MARICO.NS",
    "MARUTI.NS", "MCDOWELL-N.NS", "MCX.NS", "METROBRANDS.NS", "MFSL.NS", "MGL.NS", "MINDTREE.NS", "MOTILALFSL.NS", "MPHASIS.NS", "MRF.NS", "MUTHOOTFIN.NS",
    "NAM-INDIA.NS", "NATCOPHARM.NS", "NATIONALUM.NS", "NAVINFLUOR.NS", "NBCC.NS", "NESTLEIND.NS", "NETWORK18.NS", "NHPC.NS", "NMDC.NS", "NTPC.NS", "OFSS.NS",
    "ONGC.NS", "PAGEIND.NS", "PETRONET.NS", "PFC.NS", "PIDILITIND.NS", "PIIND.NS", "POLYCAB.NS", "POWERGRID.NS", "PVRINOX.NS", "RAMCOCEM.NS", "RBLBANK.NS",
    "RELIANCE.NS", "SBILIFE.NS", "SBIN.NS", "SHREECEM.NS", "SIEMENS.NS", "SRF.NS", "SUNPHARMA.NS", "SUNTV.NS", "TATACONSUM.NS", "TATASTEEL.NS", "TCS.NS",
    "TECHM.NS", "TITAN.NS", "TORNTPHARM.NS", "TORNTPOWER.NS", "TRENT.NS", "TVSMOTOR.NS", "UBL.NS", "ULTRACEMCO.NS", "UPL.NS", "VGUARD.NS", "VOLTAS.NS",
    "WIPRO.NS", "ZEEL.NS", "ZYDUSLIFE.NS"
]



# Master filter
with st.sidebar:
    st.header("📋 Filters")
    st.markdown("""Customize your analysis with dynamic filters below:""")
    default_symbols = ["RELIANCE.NS", "TCS.NS", "INFY.NS"]
    if set(default_symbols).issubset(set(nse_500_symbols)):
        master_symbols = st.multiselect(
            "🔍 Select Stocks (Master Filter)",
            options=nse_500_symbols,
            default=default_symbols,
            key="master_symbols"
        )
    else:
        st.warning("Some default symbols are not in the options. Please select manually.")
        master_symbols = st.multiselect(
            "🔍 Select Stocks (Master Filter)",
            options=nse_500_symbols,
            key="master_symbols"
        )

    display_period = st.selectbox("Time Period", ["1mo", "3mo", "6mo", "1y", "5y"], index=1, key="display_period")
    compare_type = st.radio("Compare By", ["Top Gainers", "Top Losers"], horizontal=True, key="compare_type")
    show_raw_data = st.checkbox("📝 Show Raw Data", key="show_raw_data")
    show_info = st.checkbox("🛈 Show DataFrame Info", key="show_info")
    show_nulls = st.checkbox("🕳 Show Null Summary", key="show_nulls")
    st.markdown("---")
    st.caption("Developed by ChatGPT · Powered by Streamlit")

# Download data
st.info("\U0001F4E5 Downloading stock data...")
all_data = yf.download(master_symbols, period=display_period, group_by="ticker", progress=False)

if not isinstance(all_data.index, pd.DatetimeIndex):
    st.error("Index is not datetime. Cannot proceed.")
    st.stop()

# Filter last 7 weeks
latest_date = all_data.index.max()
start_date = latest_date - datetime.timedelta(weeks=7)
df_filtered = all_data[all_data.index >= start_date]

st.markdown(f"\U0001F4C6 Showing data from **{start_date.date()}** to **{latest_date.date()}**")

# Optional displays
if show_raw_data:
    st.subheader("\U0001F4C2 Filtered Raw Data")
    st.dataframe(df_filtered)

if show_info:
    buffer = io.StringIO()
    df_filtered.info(buf=buffer)
    st.subheader("\U0001F4CA DataFrame Info")
    st.text(buffer.getvalue())

if show_nulls:
    st.subheader("\U0001F573 Null Summary")
    nulls = df_filtered.isna().sum().sort_values(ascending=False)
    st.dataframe(nulls[nulls > 0].head(10))

# Weekly Performance Summary
st.subheader("\U0001F4C9 Weekly Stock Performance Summary")
performance = []
for symbol in master_symbols:
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
            "Change (%)": round(change, 2),
            "Recommendation": "BUY" if change <= -5 else "SELL"
        })
    except:
        continue

perf_df = pd.DataFrame(performance).sort_values(by="Change (%)", ascending=(compare_type == "Top Losers"))
st.dataframe(perf_df)

# Side-by-side gainers & losers
sorted_perf = perf_df.sort_values(by="Change (%)", ascending=False).reset_index(drop=True)
top_gainers = sorted_perf.head(5)

sorted_perf_losers = perf_df.sort_values(by="Change (%)", ascending=True).reset_index(drop=True)
top_losers = sorted_perf_losers.head(5)

# Remove duplicates (optional)
common_symbols = set(top_gainers["Symbol"]).intersection(set(top_losers["Symbol"]))
top_losers = top_losers[~top_losers["Symbol"].isin(common_symbols)]

col1, col2 = st.columns(2)
with col1:
    st.markdown("### 🔼 Top 5 Gainers")
    st.dataframe(top_gainers)

with col2:
    st.markdown("### 🔽 Top 5 Losers")
    st.dataframe(top_losers)

# Charting selected comparison type
chart_type = "Gainers" if compare_type == "Top Gainers" else "Losers"
chart_n = st.slider(f"Compare Top {chart_type}", min_value=1, max_value=10, value=3, key="chart_top")
top_symbols = perf_df.head(chart_n)['Symbol'].tolist() if chart_type == "Losers" else perf_df.tail(chart_n)['Symbol'].tolist()

chart_df = pd.DataFrame()
for symbol in top_symbols:
    try:
        series = df_filtered[symbol]["Close"].dropna()
        chart_df[symbol] = series
    except:
        continue

if not chart_df.empty:
    st.line_chart(chart_df)
else:
    st.warning("No valid data available for chart.")

# Side-by-side Area and Bar Charts
st.subheader("📊 Visual Comparison: Price Trends vs Performance")
chart_area_df = chart_df.copy()
chart_bar_df = perf_df.set_index("Symbol")["Change (%)"]

area_col, bar_col = st.columns(2)

with area_col:
    st.markdown("**📈 Area Chart - Price Trends**")
    if not chart_area_df.empty:
        st.area_chart(chart_area_df)
    else:
        st.info("No data available for area chart.")

with bar_col:
    st.markdown("**📊 Bar Chart - % Change**")
    if not chart_bar_df.empty:
        st.bar_chart(chart_bar_df[top_symbols])
    else:
        st.info("No data available for bar chart.")

# EDA and Recommendation Summary
st.subheader("\U0001F9E0 Exploratory Data Analysis & Insights")

# Buy Recommendation Summary
buy_df = perf_df[perf_df["Recommendation"] == "BUY"]
if not buy_df.empty:
    st.success("\U0001F4B8 Stocks recommended for BUY (dropped more than 5%):")
    st.dataframe(buy_df)
else:
    st.info("No BUY recommendations this week. All stocks are relatively stable or gaining.")

# Sell Recommendation Summary
sell_df = perf_df[perf_df["Recommendation"] == "SELL"]
if not sell_df.empty:
    st.warning("\U0001F6AB Stocks marked for SELL:")
    st.dataframe(sell_df)
