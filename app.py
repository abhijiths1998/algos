import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import time
import numpy as np

# Streamlit config
st.set_page_config(page_title="NSE Mini Signal App", layout="wide")
st.title("📈 NSE Stock Signal Dashboard")
st.markdown("""
This dashboard gives you:
- ✅ Real **Buy/Sell signals** based on 7-day price difference
- ✅ Choose how many stocks to scan (top N)
- ✅ Search for specific stock symbol and get weekly price change & company financials
""")

# Today's date (adjust if weekend)
today = datetime.date.today()
if today.weekday() >= 5:  # If it's weekend (5=Saturday, 6=Sunday)
    today -= datetime.timedelta(days=today.weekday() - 4)  # Adjust to Friday
start_week = today - datetime.timedelta(days=7)

st.markdown(f"📅 Date range: **{start_week}** to **{today}**")

# Allow user to select how many stocks to scan
# Add this missing feature mentioned in the description
num_stocks = st.slider("Number of stocks to scan", min_value=5, max_value=50, value=10, step=5)

# Input symbol for search
search_symbol = st.text_input("🔍 Enter NSE symbol to get detailed info (e.g. RELIANCE.NS)")

# Extended stock list - add more popular NSE stocks
symbols_all = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "ICICIBANK.NS", "HDFCBANK.NS",
    "ITC.NS", "SBIN.NS", "LT.NS", "AXISBANK.NS", "BAJFINANCE.NS",
    "HINDUNILVR.NS", "BHARTIARTL.NS", "KOTAKBANK.NS", "HDFC.NS", "ASIANPAINT.NS",
    "MARUTI.NS", "HCLTECH.NS", "TATAMOTORS.NS", "SUNPHARMA.NS", "NTPC.NS",
    "TITAN.NS", "ONGC.NS", "NESTLEIND.NS", "TATASTEEL.NS", "ULTRACEMCO.NS",
    "BAJAJFINSV.NS", "JSWSTEEL.NS", "ADANIENT.NS", "POWERGRID.NS", "M&M.NS",
    "HINDALCO.NS", "CIPLA.NS", "DRREDDY.NS", "WIPRO.NS", "COALINDIA.NS",
    "INDUSINDBK.NS", "GRASIM.NS", "HDFCLIFE.NS", "TECHM.NS", "BPCL.NS",
    "BAJAJ-AUTO.NS", "DIVISLAB.NS", "EICHERMOT.NS", "APOLLOHOSP.NS", "SBILIFE.NS",
    "UPL.NS", "HEROMOTOCO.NS", "BRITANNIA.NS", "ADANIPORTS.NS", "TATACONSUM.NS"
]

# Use only the selected number of stocks
symbols_to_scan = symbols_all[:num_stocks]

# Paginate through selected symbols and collect their info
buy_list = []
sell_list = []
neutral_list = []
skipped = []
all_rows = []

progress_bar = st.progress(0)

with st.spinner("🔄 Fetching and collating stock info..."):
    for i, symbol in enumerate(symbols_to_scan):
        try:
            # Update progress bar
            progress_bar.progress((i + 1) / len(symbols_to_scan))
            
            # Download data with error handling
            df = yf.download(symbol, start=start_week, end=today + datetime.timedelta(days=1), progress=False)
            
            if not isinstance(df, pd.DataFrame) or df.empty or df['Close'].isna().all():
                skipped.append(f"{symbol} - no valid close price")
                continue

            close_prices = df['Close'].dropna()
            if len(close_prices) < 2:
                skipped.append(f"{symbol} - not enough data")
                continue

            # Get company name for better display
            try:
                ticker_info = yf.Ticker(symbol).info
                company_name = ticker_info.get('shortName', symbol)
            except:
                company_name = symbol
            
            # Calculate price change
            start_price = round(close_prices.iloc[0], 2)
            current_price = round(close_prices.iloc[-1], 2)
            change = round(((current_price - start_price) / start_price) * 100, 2)
            
            # Determine signal and emoji
            if change <= -5:
                signal = "BUY"
                emoji = "📉"
            elif change >= 5:
                signal = "SELL"
                emoji = "📈"
            else:
                signal = "HOLD"
                emoji = "↔️"
                
            # Format prices with currency symbol
            formatted_start = f"₹{start_price:.2f}"
            formatted_current = f"₹{current_price:.2f}"
            
            row = (symbol, company_name, formatted_start, formatted_current, change, emoji, signal)
            all_rows.append(row)

            # Categorize based on signal
            if signal == "BUY":
                buy_list.append(row)
            elif signal == "SELL":
                sell_list.append(row)
            else:
                neutral_list.append(row)

            # Avoid hitting rate limits
            time.sleep(0.2)
        except Exception as e:
            skipped.append(f"{symbol} - error: {str(e)}")

