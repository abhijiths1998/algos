import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import io
# import smtplib # Not used in the current version, can be re-integrated for alerts
# from email.message import EmailMessage # Not used
import matplotlib.pyplot as plt
import mplfinance as mpf # For candlestick charts

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
    start_date_val = col_start_date.date_input("Start Date", datetime.date.today() - datetime.timedelta(days=90), key="start_date")
    end_date_val = col_end_date.date_input("End Date", datetime.date.today(), key="end_date")

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
    # Advanced/Debug options can be in an expander
    with st.expander("🛠️ Advanced Data Views"):
        show_info = st.checkbox("🛈 Show DataFrame Info", key="show_info")
        show_nulls = st.checkbox("🕳 Show Null Summary", key="show_nulls")

    st.markdown("---")
    st.caption("Enhanced NSE Dashboard")

# Helper function to download DataFrame as CSV
def download_df_as_csv(df, filename="data.csv"):
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=f"📥 Download {filename}",
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
    symbols_to_fetch.append("^NSEI") # NIFTY 50 symbol

with st.spinner(f"📥 Downloading data for {len(symbols_to_fetch)} symbol(s)..."):
    try:
        all_data_multi_level = yf.download(
            symbols_to_fetch,
            start=start_date_val,
            end=end_date_val + datetime.timedelta(days=1), # yfinance end date is exclusive
            group_by='ticker',
            progress=False
        )
    except Exception as e:
        st.error(f"Error downloading data: {e}")
        st.stop()

if all_data_multi_level.empty:
    st.error(f"No data found for the selected symbols and date range. Please check symbols or broaden the date range.")
    st.stop()

# For single stock download, yfinance returns a DataFrame, not multi-index.
# For multiple stocks, it returns a multi-index DataFrame.
# We need to handle both to get a consistent structure.
all_data = pd.DataFrame()
if len(symbols_to_fetch) == 1:
    # If only one symbol, yf.download might not create a multi-level column index
    # We need to reshape it to be consistent
    if not all_data_multi_level.empty:
        _single_stock_df = all_data_multi_level.copy()
        _single_stock_df.columns = pd.MultiIndex.from_product([[symbols_to_fetch[0]], _single_stock_df.columns])
        all_data = _single_stock_df
else:
    all_data = all_data_multi_level

if not isinstance(all_data.index, pd.DatetimeIndex):
    st.error("Data index is not datetime. Cannot proceed.")
    st.stop()

df_filtered = all_data.copy() # Data is already filtered by date range from yf.download

st.success(f"✅ Data loaded for period: **{start_date_val.strftime('%Y-%m-%d')}** to **{end_date_val.strftime('%Y-%m-%d')}**")

# --- Optional Raw Data Displays ---
if show_raw_data:
    with st.expander("📂 Filtered Raw Data (Last 7 weeks of selected period shown if data exceeds that)", expanded=False):
        # If df_filtered is large, show a sample or last N rows
        display_df = df_filtered.copy()
        if len(df_filtered) > 35 : # Approx 7 weeks * 5 trading days
             latest_date_in_df = df_filtered.index.max()
             start_display_date = latest_date_in_df - datetime.timedelta(weeks=7)
             display_df = df_filtered[df_filtered.index >= start_display_date]
             st.caption(f"Displaying data from {start_display_date.date()} to {latest_date_in_df.date()}")

        st.dataframe(display_df)
        download_df_as_csv(df_filtered.reset_index(), "filtered_stock_data.csv")


if show_info:
    with st.expander("ℹ️ DataFrame Info", expanded=False):
        buffer = io.StringIO()
        df_filtered.info(buf=buffer)
        st.text(buffer.getvalue())

if show_nulls:
    with st.expander(" wojewódzkie Null Value Summary (Top 10 columns with nulls)", expanded=False):
        nulls = df_filtered.isna().sum()
        # For multi-index columns, sum() might return a series. We want sum over all entries.
        if isinstance(df_filtered.columns, pd.MultiIndex):
            nulls_overall = df_filtered.stack(level=0).isna().sum().sort_values(ascending=False)
        else:
            nulls_overall = nulls.sort_values(ascending=False)

        if nulls_overall.sum() == 0:
            st.write("No null values found in the dataset for the selected period.")
        else:
            st.dataframe(nulls_overall[nulls_overall > 0].head(10))


