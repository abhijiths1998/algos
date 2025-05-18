import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import io
from prophet import Prophet
# import smtplib # Not used in the current version, can be re-integrated for alerts
# from email.message import EmailMessage # Not used
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from urllib.parse import urlparse, parse_qs 
from kiteconnect import KiteConnect

# Set wide layout with stylish sidebar
st.set_page_config(page_title="📊 NSE Enhanced Dashboard", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
    <style>
        .big-font { font-size:24px !important; }
        .stButton>button { background-color: #0072C6; color: white; border-radius: 5px; padding: 0.4rem 1rem;}
        .stButton>button:hover { background-color: #005ea0; color: white; }
        .stSlider>div>div>div>div { background: #0072C6; }
        .block-container { padding-top: 1rem; padding-bottom: 2rem; padding-left: 2rem; padding-right: 2rem;}
        .sidebar .sidebar-content { background-color: #f0f2f6; }
        h1, h2, h3 { color: #003366; }
    </style>
""", unsafe_allow_html=True)

st.title("📊 NSE Enhanced Stock Analysis Dashboard")
st.markdown("""
Welcome! Analyze top Indian stocks with enhanced visualizations and configurable metrics.
Select stocks, date ranges, and explore detailed insights.
---
""")

# Top NSE symbols (cleaned and sorted)
nse_symbols_raw = [
    "3MINDIA.NS", "AARTIIND.NS", "AAVAS.NS", "ABB.NS", "ABBOTINDIA.NS", "ABCAPITAL.NS", "ABFRL.NS", "ACC.NS", "ADANIENT.NS",
    "ADANIPORTS.NS", "ADANIPOWER.NS", "ADANITOTGAS.NS", "ADANIENSOL.NS", "ADANIGREEN.NS", "AIAENG.NS", "AJANTPHARM.NS",
    "ALKEM.NS", "APLLTD.NS", "AMARAJABAT.NS", "AMBUJACEM.NS", "APOLLOHOSP.NS", "APOLLOTYRE.NS", "APARINDS.NS", "APLAPOLLO.NS",
    "ASIANPAINT.NS", "ASTRAL.NS", "ATUL.NS", "AUBANK.NS", "AUROPHARMA.NS", "AXISBANK.NS", "BAJAJ-AUTO.NS", "BAJFINANCE.NS",
    "BAJAJFINSV.NS", "BAJAJHLDNG.NS", "BALKRISIND.NS", "BANDHANBNK.NS", "BANKBARODA.NS", "BANKINDIA.NS", "BATAINDIA.NS",
    "BAYERCROP.NS", "BERGEPAINT.NS", "BEL.NS", "BHARATFORG.NS", "BHARTIARTL.NS", "BHEL.NS", "BIOCON.NS", "BLUEDART.NS",
    "BBTC.NS", "BOSCHLTD.NS", "BPCL.NS", "BRITANNIA.NS", "CANBK.NS", "CASTROLIND.NS", "CENTRALBK.NS", "CHOLAFIN.NS",
    "CIPLA.NS", "COALINDIA.NS", "COFORGE.NS", "COLPAL.NS", "CONCOR.NS", "COROMANDEL.NS", "CROMPTON.NS", "DABUR.NS",
    "DALBHARAT.NS", "DIVISLAB.NS", "DIXON.NS", "DLF.NS", "DRREDDY.NS", "EICHERMOT.NS", "ESCORTS.NS", "GAIL.NS", "GLAND.NS",
    "GODREJCP.NS", "GODREJPROP.NS", "GRASIM.NS", "GUJGASLTD.NS", "HAVELLS.NS", "HCLTECH.NS", "HDFCAMC.NS", "HDFCBANK.NS",
    "HDFCLIFE.NS", "HEROMOTOCO.NS", "HINDALCO.NS", "HINDPETRO.NS", "HINDUNILVR.NS", "HINDZINC.NS", "HONAUT.NS",
    "IBULHSGFIN.NS", "ICICIBANK.NS", "ICICIGI.NS", "ICICIPRULI.NS", "IDBI.NS", "IDFCFIRSTB.NS", "IGL.NS", "INDHOTEL.NS",
    "INDIAMART.NS", "INDIGO.NS", "INDUSINDBK.NS", "INDUSTOWER.NS", "INFY.NS", "IOC.NS", "IRCTC.NS", "ITC.NS", "ASHOKLEY.NS",
    "JINDALSTEL.NS", "JSWENERGY.NS", "JSWSTEEL.NS", "JUBLFOOD.NS", "KOTAKBANK.NS", "L&TFH.NS", "LALPATHLAB.NS",
    "LICHSGFIN.NS", "LTI.NS", "LTTS.NS", "M&M.NS", "M&MFIN.NS", "MANAPPURAM.NS", "MARICO.NS", "MARUTI.NS", "MCDOWELL-N.NS",
    "MCX.NS", "METROBRANDS.NS", "MFSL.NS", "MGL.NS", "MINDTREE.NS", "MOTILALFSL.NS", "MPHASIS.NS", "MRF.NS", "MUTHOOTFIN.NS",
    "NAM-INDIA.NS", "NATCOPHARM.NS", "NATIONALUM.NS", "NAVINFLUOR.NS", "NBCC.NS", "NESTLEIND.NS", "NETWORK18.NS", "NHPC.NS",
    "NMDC.NS", "NTPC.NS", "OBEROIRLTY.NS", "OFSS.NS", "ONGC.NS", "PAGEIND.NS", "PEL.NS", "PETRONET.NS", "PFC.NS",
    "PIDILITIND.NS", "PIIND.NS", "PNB.NS", "POLYCAB.NS", "POWERGRID.NS", "PVRINOX.NS", "RAMCOCEM.NS", "RBLBANK.NS",
    "RECLTD.NS", "RELIANCE.NS", "SBICARD.NS", "SBILIFE.NS", "SBIN.NS", "SHREECEM.NS", "SIEMENS.NS", "SRF.NS", "SRTRANSFIN.NS",
    "SUNPHARMA.NS", "SUNTV.NS", "TATACHEM.NS", "TATACONSUM.NS", "TATAMOTORS.NS", "TATAPOWER.NS", "TATASTEEL.NS", "TCS.NS",
    "TECHM.NS", "TITAN.NS", "TORNTPHARM.NS", "TORNTPOWER.NS", "TRENT.NS", "TVSMOTOR.NS", "UBL.NS", "ULTRACEMCO.NS", "UPL.NS",
    "VEDL.NS", "VGUARD.NS", "VOLTAS.NS", "WIPRO.NS", "YESBANK.NS", "ZEEL.NS", "ZYDUSLIFE.NS"
]
nse_500_symbols = sorted(list(set(nse_symbols_raw)))


# --- Sidebar Filters ---
with st.sidebar:
    st.header("🛠️ Controls & Filters")
    st.markdown("Customize your analysis:")

    default_symbols = ["RELIANCE.NS", "TCS.NS", "INFY.NS"]
    master_symbols = st.multiselect(
        "🔍 Select Stocks (Master Filter)",
        options=nse_500_symbols,
        default=[s for s in default_symbols if s in nse_500_symbols],
        key="master_symbols"
    )

    st.markdown("---")
    st.subheader("📅 Date Range")
    col_start_date, col_end_date = st.columns(2)
    # Default to a sensible range like last 3 months, or 1 year
    # Using datetime.date directly for default values
    default_start_date = datetime.date.today() - datetime.timedelta(days=365)
    default_end_date = datetime.date.today()

    start_date_val = col_start_date.date_input("Start Date", default_start_date, key="start_date")
    end_date_val = col_end_date.date_input("End Date", default_end_date, key="end_date")


    if start_date_val >= end_date_val:
        st.error("Error: End date must fall after start date.")
        st.stop()

    st.markdown("---")
    st.subheader("📊 Performance & Charting")
    compare_type = st.radio("Compare By", ["Top Gainers", "Top Losers"], horizontal=True, key="compare_type", index=0)
    chart_n = st.slider(f"Show Top/Bottom N for Chart", min_value=1, max_value=10, value=3, key="chart_top")

    st.markdown("---")
    st.subheader("💡 Recommendation Thresholds (%)")
    col_buy_thresh, col_sell_thresh = st.columns(2)
    strong_buy_threshold = col_buy_thresh.number_input("Strong Buy if drops >", min_value=0.0, value=7.0, step=0.5, format="%.1f")
    buy_threshold = col_buy_thresh.number_input("Buy if drops >", min_value=0.0, value=3.0, step=0.5, format="%.1f")
    strong_sell_threshold = col_sell_thresh.number_input("Strong Sell if gains >", min_value=0.0, value=10.0, step=0.5, format="%.1f")
    sell_threshold = col_sell_thresh.number_input("Sell if gains >", min_value=0.0, value=5.0, step=0.5, format="%.1f")


    st.markdown("---")
    st.subheader("⚙️ Display Options")
    show_raw_data = st.checkbox("📝 Show Raw Data Table", key="show_raw_data")
    show_nifty_comparison = st.checkbox("📈 Compare with NIFTY 50 (^NSEI)", value=False, key="show_nifty_comparison")
    
    with st.expander("🛠️ Advanced Data Views"):
        show_info = st.checkbox("🛈 Show DataFrame Info", key="show_info")
        show_nulls = st.checkbox("🕳 Show Null Summary", key="show_nulls")

    st.markdown("---")
    st.caption("Enhanced NSE Dashboard")

    st.header("🛠️ Controls & Filters")
    st.markdown("Customize your analysis:")

    selected_symbol_forecast = st.selectbox(
        "🔍 Select Stock for Forecast",
        options=nse_500_symbols,
        index=nse_500_symbols.index("RELIANCE.NS") if "RELIANCE.NS" in nse_500_symbols else 0,
        key="forecast_symbol"
    )

    st.markdown("---")

# Helper function to download DataFrame as CSV
def download_df_as_csv(df, filename="data.csv", label_prefix="📥 Download"):
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=f"{label_prefix} {filename}",
        data=csv,
        file_name=filename,
        mime='text/csv',
    )

# --- Data Fetching ---
if not master_symbols:
    st.warning("Please select at least one stock from the sidebar.")
    st.stop()

symbols_to_fetch = master_symbols[:]
if show_nifty_comparison:
    if "^NSEI" not in symbols_to_fetch: # Avoid duplicates if already somehow added
        symbols_to_fetch.append("^NSEI") # NIFTY 50 symbol

# Convert date objects to strings for yf.download if they are not already
str_start_date = start_date_val.strftime('%Y-%m-%d')
# yfinance end date is exclusive, so add 1 day if using date objects directly,
# or ensure the string format is correctly interpreted.
# For yf.download, passing date objects for start/end is fine.
str_end_date = (end_date_val + datetime.timedelta(days=1)).strftime('%Y-%m-%d')


with st.spinner(f"📥 Downloading data for {len(symbols_to_fetch)} symbol(s)..."):
    try:
        all_data_multi_level = yf.download(
            symbols_to_fetch,
            start=start_date_val, # Use date objects directly
            end=end_date_val + datetime.timedelta(days=1), # yfinance end date is exclusive
            group_by='ticker',
            progress=False
        )
    except Exception as e:
        st.error(f"Error downloading data: {e}")
        st.stop()

if all_data_multi_level.empty:
    st.error(f"No data found for the selected symbols and date range: {start_date_val.strftime('%Y-%m-%d')} to {end_date_val.strftime('%Y-%m-%d')}. Please check symbols or broaden the date range.")
    st.stop()

all_data = pd.DataFrame()
if len(symbols_to_fetch) == 1:
    if not all_data_multi_level.empty:
        _single_stock_df = all_data_multi_level.copy()
        # Ensure it's a DataFrame, not Series (can happen if only one column like 'Close' is fetched)
        if isinstance(_single_stock_df, pd.Series):
             _single_stock_df = _single_stock_df.to_frame()
        # Standardize column structure to MultiIndex for consistency
        _single_stock_df.columns = pd.MultiIndex.from_product([[symbols_to_fetch[0]], _single_stock_df.columns])
        all_data = _single_stock_df
else:
    all_data = all_data_multi_level

# Drop columns that are all NaN (can happen if a stock has no data for a period)
all_data.dropna(axis=1, how='all', inplace=True)

# Filter out symbols from master_symbols if they didn't return any data
valid_symbols_in_data = [s for s in master_symbols if s in all_data.columns.get_level_values(0)]
if not valid_symbols_in_data and not (show_nifty_comparison and "^NSEI" in all_data.columns.get_level_values(0)):
    st.error(f"None of the selected primary stocks returned data for the period.")
    st.stop()


if not isinstance(all_data.index, pd.DatetimeIndex):
    st.error("Data index is not datetime. Cannot proceed.")
    st.stop()

df_filtered = all_data.copy()

st.success(f"✅ Data loaded for period: **{start_date_val.strftime('%Y-%m-%d')}** to **{end_date_val.strftime('%Y-%m-%d')}**")

# --- Optional Raw Data Displays ---
if show_raw_data:
    with st.expander("📂 Filtered Raw Data (Last 7 weeks of selected period shown if data exceeds that)", expanded=False):
        display_df_raw = df_filtered.copy()
        # For MultiIndex columns, reset_index can make it more readable for download
        display_df_raw_downloadable = display_df_raw.copy()
        if isinstance(display_df_raw_downloadable.columns, pd.MultiIndex):
            display_df_raw_downloadable.columns = ['_'.join(col).strip() for col in display_df_raw_downloadable.columns.values]
        display_df_raw_downloadable = display_df_raw_downloadable.reset_index()


        if len(df_filtered) > 35 : 
             latest_date_in_df = df_filtered.index.max()
             start_display_date = latest_date_in_df - datetime.timedelta(weeks=7)
             display_df_raw = df_filtered[df_filtered.index >= start_display_date]
             st.caption(f"Displaying data from {start_display_date.date()} to {latest_date_in_df.date()}")
        st.dataframe(display_df_raw)
        download_df_as_csv(display_df_raw_downloadable, "filtered_stock_data.csv", label_prefix="📥 Download Raw")


if show_info:
    with st.expander("ℹ️ DataFrame Info", expanded=False):
        buffer = io.StringIO()
        df_filtered.info(buf=buffer)
        st.text(buffer.getvalue())

if show_nulls:
    with st.expander(" wojewódzkie Null Value Summary (Top 10 columns with nulls)", expanded=False):
        if isinstance(df_filtered.columns, pd.MultiIndex):
            nulls_overall = df_filtered.isna().sum().unstack(level=0).sum(axis=1).sort_values(ascending=False)
        else: # Single stock was fetched initially
            nulls_overall = df_filtered.isna().sum().sort_values(ascending=False)
        
        if nulls_overall.sum() == 0:
            st.write("No null values found in the dataset for the selected period.")
        else:
            st.dataframe(nulls_overall[nulls_overall > 0].head(10).to_frame(name="Null Count"))


# --- Individual Stock Deep Dive ---
st.markdown("---")
st.header("🔬 Individual Stock Deep Dive")

# Use valid_symbols_in_data for the deep dive selector
# Ensure default selection for deep_dive_stock is valid
deep_dive_options = [s for s in master_symbols if s in df_filtered.columns.get_level_values(0)]

if deep_dive_options:
    selected_stock_for_deep_dive = st.selectbox(
        "Select a stock for detailed analysis:",
        options=deep_dive_options,
        index=0 if deep_dive_options else -1, # Prevent error if empty
        key="deep_dive_stock"
    )

    if selected_stock_for_deep_dive: # Check if a stock is actually selected
        stock_ticker_obj = yf.Ticker(selected_stock_for_deep_dive)
        # Ensure the selected stock's data is available in df_filtered under the first level of MultiIndex
        if selected_stock_for_deep_dive in df_filtered.columns.get_level_values(0):
            stock_data_single = df_filtered[selected_stock_for_deep_dive]
        else:
            stock_data_single = pd.DataFrame() # Empty DataFrame if not found

        if stock_data_single.empty or not all(col in stock_data_single.columns for col in ['Open', 'High', 'Low', 'Close', 'Volume']):
            st.warning(f"No complete OHLCV data available for {selected_stock_for_deep_dive} in the selected period for deep dive.")
        else:
            with st.spinner(f"Fetching key metrics for {selected_stock_for_deep_dive}..."):
                try:
                    info = stock_ticker_obj.info
                except Exception as e:
                    info = {}
                    st.caption(f"Could not fetch some Ticker info for {selected_stock_for_deep_dive}: Request failed or info not available.")
            
            st.subheader(f"📈 Key Metrics & Chart for: {info.get('longName', selected_stock_for_deep_dive)}")
            # Key Metrics Display (as before)
            m_col1, m_col2, m_col3, m_col4 = st.columns(4)
            m_col1.metric("Market Cap", f"{info.get('marketCap', 'N/A'):,}" if isinstance(info.get('marketCap'), (int, float)) else "N/A")
            m_col2.metric("P/E Ratio", f"{info.get('trailingPE', 'N/A'):.2f}" if isinstance(info.get('trailingPE'), float) else "N/A")
            m_col3.metric("Beta", f"{info.get('beta', 'N/A'):.2f}" if isinstance(info.get('beta'), float) else "N/A")
            latest_close = stock_data_single['Close'].iloc[-1] if not stock_data_single['Close'].empty else "N/A"
            m_col4.metric("Latest Close", f"{latest_close:.2f}" if isinstance(latest_close, float) else "N/A")
            
            m_col5, m_col6, m_col7, m_col8 = st.columns(4)
            m_col5.metric("52 Week High", f"{info.get('fiftyTwoWeekHigh', 'N/A'):.2f}" if isinstance(info.get('fiftyTwoWeekHigh'), float) else "N/A")
            m_col6.metric("52 Week Low", f"{info.get('fiftyTwoWeekLow', 'N/A'):.2f}" if isinstance(info.get('fiftyTwoWeekLow'), float) else "N/A")
            m_col7.metric("Fwd Dividend", f"{info.get('forwardDividendRate', 'N/A')}" if info.get('forwardDividendRate') else "N/A")
            m_col8.metric("Fwd Div Yield", f"{info.get('dividendYield', 'N/A')*100:.2f}%" if isinstance(info.get('dividendYield'), float) else "N/A")


            st.markdown("#### Interactive Candlestick Chart with Moving Averages & Volume")
            chart_data = stock_data_single[['Open', 'High', 'Low', 'Close', 'Volume']].copy().dropna()
            chart_data.index.name = 'Date'
            
            # SMA Calculation
            sma_checkbox_cols = st.columns(2)
            show_sma20 = sma_checkbox_cols[0].checkbox("Show 20-Day SMA", value=True, key=f"sma20_{selected_stock_for_deep_dive}")
            show_sma50 = sma_checkbox_cols[1].checkbox("Show 50-Day SMA", value=True, key=f"sma50_{selected_stock_for_deep_dive}")

            if show_sma20:
                chart_data['SMA20'] = chart_data['Close'].rolling(window=20).mean()
            if show_sma50:
                chart_data['SMA50'] = chart_data['Close'].rolling(window=50).mean()

            if not chart_data.empty:
                try:
                    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                                        vertical_spacing=0.05, # Increased spacing a bit
                                        subplot_titles=(f'{selected_stock_for_deep_dive} Candlestick', 'Volume'),
                                        row_heights=[0.7, 0.3]) # Adjusted row heights

                    fig.add_trace(go.Candlestick(x=chart_data.index,
                                                 open=chart_data['Open'], high=chart_data['High'],
                                                 low=chart_data['Low'], close=chart_data['Close'],
                                                 name='Candlestick'), row=1, col=1)
                    if 'SMA20' in chart_data.columns:
                        fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data['SMA20'],
                                                 line=dict(color='blue', width=1), name='SMA 20'), row=1, col=1)
                    if 'SMA50' in chart_data.columns:
                        fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data['SMA50'],
                                                 line=dict(color='orange', width=1), name='SMA 50'), row=1, col=1)
                    fig.add_trace(go.Bar(x=chart_data.index, y=chart_data['Volume'], name='Volume', marker_color='rgba(100,149,237,0.6)'), row=2, col=1) # Cornflower blue for volume

                    fig.update_layout(
                        title_text=f"{info.get('shortName', selected_stock_for_deep_dive)} - Interactive Chart",
                        xaxis_title=None, # Remove x-axis title for cleaner look with shared axes
                        yaxis_title="Price (INR)",
                        xaxis_rangeslider_visible=False,
                        legend_title_text='Legend',
                        height=700, # Increased height
                        margin=dict(l=50, r=50, b=50, t=100), # Adjusted margins
                        hovermode="x unified" # Shows all data for a given x value
                    )
                    fig.update_xaxes(showticklabels=True, row=1, col=1) # Ensure x-axis ticks are shown on top plot if shared
                    fig.update_yaxes(title_text="Volume", row=2, col=1)
                    
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"Could not generate interactive candlestick chart for {selected_stock_for_deep_dive}: {e}")
                    st.line_chart(chart_data[['Close'] + [col for col in ['SMA20', 'SMA50'] if col in chart_data.columns]])
            else:
                st.info(f"Not enough data to plot interactive candlestick for {selected_stock_for_deep_dive}.")
else:
    st.info("Select stocks from the sidebar and ensure data is loaded to see individual analysis options.")


# --- Performance Summary ---
st.markdown("---")
st.header("💹 Stock Performance Summary")
performance = []

# Use only master_symbols for performance calculation, not ^NSEI
# Ensure symbols exist in the df_filtered columns after potential drops
valid_master_symbols_for_perf = [s for s in master_symbols if s in df_filtered.columns.get_level_values(0)]

for symbol in valid_master_symbols_for_perf:
    try:
        data_close = df_filtered[(symbol, 'Close')].dropna()
        data_volume = df_filtered[(symbol, 'Volume')].dropna()

        if len(data_close) < 2:
            st.caption(f"Not enough data points for {symbol} to calculate performance.")
            continue

        start_price = data_close.iloc[0]
        end_price = data_close.iloc[-1]
        change = ((end_price - start_price) / start_price) * 100
        avg_volume = data_volume.mean()

        rec = "Hold"
        if change <= -strong_buy_threshold: rec = "Strong Buy"
        elif change <= -buy_threshold: rec = "Buy"
        elif change >= strong_sell_threshold: rec = "Strong Sell"
        elif change >= sell_threshold: rec = "Sell"

        performance.append({
            "Symbol": symbol,
            "Start Price": round(start_price, 2), "End Price": round(end_price, 2),
            "Change (%)": round(change, 2), "Avg Volume": f"{avg_volume:,.0f}",
            "Recommendation": rec
        })
    except KeyError:
        st.caption(f"Data columns ('Close' or 'Volume') missing for {symbol}, skipping performance.")
    except Exception as e:
        st.caption(f"Error calculating performance for {symbol}: {e}")

if performance:
    perf_df = pd.DataFrame(performance).sort_values(by="Change (%)", ascending=(compare_type == "Top Losers"))
    st.dataframe(perf_df, height=min(300, (len(perf_df) + 1) * 35 + 5), use_container_width=True)
    download_df_as_csv(perf_df, "stock_performance_summary.csv", label_prefix="📥 Download Performance")

    st.markdown("---")
    st.subheader("🏆 Top/Bottom 5 Performers")
    # ... (Top/Bottom Performers table display - same as before)
    sorted_perf_gainers = perf_df.sort_values(by="Change (%)", ascending=False).reset_index(drop=True)
    top_gainers = sorted_perf_gainers.head(5)

    sorted_perf_losers = perf_df.sort_values(by="Change (%)", ascending=True).reset_index(drop=True)
    top_losers = sorted_perf_losers.head(5)
    
    common_symbols_perf = set(top_gainers["Symbol"]).intersection(set(top_losers["Symbol"]))
    top_losers_display = top_losers[~top_losers["Symbol"].isin(common_symbols_perf)] if len(valid_master_symbols_for_perf) > 5 else top_losers

    col1_perf, col2_perf = st.columns(2)
    with col1_perf:
        st.markdown("#### 🔼 Top 5 Gainers")
        st.dataframe(top_gainers, use_container_width=True)
    with col2_perf:
        st.markdown("#### 🔽 Top 5 Losers")
        st.dataframe(top_losers_display, use_container_width=True)


    st.markdown("---")
    st.subheader(f"📉 Price Trends for Top/Bottom {chart_n} Performers")
    # ... (Price trends line chart - same as before)
    if compare_type == "Top Gainers":
        chart_symbols_trends = perf_df.sort_values(by="Change (%)", ascending=False).head(chart_n)['Symbol'].tolist()
    else: # Top Losers
        chart_symbols_trends = perf_df.sort_values(by="Change (%)", ascending=True).head(chart_n)['Symbol'].tolist()

    chart_df_trends = pd.DataFrame()
    for symbol_trend in chart_symbols_trends:
        try:
            series = df_filtered[(symbol_trend, "Close")].dropna()
            if not series.empty: chart_df_trends[symbol_trend] = series
        except Exception: continue
    
    if not chart_df_trends.empty: st.line_chart(chart_df_trends)
    else: st.info("No valid data for price trends chart.")


    st.markdown("---")
    st.subheader(f"📊 Visual Comparison: Price Trends vs. % Change (Top/Bottom {chart_n})")
    # ... (Area and Bar chart comparison - same as before)
    chart_area_df_comp = chart_df_trends.copy() 
    chart_bar_df_comp = perf_df[perf_df['Symbol'].isin(chart_symbols_trends)].set_index("Symbol")["Change (%)"]
    area_col_comp, bar_col_comp = st.columns(2)
    with area_col_comp:
        st.markdown("**📈 Area Chart - Price Trends**")
        if not chart_area_df_comp.empty: st.area_chart(chart_area_df_comp)
        else: st.info("No data for area chart.")
    with bar_col_comp:
        st.markdown("**📊 Bar Chart - % Change**")
        if not chart_bar_df_comp.empty: st.bar_chart(chart_bar_df_comp)
        else: st.info("No data for bar chart.")
else:
    st.info("No performance data to display. Check stock selections and date range.")


# --- NIFTY 50 Comparison ---
if show_nifty_comparison and "^NSEI" in df_filtered.columns.get_level_values(0):
    st.markdown("---")
    st.header("🆚 NIFTY 50 Performance Comparison")
    nifty_data = df_filtered[("^NSEI", "Close")].dropna()
    if not nifty_data.empty:
        normalized_df = pd.DataFrame()
        normalized_df["NIFTY 50"] = (nifty_data / nifty_data.iloc[0]) * 100
        
        for symbol_norm in valid_master_symbols_for_perf: # Use valid symbols that have data
            try:
                stock_close_data = df_filtered[(symbol_norm, "Close")].dropna()
                if not stock_close_data.empty:
                    normalized_df[symbol_norm] = (stock_close_data / stock_close_data.iloc[0]) * 100
            except Exception: continue
        
        if len(normalized_df.columns) > 1:
            st.line_chart(normalized_df)
            st.caption("Performance normalized to 100 at the start of the selected period.")
        else:
            st.info("Not enough stock data (or only NIFTY 50) to compare.")
    else:
        st.warning("NIFTY 50 data could not be loaded or is empty for the selected period.")
st.markdown("---")
st.header("🔮 Stock Price Forecasting")
st.subheader("📆 Forecasting Date Range")
forecast_start = st.date_input("Start Date for Forecast", default_start_date, key="start_date_forecast")
forecast_end = st.date_input("End Date for Forecast", default_end_date, key="end_date_forecast")

if st.session_state.get("forecast_symbol"):
    forecast_symbol = st.session_state.forecast_symbol
    start_date_val = forecast_start
    end_date_val = forecast_end


    with st.spinner(f"📈 Fetching data for {forecast_symbol} for forecasting..."):
        forecast_data_raw = yf.download(
            forecast_symbol,
            start=start_date_val,
            end=end_date_val + datetime.timedelta(days=1),
            progress=False
        )

    if forecast_data_raw.empty:
        st.error(f"No data found for {forecast_symbol} in the selected date range for forecasting.")
    else:
        # Ensure 'Close' column exists
        if 'Close' not in forecast_data_raw.columns:
            st.error(f"Error: 'Close' data not found for {forecast_symbol}.")
        else:
            # Create the forecast DataFrame correctly
            forecast_df = forecast_data_raw[['Close']].copy()
            forecast_df['ds'] = forecast_data_raw.index
            forecast_df['y'] = forecast_df['Close']
            forecast_df = forecast_df[['ds', 'y']]


            # Train Prophet model
            with st.spinner(f"⚙️ Training Prophet model for {forecast_symbol}..."):
                model = Prophet()
                model.fit(forecast_df)

            # Make future dataframes for different forecast horizons
            future_3m = model.make_future_dataframe(periods=90) # approx. 3 months
            future_6m = model.make_future_dataframe(periods=180) # approx. 6 months
            future_1y = model.make_future_dataframe(periods=365) # approx. 1 year
            future_5y = model.make_future_dataframe(periods=365 * 5) # approx. 5 years

            # Make predictions
            with st.spinner(f"🔮 Making forecasts for {forecast_symbol}..."):
                forecast_3m = model.predict(future_3m)
                forecast_6m = model.predict(future_6m)
                forecast_1y = model.predict(future_1y)
                forecast_5y = model.predict(future_5y)

            st.subheader(f"📈 Price Forecast for {forecast_symbol}")

            forecast_months = st.slider("Show Last N Months of Forecast", min_value=1, max_value=60, value=24) # Up to 5 years

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=forecast_df['ds'], y=forecast_df['y'], mode='lines', name='Historical Close Price'))

            # Filter and add forecast traces
            forecast_3m_filtered = forecast_3m.tail(forecast_months)
            fig.add_trace(go.Scatter(x=forecast_3m_filtered['ds'], y=forecast_3m_filtered['yhat'], mode='lines', name='Forecast (3 Months)'))

            forecast_6m_filtered = forecast_6m.tail(forecast_months)
            fig.add_trace(go.Scatter(x=forecast_6m_filtered['ds'], y=forecast_6m_filtered['yhat'], mode='lines', name='Forecast (6 Months)'))

            forecast_1y_filtered = forecast_1y.tail(forecast_months)
            fig.add_trace(go.Scatter(x=forecast_1y_filtered['ds'], y=forecast_1y_filtered['yhat'], mode='lines', name='Forecast (1 Year)'))

            forecast_5y_filtered = forecast_5y.tail(forecast_months)
            fig.add_trace(go.Scatter(x=forecast_5y_filtered['ds'], y=forecast_5y_filtered['yhat'], mode='lines', name='Forecast (5 Years)'))

            fig.update_layout(title='Historical Price vs. Forecasted Price',
                              xaxis_title='Date',
                              yaxis_title='Price',
                              legend_title='Forecast Horizon')
            st.plotly_chart(fig, use_container_width=True)

            st.info("Note: These forecasts are based on historical data and the Prophet model. They are not financial advice and should be interpreted with caution.")
else:
    st.warning("No filters given!!")

# --- EDA and Recommendation Summary ---
st.markdown("---")
st.header("💡 Recommendation Insights")
if performance: 
    rec_col1, rec_col2, rec_col3 = st.columns(3)
    # ... (Recommendation display logic - same as before)
    strong_buy_rec_df = perf_df[perf_df["Recommendation"] == "Strong Buy"]
    if not strong_buy_rec_df.empty:
        with rec_col1.expander("💎 Strong Buy Candidates", expanded=True): st.dataframe(strong_buy_rec_df, use_container_width=True)
    else: rec_col1.info("No 'Strong Buy' signals.")

    buy_rec_df = perf_df[perf_df["Recommendation"] == "Buy"]
    if not buy_rec_df.empty:
        with rec_col1.expander("🛒 Buy Candidates", expanded=True): st.dataframe(buy_rec_df, use_container_width=True)
    else: rec_col1.info("No 'Buy' signals.")

    sell_rec_df = perf_df[perf_df["Recommendation"] == "Sell"]
    if not sell_rec_df.empty:
        with rec_col2.expander("💸 Sell Candidates", expanded=False): st.dataframe(sell_rec_df, use_container_width=True)
    else: rec_col2.info("No 'Sell' signals.")

    strong_sell_rec_df = perf_df[perf_df["Recommendation"] == "Strong Sell"]
    if not strong_sell_rec_df.empty:
        with rec_col2.expander("🛑 Strong Sell Candidates", expanded=False): st.dataframe(strong_sell_rec_df, use_container_width=True)
    else: rec_col2.info("No 'Strong Sell' signals.")

    hold_rec_df = perf_df[perf_df["Recommendation"] == "Hold"]
    if not hold_rec_df.empty:
        with rec_col3.expander("⚖️ Hold Candidates", expanded=True): st.dataframe(hold_rec_df, use_container_width=True)
    else: rec_col3.info("No 'Hold' signals.")
else:
    st.info("Run analysis to see recommendation insights.")

st.markdown("---")
st.info("Disclaimer: This dashboard is for informational and educational purposes only. Not financial advice.")


# --- Streamlit UI ---
st.title("Simple Zerodha Trading Bot (Manual Token Generation)")

st.sidebar.header("API Credentials")
api_key = st.sidebar.text_input("Enter Zerodha API Key")
api_secret = st.sidebar.text_input("Enter Zerodha API Secret", type="password")

# --- WARNING ---
st.warning("SECURITY WARNING: Handling API Secret and Access Token directly is highly insecure. "
           "Use this ONLY for local testing. For production, implement Zerodha's OAuth login flow securely.")
# --- End WARNING ---

kite = None # Initialize kite as None
access_token = None # Initialize access_token

# --- Manual Token Generation Flow ---
st.header("Generate Access Token")
st.info("Follow these steps to generate your Access Token:")

if api_key and api_secret:
    try:
        # Step 1: Generate Login URL
        temp_kite = KiteConnect(api_key=api_key)
        # You need to configure this redirect_uri in your Zerodha Developer Console
        # For local testing, you can use http://localhost:8501/ (the default Streamlit address)
        # or a specific path like http://localhost:8501/callback if your web server handles routing.
        # In a real app, this must be a URL your server handles.
        redirect_uri = "http://localhost:8501/" # Replace with your configured redirect URI

        login_url = temp_kite.login_url() # pykiteconnect automatically adds redirect_uri if configured
        st.write(f"1. Click the link below to log in to Zerodha and authorize your app:")
        st.markdown(f"**[Login to Zerodha]({login_url})**")
        st.write(f"   (Your configured redirect URI: `{temp_kite._redirect_url}`)") # Display configured redirect URI

        st.write("2. After logging in, you will be redirected to your redirect URI. The URL in your browser will look like: `YOUR_REDIRECT_URI?request_token=YOUR_REQUEST_TOKEN&status=success`")
        st.write("3. Copy the value of `request_token` from the redirected URL.")

        request_token = st.text_input("4. Paste the Request Token here:")

        if request_token:
            if st.button("Generate Access Token from Request Token"):
                try:
                    # Step 5 & 6: Exchange request_token for access_token
                    data = temp_kite.generate_session(request_token, api_secret=api_secret)
                    access_token = data["access_token"]

                    st.success("Access Token generated successfully!")
                    st.write(f"Your Access Token (Keep this secure!): `{access_token}`")

                    # Store the access token in session state if you want to persist it across reruns
                    # st.session_state['access_token'] = access_token

                    # Now you can initialize the main kite object for trading
                    kite = KiteConnect(api_key=api_key)
                    kite.set_access_token(access_token)
                    st.sidebar.success("Kite Connect initialized with new Access Token.")

                    try:
                        user_profile = kite.profile()
                        st.sidebar.write(f"Logged in as: {user_profile['user_name']}")
                    except Exception as e:
                        st.sidebar.error(f"Error verifying connection with new token: {e}. Access Token might be invalid or expired.")
                        kite = None # Invalidate kite if connection fails


                except Exception as e:
                    st.error(f"Error generating Access Token: {e}")
                    st.info("Ensure your API Key, Secret, and Request Token are correct and the token hasn't expired.")
        else:
            st.info("Paste the Request Token to generate the Access Token.")

    except Exception as e:
        st.error(f"Error generating login URL: {e}")
        st.info("Please check your API Key.")

# --- Check if kite object is initialized for trading sections ---
if kite:
    st.header("Trading Functionality")

    # --- Helper Function to get Instrument Token ---
    @st.cache_data # Cache the instrument data to avoid refetching on every interaction
    def get_instruments(exchange="NSE"):
        try:
            instruments = kite.instruments([exchange])
            # Convert to DataFrame for easier searching
            df = pd.DataFrame(instruments)
            return df
        except Exception as e:
            st.error(f"Error fetching instruments for {exchange}: {e}")
            return pd.DataFrame()

    st.header("Account Information")

    # 3. Show the balance
    if st.button("Show Balance"):
        try:
            margins = kite.margins()
            equity_margin = margins.get('equity', {})
            available_cash = equity_margin.get('available', {}).get('live_margin', 'N/A')
            st.write(f"**Available Equity Margin:** ₹{available_cash}")
        except Exception as e:
            st.error(f"Error fetching balance: {e}")

    st.header("Trade Execution")

    st.sidebar.header("Trade Settings")
    exchange = st.sidebar.selectbox("Select Exchange", ["NSE", "BSE", "NFO", "MCX"], index=0)
    instrument_df = get_instruments(exchange)

    # 2. Get the stock symbol as input
    tradingsymbol = st.text_input("Enter Stock Symbol (e.g., RELIANCE, TCS)").upper()

    # Find instrument token for the given symbol and exchange
    instrument_token = None
    if tradingsymbol and not instrument_df.empty:
        instrument_row = instrument_df[(instrument_df['tradingsymbol'] == tradingsymbol) & (instrument_df['exchange'] == exchange)]
        if not instrument_row.empty:
            instrument_token = instrument_row.iloc[0]['instrument_token']
            # st.write(f"Found Instrument Token for {tradingsymbol} on {exchange}: {instrument_token}")
        else:
            st.warning(f"Could not find instrument token for {tradingsymbol} on {exchange}. Check the symbol and exchange.")

    # Placeholder for quantity input
    quantity = st.number_input("Enter Quantity", min_value=1, value=1, step=1)

    # 3. Based on the rule of 5% diff show buy or sell
    st.header("Trading Suggestion (5% Difference Rule)")

    if tradingsymbol and instrument_token:
        try:
            # Get current LTP
            ltp_data = kite.ltp([f"{exchange}:{tradingsymbol}"])
            current_ltp = None
            if f"{exchange}:{tradingsymbol}" in ltp_data:
                current_ltp = ltp_data[f"{exchange}:{tradingsymbol}"]['last_price']
                st.write(f"Current Last Traded Price (LTP) for {tradingsymbol}: ₹{current_ltp}")
            else:
                 st.warning(f"Could not fetch LTP for {tradingsymbol} on {exchange}. Cannot apply 5% rule.")


            # Fetch holdings to check average price if selling
            holdings = kite.holdings()
            stock_holding = next((item for item in holdings if item['tradingsymbol'] == tradingsymbol and item['exchange'] == exchange), None)

            suggestion = "Analyze..."
            action = None
            avg_buy_price = None
            held_quantity = 0

            if stock_holding:
                avg_buy_price = stock_holding['average_price']
                held_quantity = stock_holding['quantity']
                st.write(f"Your Average Buy Price for {tradingsymbol}: ₹{avg_buy_price:.2f}")
                st.write(f"Quantity Held: {held_quantity}")

                # 5% Sell Rule: If LTP is 5% or more above the average buy price
                if current_ltp is not None and current_ltp >= avg_buy_price * 1.05:
                    suggestion = f"**SELL:** LTP (₹{current_ltp}) is >= 5% above Average Buy Price (₹{avg_buy_price * 1.05:.2f})."
                    action = "SELL"
                elif current_ltp is not None:
                    suggestion = f"**HOLD/Analyze:** LTP (₹{current_ltp}) is not 5% or more above Average Buy Price (₹{avg_buy_price:.2f})."
                else:
                     suggestion = "Cannot apply 5% sell rule: Could not fetch LTP."

            else:
                # Simple Placeholder for Buy Logic (Needs a real strategy)
                suggestion = f"No holdings found for {tradingsymbol}. Consider a BUY based on your strategy."
                # Decide if we show a buy button based on *some* condition or just allow manual buy via button below
                # For simplicity, let's just show the buy button regardless if the instrument is found

            st.markdown(suggestion)

            # 4. Using zerodha api buy or sell the stock
            buy_col, sell_col = st.columns(2)

            with buy_col:
                 # Disable buy button if no symbol/quantity or LTP not available
                 if st.button(f"Execute BUY Order for {tradingsymbol}", disabled=not tradingsymbol or quantity <= 0 or current_ltp is None):
                     try:
                         st.info(f"Placing BUY order for {quantity} shares of {tradingsymbol}...")
                         order_id = kite.place_order(
                             tradingsymbol=tradingsymbol,
                             exchange=exchange,
                             transaction_type=kite.TRANSACTION_TYPE_BUY,
                             quantity=quantity,
                             variety=kite.VARIETY_REGULAR, # or kite.VARIETY_MIS, etc.
                             order_type=kite.ORDER_TYPE_MARKET, # or kite.ORDER_TYPE_LIMIT, etc.
                             product=kite.PRODUCT_CNC # or kite.PRODUCT_MIS, etc.
                         )
                         st.success(f"BUY order placed successfully! Order ID: {order_id}")
                         st.info("Check your Zerodha Kite terminal for order status.")
                     except Exception as e:
                         st.error(f"Error placing BUY order: {e}")

            with sell_col:
                 # Disable sell button if no symbol/quantity, no holdings, LTP not available, or 5% rule not met
                 if st.button(f"Execute SELL Order for {tradingsymbol}", disabled=action != "SELL" or quantity <= 0 or held_quantity <= 0 or current_ltp is None):
                      if quantity > held_quantity:
                          st.warning(f"Attempting to sell {quantity} but only {held_quantity} held. Adjusting quantity to {held_quantity}.")
                          sell_quantity = held_quantity
                      else:
                          sell_quantity = quantity

                      if sell_quantity > 0:
                          try:
                              st.info(f"Placing SELL order for {sell_quantity} shares of {tradingsymbol}...")
                              # Place SELL order
                              order_id = kite.place_order(
                                  tradingsymbol=tradingsymbol,
                                  exchange=exchange,
                                  transaction_type=kite.TRANSACTION_TYPE_SELL,
                                  quantity=sell_quantity,
                                  variety=kite.VARIETY_REGULAR, # or kite.VARIETY_MIS, etc.
                                  order_type=kite.ORDER_TYPE_MARKET, # or kite.ORDER_TYPE_LIMIT, etc.
                                  product=kite.PRODUCT_CNC # or kite.PRODUCT_MIS, etc.
                              )
                              st.success(f"SELL order placed successfully! Order ID: {order_id}")
                              st.info("Check your Zerodha Kite terminal for order status.")
                          except Exception as e:
                              st.error(f"Error placing SELL order: {e}")
                      else:
                           st.warning("Cannot place SELL order: Quantity to sell is zero.")


        except Exception as e:
            st.error(f"An error occurred during analysis: {e}")

    st.markdown("---")
    st.info("Disclaimer: This is a simplified example for educational purposes. "
            "Trading involves risk. Use this code responsibly and at your own risk. "
            "Implement proper error handling, security measures (especially for credentials), "
            " and a robust trading strategy for any real trading.")

    # --- Optional: Display Holdings ---
    st.header("Your Holdings")
    if st.button("Show Holdings"):
        try:
            holdings_data = kite.holdings()
            if holdings_data:
                holdings_df = pd.DataFrame(holdings_data)
                st.dataframe(holdings_df)
            else:
                st.info("No holdings found in your portfolio.")
        except Exception as e:
            st.error(f"Error fetching holdings: {e}")

else:
    st.info("Please provide your API Key and Secret in the sidebar and generate an Access token")