# Clear progress bar when done
progress_bar.empty()

# Create final DataFrame from all collected stock info
df_all = pd.DataFrame(all_rows, columns=["Symbol", "Company", "Start Price", "Current Price", "% Change", "Trend", "Signal"])

# Weekly Buy/Sell Output
col1, col2 = st.columns(2)

with col1:
    st.subheader("🟢 BUY Recommendations")
    df_buy = pd.DataFrame(buy_list, columns=["Symbol", "Company", "Start Price", "Current Price", "% Change", "Trend", "Signal"])
    if not df_buy.empty:
        st.dataframe(df_buy.sort_values(by="% Change"), use_container_width=True)
    else:
        st.info("No BUY recommendations for the selected period.")

with col2:
    st.subheader("🔴 SELL Recommendations")
    df_sell = pd.DataFrame(sell_list, columns=["Symbol", "Company", "Start Price", "Current Price", "% Change", "Trend", "Signal"])
    if not df_sell.empty:
        st.dataframe(df_sell.sort_values(by="% Change", ascending=False), use_container_width=True)
    else:
        st.info("No SELL recommendations for the selected period.")

# Show neutral recommendations in expandable section
with st.expander("HOLD Recommendations"):
    df_neutral = pd.DataFrame(neutral_list, columns=["Symbol", "Company", "Start Price", "Current Price", "% Change", "Trend", "Signal"])
    if not df_neutral.empty:
        st.dataframe(df_neutral.sort_values(by="% Change", ascending=False), use_container_width=True)
    else:
        st.info("No HOLD recommendations for the selected period.")

# Show full dataframe if user wants to see all scanned data
with st.expander("📋 All Scanned Stock Data"):
    st.dataframe(df_all.sort_values(by="% Change", ascending=False), use_container_width=True)

