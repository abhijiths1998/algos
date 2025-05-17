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
top_250_stocks = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS",
    "HINDUNILVR.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "BAJFINANCE.NS",
    "LICI.NS", "KOTAKBANK.NS", "LT.NS", "AXISBANK.NS", "ASIANPAINT.NS",
    "HCLTECH.NS", "MARUTI.NS", "SUNPHARMA.NS", "DMART.NS", "NTPC.NS",
    "TITAN.NS", "ULTRACEMCO.NS", "WIPRO.NS", "ADANIENT.NS", "POWERGRID.NS",
    "BAJAJFINSV.NS", "ONGC.NS", "COALINDIA.NS", "ADANIGREEN.NS", "ADANIPORTS.NS",
    "ADANITRANS.NS", "ADANIPOWER.NS", "HDFCLIFE.NS", "TECHM.NS", "JSWSTEEL.NS",
    "TATASTEEL.NS", "HINDALCO.NS", "SBILIFE.NS", "BAJAJ-AUTO.NS", "EICHERMOT.NS",
    "GRASIM.NS", "DIVISLAB.NS", "CIPLA.NS", "DRREDDY.NS", "BPCL.NS",
    "IOC.NS", "BRITANNIA.NS", "SHREECEM.NS", "HEROMOTOCO.NS", "HAVELLS.NS",
    "DLF.NS", "PIDILITIND.NS", "GODREJCP.NS", "INDUSINDBK.NS", "M&M.NS",
    "BAJAJHLDNG.NS", "SIEMENS.NS", "TATAMOTORS.NS", "TATACONSUM.NS", "SBICARD.NS",
    "ICICIPRULI.NS", "ICICIGI.NS", "HINDPETRO.NS", "AMBUJACEM.NS", "ACC.NS",
    "COLPAL.NS", "UBL.NS", "PAGEIND.NS", "BERGEPAINT.NS", "DABUR.NS",
    "MARICO.NS", "NESTLEIND.NS", "GAIL.NS", "PETRONET.NS", "MUTHOOTFIN.NS",
    "CHOLAFIN.NS", "LUPIN.NS", "TORNTPHARM.NS", "SRF.NS", "APOLLOHOSP.NS",
    "AUROPHARMA.NS", "GLAND.NS", "BIOCON.NS", "ALKEM.NS", "IPCALAB.NS",
    "LALPATHLAB.NS", "METROPOLIS.NS", "FORTIS.NS", "MAXHEALTH.NS", "RAIN.NS",
    "TATAELXSI.NS", "LTTS.NS", "COFORGE.NS", "MPHASIS.NS", "PERSISTENT.NS",
    "MINDTREE.NS", "LTI.NS", "OFSS.NS", "BALKRISIND.NS", "MRF.NS",
    "CEATLTD.NS", "APOLLOTYRE.NS", "TVSMOTOR.NS", "ASHOKLEY.NS", "ESCORTS.NS",
    "BOSCHLTD.NS", "M&MFIN.NS", "LICHSGFIN.NS", "CANFINHOME.NS", "RECLTD.NS",
    "PFC.NS", "IDFCFIRSTB.NS", "FEDERALBNK.NS", "BANDHANBNK.NS", "RBLBANK.NS",
    "INDIGO.NS", "INTERGLOBE.NS", "IRCTC.NS", "CONCOR.NS", "GMRINFRA.NS",
    "ADANITOTAL.NS", "ADANIGAS.NS", "ADANIRENEW.NS", "ADANIWILMAR.NS", "ADANIDATA.NS",
    "ADANIDIGI.NS", "ADANINEW.NS", "ADANIMEDIA.NS", "ADANICOMM.NS", "ADANITECH.NS",
    "ADANICONS.NS", "ADANILOG.NS", "ADANIPOWERGRID.NS", "ADANITRANSFORM.NS", "ADANIGLOBAL.NS",
    "ADANICAP.NS", "ADANIFIN.NS", "ADANIBANK.NS", "ADANILIFE.NS", "ADANIHEALTH.NS",
    "ADANIPHARM.NS", "ADANIMED.NS", "ADANIBIO.NS", "ADANICHEM.NS", "ADANIMETAL.NS",
    "ADANISTEEL.NS", "ADANIALUM.NS", "ADANICEMENT.NS", "ADANIBUILD.NS", "ADANICONST.NS",
    "ADANIREAL.NS", "ADANIPROP.NS", "ADANILAND.NS", "ADANIFERT.NS", "ADANICROP.NS",
    "ADANIFOOD.NS", "ADANIBEVER.NS", "ADANITEXT.NS", "ADANIFASH.NS", "ADANIRETAIL.NS",
    "ADANIECOM.NS", "ADANIDIGITAL.NS", "ADANINET.NS", "ADANITELE.NS", "ADANIMEDIA.NS",
    "ADANINEWS.NS", "ADANIENTERTAIN.NS", "ADANIMUSIC.NS", "ADANIFILM.NS", "ADANIGAME.NS",
    "ADANISPORT.NS", "ADANIEDU.NS", "ADANITRAIN.NS", "ADANIAIR.NS", "ADANISHIP.NS",
    "ADANIPORT.NS", "ADANILOGISTICS.NS", "ADANISTORAGE.NS", "ADANITRANS.NS", "ADANIGRID.NS",
    "ADANIPOWER.NS", "ADANIGEN.NS", "ADANIRENEW.NS", "ADANISOLAR.NS", "ADANIGREEN.NS",
    "ADANICLEAN.NS", "ADANIECO.NS", "ADANICARBON.NS", "ADANIGAS.NS", "ADANILNG.NS",
    "ADANIOIL.NS", "ADANICHEM.NS", "ADANIFERT.NS", "ADANIPETRO.NS", "ADANIMETAL.NS",
    "ADANISTEEL.NS", "ADANIALUM.NS", "ADANICEMENT.NS", "ADANIBUILD.NS", "ADANICONST.NS",
    "ADANIREAL.NS", "ADANIPROP.NS", "ADANILAND.NS", "ADANIFOOD.NS", "ADANIBEVER.NS",
    "ADANITEXT.NS", "ADANIFASH.NS", "ADANIRETAIL.NS", "ADANIECOM.NS", "ADANIDIGITAL.NS",
    "ADANINET.NS", "ADANITELE.NS", "ADANIMEDIA.NS", "ADANINEWS.NS", "ADANIENTERTAIN.NS",
    "ADANIMUSIC.NS", "ADANIFILM.NS", "ADANIGAME.NS", "ADANISPORT.NS", "ADANIEDU.NS",
    "ADANITRAIN.NS", "ADANIAIR.NS", "ADANISHIP.NS", "ADANIPORT.NS", "ADANILOGISTICS.NS",
    "ADANISTORAGE.NS", "ADANITRANS.NS", "ADANIGRID.NS", "ADANIPOWER.NS", "ADANIGEN.NS",
    "ADANIRENEW.NS", "ADANISOLAR.NS", "ADANIGREEN.NS", "ADANICLEAN.NS", "ADANIECO.NS",
    "ADANICARBON.NS", "ADANIGAS.NS", "ADANILNG.NS", "ADANIOIL.NS", "ADANICHEM.NS",
    "ADANIFERT.NS", "ADANIPETRO.NS", "ADANIMETAL.NS", "ADANISTEEL.NS", "ADANIALUM.NS",
    "ADANICEMENT.NS", "ADANIBUILD.NS", "ADANICONST.NS", "ADANIREAL.NS", "ADANIPROP.NS",
    "ADANILAND.NS", "ADANIFOOD.NS", "ADANIBEVER.NS", "ADANITEXT.NS", "ADANIFASH.NS",
    "ADANIRETAIL.NS", "ADANIECOM.NS", "ADANIDIGITAL.NS", "ADANINET.NS", "ADANITELE.NS",
    "ADANIMEDIA.NS", "ADANINEWS.NS", "ADANIENTERTAIN.NS", "ADANIMUSIC.NS", "ADANIFILM.NS",
    "ADANIGAME.NS", "ADANISPORT.NS", "ADANIEDU.NS", "ADANITRAIN.NS", "ADANIAIR.NS",
    "ADANISHIP.NS", "ADANIPORT.NS", "ADANILOGISTICS.NS", "ADANISTORAGE.NS", "ADANITRANS.NS",
    "ADANIGRID.NS", "ADANIPOWER.NS", "ADANIGEN.NS", "ADANIRENEW.NS", "ADANISOLAR.NS"
]


# Master filter
with st.sidebar:
    st.header("\U0001F4CB Filters")
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
    show_raw_data = st.checkbox("\U0001F4DD Show Raw Data", key="show_raw_data")
    show_info = st.checkbox("\U0001F6C8 Show DataFrame Info", key="show_info")
    show_nulls = st.checkbox("\U0001F573 Show Null Summary", key="show_nulls")
    st.markdown("---")
    st.caption("Developed by abhivarma362 · Powered by Streamlit")

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
col1, col2 = st.columns(2)
with col1:
    st.markdown("### \U0001F53C Top 5 Gainers")
    st.dataframe(perf_df.sort_values(by="Change (%)", ascending=False).head(5))

with col2:
    st.markdown("### \U0001F53D Top 5 Losers")
    st.dataframe(perf_df.sort_values(by="Change (%)").head(5))

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