# --- Individual Stock Deep Dive ---
st.markdown("---")
st.header("🔬 Individual Stock Deep Dive")
if master_symbols:
    selected_stock_for_deep_dive = st.selectbox(
        "Select a stock for detailed analysis:",
        options=master_symbols,
        index=0,
        key="deep_dive_stock"
    )

    if selected_stock_for_deep_dive:
        stock_ticker_obj = yf.Ticker(selected_stock_for_deep_dive)
        stock_data_single = df_filtered.get(selected_stock_for_deep_dive)

        if stock_data_single is None or stock_data_single.empty:
            st.warning(f"No data available for {selected_stock_for_deep_dive} in the selected period for deep dive.")
        else:
            # Display Key Metrics
            with st.spinner(f"Fetching key metrics for {selected_stock_for_deep_dive}..."):
                try:
                    info = stock_ticker_obj.info
                except Exception as e:
                    info = {}
                    st.caption(f"Could not fetch some Ticker info for {selected_stock_for_deep_dive}: {e}")


            st.subheader(f"📈 Key Metrics & Chart for: {info.get('longName', selected_stock_for_deep_dive)}")

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
            m_col8.metric("Fwd Div Yield", f"{info.get('forwardPE', 'N/A')}" if info.get('forwardPE') else "N/A")


            # Candlestick Chart
            st.markdown("#### Candlestick Chart with Moving Averages & Volume")
            chart_data = stock_data_single[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
            chart_data.index.name = 'Date'

            mav_options = []
            if st.checkbox("Show 20-Day SMA", value=True, key=f"sma20_{selected_stock_for_deep_dive}"):
                chart_data['SMA20'] = chart_data['Close'].rolling(window=20).mean()
                mav_options.append(20)
            if st.checkbox("Show 50-Day SMA", value=True, key=f"sma50_{selected_stock_for_deep_dive}"):
                chart_data['SMA50'] = chart_data['Close'].rolling(window=50).mean()
                mav_options.append(50)

            if not chart_data.empty:
                try:
                    fig, ax = mpf.plot(
                        chart_data,
                        type='candle',
                        style='yahoo',
                        title=f"\n{selected_stock_for_deep_dive} Price Action",
                        ylabel='Price (INR)',
                        volume=True,
                        ylabel_lower='Volume',
                        mav=tuple(m for m in mav_options if m in [20,50]), # Ensure only calculated MAs are passed
                        figratio=(12, 6),
                        returnfig=True
                    )
                    st.pyplot(fig)
                except Exception as e:
                    st.error(f"Could not generate candlestick chart for {selected_stock_for_deep_dive}: {e}")
                    st.line_chart(chart_data[['Close'] + [f'SMA{m}' for m in mav_options if f'SMA{m}' in chart_data.columns]])


            else:
                st.info(f"Not enough data to plot candlestick for {selected_stock_for_deep_dive}.")
else:
    st.info("Select stocks from the sidebar to see individual analysis options.")


# --- Performance Summary ---
st.markdown("---")
st.header("💹 Stock Performance Summary")
performance = []

# Use only master_symbols for performance calculation, not ^NSEI
for symbol in master_symbols:
    try:
        # Ensure we are accessing the correct MultiIndex level if it exists
        if isinstance(df_filtered.columns, pd.MultiIndex):
            if symbol not in df_filtered.columns.levels[0]:
                st.caption(f"Data for {symbol} not found in downloaded set for performance summary.")
                continue
            data_close = df_filtered[(symbol, 'Close')].dropna()
            data_volume = df_filtered[(symbol, 'Volume')].dropna()
        else: # Single stock was fetched initially
             if symbol == symbols_to_fetch[0]: # Check if current symbol is the one fetched
                data_close = df_filtered['Close'].dropna()
                data_volume = df_filtered['Volume'].dropna()
             else: # Should not happen if logic above is correct, but as a fallback
                st.caption(f"Data for {symbol} not available in the current structure for performance summary.")
                continue


        if len(data_close) < 2:
            st.caption(f"Not enough data points for {symbol} to calculate performance.")
            continue

        start_price = data_close.iloc[0]
        end_price = data_close.iloc[-1]
        change = ((end_price - start_price) / start_price) * 100

        avg_volume = data_volume.mean()

        # Enhanced Recommendation Logic
        rec = "Hold"
        if change <= -strong_buy_threshold:
            rec = "Strong Buy"
        elif change <= -buy_threshold:
            rec = "Buy"
        elif change >= strong_sell_threshold:
            rec = "Strong Sell"
        elif change >= sell_threshold:
            rec = "Sell"

        performance.append({
            "Symbol": symbol,
            "Start Price": round(start_price, 2),
            "End Price": round(end_price, 2),
            "Change (%)": round(change, 2),
            "Avg Volume": f"{avg_volume:,.0f}",
            "Recommendation": rec
        })
    except KeyError:
        st.caption(f"Data columns missing for {symbol}, skipping performance calculation.")
        continue
    except Exception as e:
        st.caption(f"Error calculating performance for {symbol}: {e}")
        continue


if performance:
    perf_df = pd.DataFrame(performance).sort_values(by="Change (%)", ascending=(compare_type == "Top Losers"))
    st.dataframe(perf_df, height=min(300, (len(perf_df) + 1) * 35))
    download_df_as_csv(perf_df, "stock_performance_summary.csv")

    # Side-by-side gainers & losers
    st.markdown("---")
    st.subheader("🏆 Top/Bottom 5 Performers")
    sorted_perf = perf_df.sort_values(by="Change (%)", ascending=False).reset_index(drop=True)
    top_gainers = sorted_perf.head(5)

    sorted_perf_losers = perf_df.sort_values(by="Change (%)", ascending=True).reset_index(drop=True)
    top_losers = sorted_perf_losers.head(5)

    # Remove duplicates if a stock appears in both (e.g., if less than 10 stocks selected)
    common_symbols_perf = set(top_gainers["Symbol"]).intersection(set(top_losers["Symbol"]))
    top_losers_display = top_losers[~top_losers["Symbol"].isin(common_symbols_perf)] if len(master_symbols) > 5 else top_losers


    col1_perf, col2_perf = st.columns(2)
    with col1_perf:
        st.markdown("#### 🔼 Top 5 Gainers")
        st.dataframe(top_gainers)
    with col2_perf:
        st.markdown("#### 🔽 Top 5 Losers")
        st.dataframe(top_losers_display)

    # Charting selected comparison type (Top N Gainers/Losers)
    st.markdown("---")
    st.subheader(f"📉 Price Trends for Top/Bottom {chart_n} Performers")
    
    if compare_type == "Top Gainers":
        chart_symbols = perf_df.sort_values(by="Change (%)", ascending=False).head(chart_n)['Symbol'].tolist()
    else: # Top Losers
        chart_symbols = perf_df.sort_values(by="Change (%)", ascending=True).head(chart_n)['Symbol'].tolist()

    chart_df_trends = pd.DataFrame()
    for symbol_trend in chart_symbols:
        try:
            if isinstance(df_filtered.columns, pd.MultiIndex):
                 series = df_filtered[(symbol_trend, "Close")].dropna()
            else: # Single stock data
                series = df_filtered["Close"].dropna() if symbol_trend == symbols_to_fetch[0] else pd.Series(dtype='float64')

            if not series.empty:
                chart_df_trends[symbol_trend] = series
        except Exception as e:
            st.caption(f"Could not prepare trend data for {symbol_trend}: {e}")
            continue
    
    if not chart_df_trends.empty:
        st.line_chart(chart_df_trends)
    else:
        st.info("No valid data available for the price trends chart based on current selection.")

    # Side-by-side Area and Bar Charts for the same top/bottom N
    st.markdown("---")
    st.subheader(f"📊 Visual Comparison: Price Trends vs. % Change (Top/Bottom {chart_n})")
    
    chart_area_df_comp = chart_df_trends.copy() # Use the same data as line chart
    chart_bar_df_comp = perf_df[perf_df['Symbol'].isin(chart_symbols)].set_index("Symbol")["Change (%)"]

    area_col_comp, bar_col_comp = st.columns(2)
    with area_col_comp:
        st.markdown("**📈 Area Chart - Price Trends**")
        if not chart_area_df_comp.empty:
            st.area_chart(chart_area_df_comp)
        else:
            st.info("No data for area chart.")
    with bar_col_comp:
        st.markdown("**📊 Bar Chart - % Change**")
        if not chart_bar_df_comp.empty:
            st.bar_chart(chart_bar_df_comp)
        else:
            st.info("No data for bar chart.")

else:
    st.info("No performance data to display. Check stock selections and date range.")


# --- NIFTY 50 Comparison ---
if show_nifty_comparison and "^NSEI" in df_filtered.columns.get_level_values(0):
    st.markdown("---")
    st.header("🆚 NIFTY 50 Performance Comparison")
    
    nifty_data = df_filtered[("^NSEI", "Close")].dropna()
    if not nifty_data.empty:
        # Normalize data to compare performance starting from 100
        normalized_df = pd.DataFrame()
        normalized_df["NIFTY 50"] = (nifty_data / nifty_data.iloc[0]) * 100
        
        for symbol in master_symbols: # Only compare against master symbols
            try:
                if isinstance(df_filtered.columns, pd.MultiIndex):
                    stock_close_data = df_filtered[(symbol, "Close")].dropna()
                else: # single stock
                    stock_close_data = df_filtered["Close"].dropna() if symbol == symbols_to_fetch[0] else pd.Series(dtype='float64')
                
                if not stock_close_data.empty:
                    normalized_df[symbol] = (stock_close_data / stock_close_data.iloc[0]) * 100
            except Exception: # Key error if symbol data is missing
                continue
        
        if len(normalized_df.columns) > 1: # More than just NIFTY 50
            st.line_chart(normalized_df)
            st.caption("Performance normalized to 100 at the start of the selected period.")
        else:
            st.info("Not enough stock data to compare with NIFTY 50, or only NIFTY 50 data is available.")
    else:
        st.warning("NIFTY 50 data could not be loaded or is empty for the selected period.")


# --- EDA and Recommendation Summary ---
st.markdown("---")
st.header("💡 Recommendation Insights")
if performance: # Check if perf_df was created
    rec_col1, rec_col2, rec_col3 = st.columns(3)
    
    strong_buy_rec_df = perf_df[perf_df["Recommendation"] == "Strong Buy"]
    if not strong_buy_rec_df.empty:
        with rec_col1.expander("💎 Strong Buy Candidates", expanded=True):
            st.dataframe(strong_buy_rec_df)
    else:
        rec_col1.info("No 'Strong Buy' signals based on current thresholds.")

    buy_rec_df = perf_df[perf_df["Recommendation"] == "Buy"]
    if not buy_rec_df.empty:
        with rec_col1.expander("🛒 Buy Candidates", expanded=True):
            st.dataframe(buy_rec_df)
    else:
        rec_col1.info("No 'Buy' signals based on current thresholds.")

    sell_rec_df = perf_df[perf_df["Recommendation"] == "Sell"]
    if not sell_rec_df.empty:
        with rec_col2.expander("💸 Sell Candidates", expanded=False):
            st.dataframe(sell_rec_df)
    else:
        rec_col2.info("No 'Sell' signals based on current thresholds.")

    strong_sell_rec_df = perf_df[perf_df["Recommendation"] == "Strong Sell"]
    if not strong_sell_rec_df.empty:
        with rec_col2.expander("🛑 Strong Sell Candidates", expanded=False):
            st.dataframe(strong_sell_rec_df)
    else:
        rec_col2.info("No 'Strong Sell' signals based on current thresholds.")

    hold_rec_df = perf_df[perf_df["Recommendation"] == "Hold"]
    if not hold_rec_df.empty:
        with rec_col3.expander("⚖️ Hold Candidates", expanded=True):
            st.dataframe(hold_rec_df)
    else:
        rec_col3.info("No 'Hold' signals based on current thresholds.")
else:
    st.info("Run analysis to see recommendation insights.")

st.markdown("---")
st.info("Disclaimer: This dashboard is for informational and educational purposes only. Not financial advice.")