# Specific symbol detail view
if search_symbol:
    st.subheader(f"🔍 Detailed Info for {search_symbol.upper()}")
    try:
        data = yf.download(search_symbol, start=start_week - datetime.timedelta(days=30), end=today + datetime.timedelta(days=1), progress=False)
        
        if isinstance(data, pd.DataFrame) and not data.empty and len(data['Close'].dropna()) >= 2:
            # Get more historical data for better context
            weekly_last = round(data['Close'].dropna().iloc[-8] if len(data) > 7 else data['Close'].dropna().iloc[0], 2)
            current = round(data['Close'].dropna().iloc[-1], 2)
            weekly_change = round(((current - weekly_last) / weekly_last) * 100, 2)
            
            # Also calculate monthly change if possible
            monthly_last = round(data['Close'].dropna().iloc[0] if len(data) > 20 else weekly_last, 2)
            monthly_change = round(((current - monthly_last) / monthly_last) * 100, 2)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Current Price", f"₹{current:.2f}")
            with col2:
                st.metric("Weekly Change", f"{weekly_change}%", delta=f"{weekly_change}%")
            with col3:
                st.metric("Monthly Change", f"{monthly_change}%", delta=f"{monthly_change}%")
            
            # Plot stock price chart
            st.subheader("Price Chart")
            st.line_chart(data['Close'].dropna())

            try:
                ticker = yf.Ticker(search_symbol)
                info = ticker.info if ticker and hasattr(ticker, 'info') and isinstance(ticker.info, dict) else {}
                
                if info:
                    col1, col2 = st.columns([2,1])
                    
                    with col1:
                        st.subheader("Company Overview")
                        st.write(info.get("longBusinessSummary", "No summary available."))
                    
                    with col2:
                        # Display company logo if available
                        if "logo_url" in info and info["logo_url"]:
                            st.image(info["logo_url"], width=100)
                        
                        st.subheader("Quick Facts")
                        st.markdown(f"**Sector:** {info.get('sector', 'N/A')}")
                        st.markdown(f"**Industry:** {info.get('industry', 'N/A')}")
                        st.markdown(f"**Exchange:** {info.get('exchange', 'N/A')}")

                    st.subheader("Key Metrics")
                    metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
                    
                    with metrics_col1:
                        st.metric("Market Cap", f"₹{info.get('marketCap', 'N/A'):,}" if isinstance(info.get('marketCap'), (int, float)) else "N/A")
                        st.metric("P/E Ratio (TTM)", f"{info.get('trailingPE', 'N/A'):.2f}" if isinstance(info.get('trailingPE'), (int, float)) else "N/A")
                        st.metric("EPS (TTM)", f"₹{info.get('trailingEps', 'N/A'):.2f}" if isinstance(info.get('trailingEps'), (int, float)) else "N/A")
                    
                    with metrics_col2:
                        st.metric("52-Week High", f"₹{info.get('fiftyTwoWeekHigh', 'N/A'):.2f}" if isinstance(info.get('fiftyTwoWeekHigh'), (int, float)) else "N/A")
                        st.metric("52-Week Low", f"₹{info.get('fiftyTwoWeekLow', 'N/A'):.2f}" if isinstance(info.get('fiftyTwoWeekLow'), (int, float)) else "N/A")
                        st.metric("Volume", f"{info.get('volume', 'N/A'):,}" if isinstance(info.get('volume'), (int, float)) else "N/A")
                    
                    with metrics_col3:
                        st.metric("Dividend Yield", f"{info.get('dividendYield', 'N/A') * 100:.2f}%" if isinstance(info.get('dividendYield'), (int, float)) else "N/A")
                        st.metric("Beta", f"{info.get('beta', 'N/A'):.2f}" if isinstance(info.get('beta'), (int, float)) else "N/A")
                        st.metric("Avg Daily Volume", f"{info.get('averageVolume', 'N/A'):,}" if isinstance(info.get('averageVolume'), (int, float)) else "N/A")
                    
                    # Display financial data if available
                    if hasattr(ticker, 'financials') and not ticker.financials.empty:
                        st.subheader("Financial Summary")
                        st.dataframe(ticker.financials.head())
                else:
                    st.warning("No detailed company metrics available.")
            except Exception as info_err:
                st.warning(f"Unable to fetch detailed info: {info_err}")
        else:
            st.warning(f"Not enough data found for {search_symbol}. Make sure you've entered a valid NSE symbol (with .NS suffix).")
    except Exception as e:
        st.error(f"Error fetching data: {e}")

# Error handling for skipped stocks
if skipped:
    with st.expander("⚠️ Skipped Stocks / Errors"):
        for s in skipped:
            st.text(s)

# Add caching information and refresh button
st.sidebar.title("Dashboard Controls")
if st.sidebar.button("🔄 Refresh Data"):
    st.experimental_rerun()

st.sidebar.info("""
**About this dashboard**
- Data is sourced from Yahoo Finance
- Buy signals: Stocks that fell ≥ 5% in 7 days
- Sell signals: Stocks that rose ≥ 5% in 7 days
- Hold: Stocks with less than 5% change
""")

# Add timestamp to show when data was last updated
st.sidebar.markdown(f"**Last updated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
