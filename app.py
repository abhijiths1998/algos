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
    "360ONE", "3MINDIA", "ABB", "ACC", "AIAENG", "APLAPOLLO", "AUBANK", "AARTIIND", "AAVAS", "ABBOTINDIA",
    "ACE", "ADANIENSOL", "ADANIENT", "ADANIGREEN", "ADANIPORTS", "ADANIPOWER", "ATGL", "AWL", "ABCAPITAL",
    "ABFRL", "ABSLAMC", "ACCELYA", "ACE", "ADFFOODS", "ADL", "ADANITRANS", "AEGISCHEM", "AFFLE", "AGARIND",
    "AGRITECH", "AGROPHOS", "AGROTECH", "AHIMSA", "AHLADA", "AHLUCONT", "AIAENG", "AIRAN", "AIROLAM",
    "AJANTPHARM", "AJMERA", "AJOONI", "AKASH", "AKG", "AKSHOPTFBR", "AKSHARCHEM", "AKZOINDIA", "ALANKIT",
    "ALBERTDAVD", "ALCHEM", "ALEMBICLTD", "ALEMBICPH", "ALICON", "ALKALI", "ALKEM", "ALKYLAMINE", "ALLCARGO",
    "ALLIEDDIGI", "ALLSEC", "ALMONDZ", "ALOKINDS", "ALPA", "ALPHAGEO", "ALPSINDUS", "AMARAJABAT", "AMBANIORG",
    "AMBER", "AMBIKCO", "AMBUJACEM", "AMDIND", "AMITSPG", "AMJLAND", "AMRUTANJAN", "ANANTRAJ", "ANDHRACEMT",
    "ANDHRAPAP", "ANGELBRKG", "ANI", "ANIKINDS", "ANJANI", "ANKITMETAL", "ANSALHSG", "ANSALAPI", "APARINDS",
    "APCOTEXIND", "APEX", "APLAPOLLO", "APOLLOHOSP", "APOLLO", "APOLLOPIPE", "APOLSINHOT", "APOLLOTYRE",
    "APTECHT", "ARCHIDPLY", "ARCHIES", "ARCOTECH", "ARIES", "ARIHANT", "ARIHANTSUP", "ARMANFIN", "AROGRANITE",
    "ARROWGREEN", "ARSHIYA", "ARSSINFRA", "ARTNIRMAN", "ARTEDZ", "ARTEMIS", "ARVEE", "ARVIND", "ARVSMART",
    "ASAHIINDIA", "ASAHSNG", "ASCOM", "ASHAPURMIN", "ASHIANA", "ASHIM", "ASHOKLEY", "ASHOKA", "ASIANTILES",
    "ASIANHOTNR", "ASIANHOT", "ASIANPAINT", "ASLIND", "ASPINWALL", "ASSOALC", "ASTEC", "ASTERDM", "ASTRAMICRO",
    "ASTRAL", "ASTRAZEN", "ASTRON", "ATLANTA", "ATLAS", "ATNINTER", "ATULAUTO", "ATUL", "AUBANK", "AURDIS",
    "AURIONPRO", "AUROPHARMA", "AUSOMENT", "AUTOLINE", "AUTOLITIND", "AUTOAXLES", "AUTOSTAMP", "AVADHSUGAR",
    "AVANTIFEED", "AVENTUS", "AVENUES", "AVGLOG", "AVROIND", "AVSL", "AVTNPL", "AXISBANK", "AXISCADES",
    "AYMSYNTEX", "BAJAJ-AUTO", "BAJFINANCE", "BAJAJFINSV", "BAJAJHLDNG", "BAJAJCON", "BAJAJELEC", "BAJAJHIND",
    "BAJAJSTL", "BALAJITELE", "BALAMINES", "BALMLAWRIE", "BALPHARMA", "BALRAMCHIN", "BANARISUG", "BANCOINDIA",
    "BANDHANBNK", "BANKBARODA", "BANKINDIA", "BANSWRAS", "BARTRONICS", "BASF", "BATAINDIA", "BAYERCROP",
    "BBTC", "BCLIND", "BEML", "BEPL", "BERGEPAINT", "BFINVEST", "BFUTILITIE", "BGRENERGY", "BHAGCHEM",
    "BHAGERIA", "BHAGYANGR", "BHANDARI", "BHARATFORG", "BHARATGEAR", "BHARATRAS", "BHARATWIRE", "BHARTIARTL",
    "BHEL", "BHUSANSTL", "BIBCL", "BIGBLOC", "BIL", "BILENERGY", "BINDALAGRO", "BIOCON", "BIRLACABLE",
    "BIRLACORPN", "BIRLAMONEY", "BIRLATYRE", "BKMINDST", "BLBLIMITED", "BLISSGVS", "BLKASHYAP", "BLS",
    "BLUEDART", "BLUESTARCO", "BODALCHEM", "BOMDYEING", "BORORENEW", "BOSCHLTD", "BPCL", "BRFL", "BRIGADE",
    "BRITANNIA", "BROADCAST", "BSE", "BSHSL", "BSL", "BSOFT", "BUTTERFLY", "BYKE", "CADILAHC", "CALSOFT",
    "CAMLINFINE", "CANBK", "CANFINHOME", "CAPACITE", "CAPLIPOINT", "CAPTRUST", "CARBORUNIV", "CAREERP",
    "CARERATING", "CASTROLIND", "CCHHL", "CCL", "CEATLTD", "CELEBRITY", "CELLO", "CENTENKA", "CENTEXT",
    "CENTRALBK", "CENTRUM", "CENTUM", "CENTURYPLY", "CENTURYTEX", "CERA", "CESC", "CGCL", "CGPOWER",
    "CHALET", "CHAMBLFERT", "CHEMPLASTS", "CHENNPETRO", "CHOLAFIN", "CHOLAHLDNG", "CIGNITITEC", "CIMMCO",
    "CINELINE", "CINEVISTA", "CIPLA", "CITYUNIONBK", "CKFSL", "CLNINDIA", "CLSEL", "CMICABLES", "COALINDIA",
    "COCHINSHIP", "COFORGE", "COLPAL", "COMPINFO", "COMPUSOFT", "CONCOR", "CONFIPET", "CONSOFINVT", "CONTROLPR",
    "CORALFINAC", "COROMANDEL", "COSMOFILMS", "COUNCODOS", "CREDITACC", "CREST", "CRISIL", "CROMPTON",
    "CSBBANK", "CTE", "CUB", "CUMMINSIND", "CUPID", "CYBERMEDIA", "CYBERTECH", "CYIENT", "DAAWAT", "DABUR",
    "DALBHARAT", "DALMIASUG", "DAMODARIND", "DANGEE", "DATAMATICS", "DBCORP", "DBL", "DBREALTY", "DBSTOCKBRO",
    "DCAL", "DCBBANK", "DCM", "DCMFINSERV", "DCMNVL", "DCMSHRIRAM", "DCW", "DECCANCE", "DEEPAKFERT",
    "DEEPAKNTR", "DEEPINDS", "DELTACORP", "DELTAMAGNT", "DEN", "DENORA", "DENTALKART", "DHAMPURSUG", "DHANBANK",
    "DHANUKA", "DHARMAJ", "DHFL", "DHRUV", "DHUNINV", "DIAMONDYD", "DICIND", "DIGISPICE", "DIL", "DISHTV",
    "DIVISLAB", "DIXON", "DLF", "DLINKINDIA", "DMART", "DNAMEDIA", "DODLA", "DOLAT", "DOLLAR", "DOLPHINOFF",
    "DONEAR", "DPSCLTD", "DPTL", "DRCSYSTEMS", "DREDGECORP", "DRREDDY", "DSSL", "DTIL", "DUCON", "DVL",
    "DWARKESH", "DYNAMATECH", "DYNPRO", "EASEMYTRIP", "EASTSILK", "ECLERX", "EDELWEISS", "EDUCOMP", "EICHERMOT",
    "EIDPARRY", "EIHAHOTELS", "EIHOTEL", "EKC", "ELAND", "ELECON", "ELECTCAST", "ELECTHERM", "ELGIEQUIP",
    "ELGIRUBCO", "EMAMILTD", "EMAMIREAL", "EMCO", "EMKAY", "EMMBI", "EMUDHRA", "ENDURANCE", "ENERGYDEV",
    "ENGINERSIN", "ENIL", "EON", "EPL", "EQUITAS", "EQUITASBNK", "ERIS", "ESABINDIA", "ESCORTS", "ESSARSHPNG",
    "ESSENTIA", "ESTER", "EVEREADY", "EVERESTIND", "EXCEL", "EXCELINDUS", "EXIDEIND", "EXPLEOSOL", "EXXARO",
    "FACT", "FAIRCHEMOR", "FCL", "FCONSUMER", "FCSSOFT", "FDC", "FEDERALBNK", "FEL", "FELDVR"
    # Extend this list up to 500 tickers
]

nse_500_symbols = [symbol + ".NS" for symbol in nse_500_symbols]

# Master filter
with st.sidebar:
    st.header("\U0001F4CB Filters")
    st.markdown("""Customize your analysis with dynamic filters below:""")
    master_symbols = st.multiselect("\U0001F50D Select Stocks (Master Filter)", options=nse_500_symbols, default=["RELIANCE.NS", "TCS.NS", "INFY.NS"], key="master_symbols")
    display_period = st.selectbox("Time Period", ["1mo", "3mo", "6mo", "1y", "5y"], index=1, key="display_period")
    compare_type = st.radio("Compare By", ["Top Gainers", "Top Losers"], horizontal=True, key="compare_type")
    show_raw_data = st.checkbox("\U0001F4DD Show Raw Data", key="show_raw_data")
    show_info = st.checkbox("\U0001F6C8 Show DataFrame Info", key="show_info")
    show_nulls = st.checkbox("\U0001F573 Show Null Summary", key="show_nulls")
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
            "Change (%)": round(change, 2)
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
