import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import io
import smtplib
from email.message import EmailMessage
import matplotlib.pyplot as plt

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

st.header("📈 Explore Stock Trends by Period")

selected_symbols = st.multiselect("🔍 Select one or more stocks", options=symbols, default=["RELIANCE.NS", "TCS.NS"], key="stock_period")
selected_range = st.selectbox("📆 Select time range", options=["1mo", "6mo", "1y", "5y", "ytd"])

if selected_symbols and selected_range:
    with st.spinner("📊 Fetching data..."):
        df = yf.download(selected_symbols, period=selected_range, group_by="ticker", progress=False)

    if df.empty:
        st.error("❌ No data returned for selected stocks.")
    else:
        # --- Charts ---
        st.subheader("📉 Closing Price Trend")
        close_df = pd.DataFrame()
        for symbol in selected_symbols:
            if symbol in df.columns.get_level_values(0):
                close_series = df[symbol]["Close"].dropna()
                close_series.name = symbol
                close_df = pd.concat([close_df, close_series], axis=1)
        if not close_df.empty:
            st.line_chart(close_df)

        st.subheader("🔊 Volume Trend")
        volume_df = pd.DataFrame()
        for symbol in selected_symbols:
            if symbol in df.columns.get_level_values(0):
                volume_series = df[symbol]["Volume"].dropna()
                volume_series.name = symbol
                volume_df = pd.concat([volume_df, volume_series], axis=1)
        if not volume_df.empty:
            st.area_chart(volume_df)

        # --- Recommendations ---
        st.subheader("💡 Weekly Buy/Sell Recommendations")

        recommendations = []

        for symbol in selected_symbols:
            try:
                symbol_df = df[symbol]
                close_series = symbol_df["Close"].dropna()
                if len(close_series) < 6:
                    continue

                current = close_series.iloc[-1]
                prev_week = close_series.iloc[-6]

                change = ((current - prev_week) / prev_week) * 100
                rec = "BUY" if change <= -5 else "SELL"

                recommendations.append({
                    "Symbol": symbol,
                    "Previous Week Close": round(prev_week, 2),
                    "Current Close": round(current, 2),
                    "% Change": round(change, 2),
                    "Recommendation": rec
                })
            except Exception as e:
                st.warning(f"Could not process {symbol}: {e}")

        if recommendations:
            rec_df = pd.DataFrame(recommendations)
            st.dataframe(rec_df, use_container_width=True)

            st.download_button("⬇️ Download as CSV", rec_df.to_csv(index=False), "recommendations.csv", "text/csv")
            st.download_button("⬇️ Download as JSON", rec_df.to_json(orient="records", indent=2), "recommendations.json", "application/json")
        else:
            st.info("No recommendations available yet.")
            
st.header(body="📈 Stock Trend Visualizer", divider="grey")
st.title("📈 Explore Stock Trends by Period")

# Multi-select dropdown for stocks
selected_symbols = st.multiselect("🔍 Select one or more stocks", options=symbols, default=["RELIANCE.NS", "TCS.NS"])
selected_range = st.selectbox("📆 Select time range", options=["1mo", "6mo", "1y", "5y", "ytd"])

if selected_symbols and selected_range:
    with st.spinner("📊 Fetching data..."):
        df = yf.download(selected_symbols, period=selected_range, group_by="ticker", progress=False)

    # --- Closing Prices ---
    st.subheader("📉 Closing Price Trend")
    close_df = pd.DataFrame()

    for symbol in selected_symbols:
        if symbol in df.columns.get_level_values(0):
            close_series = df[symbol]["Close"].dropna()
            close_series.name = symbol
            close_df = pd.concat([close_df, close_series], axis=1)

    if not close_df.empty:
        st.line_chart(close_df)
    else:
        st.warning("No valid close price data available.")

    # --- Volume Trends ---
    st.subheader("🔊 Trading Volume Trend")
    volume_df = pd.DataFrame()

    for symbol in selected_symbols:
        if symbol in df.columns.get_level_values(0):
            volume_series = df[symbol]["Volume"].dropna()
            volume_series.name = symbol
            volume_df = pd.concat([volume_df, volume_series], axis=1)

    if not volume_df.empty:
        st.area_chart(volume_df)
    else:
        st.warning("No volume data available.")


# -------------------------------------
# 🧠 Enhanced Actionable Insights (EDA)
# -------------------------------------
st.markdown("---")
st.header("🧠 Actionable Insights & Visual Recommendations")

# 1️⃣ BUY Recommendations: dropped more than 5%
st.subheader("🟢 BUY Suggestions: Stocks Dropped > 5%")
buy_df = df_perf[df_perf["Change (%)"] <= -5].sort_values(by="Change (%)")
if not buy_df.empty:
    st.dataframe(buy_df)
else:
    st.info("No stocks dropped more than 5% this week.")

# 2️⃣ Uptrend Stocks in Last 5 Days
st.subheader("📈 Consistent Uptrend (Last 5 Trading Days)")

uptrend_stocks = []
chart_data = pd.DataFrame()

for symbol in symbols:
    try:
        prices = df_filtered[symbol]['Close'].dropna()
        if len(prices) >= 5 and all(prices[-5 + i] < prices[-4 + i] for i in range(4)):
            uptrend_stocks.append(symbol)
            chart_data[symbol] = prices
    except:
        continue

if uptrend_stocks:
    st.success(f"Detected consistent upward trend in: {', '.join(uptrend_stocks)}")
    st.line_chart(chart_data[uptrend_stocks])
else:
    st.info("No consistent uptrend stocks in the last 5 days.")

# 3️⃣ Volatility Check
st.subheader("⚠️ Volatile Stocks (Standard Deviation > ₹50)")

vol_data = []
for symbol in symbols:
    try:
        series = df_filtered[symbol]['Close'].dropna()
        std_dev = series.std()
        if std_dev > 50:
            vol_data.append((symbol, round(std_dev, 2)))
    except:
        continue

df_vol = pd.DataFrame(vol_data, columns=["Symbol", "Std Dev"]).sort_values(by="Std Dev", ascending=False)
if not df_vol.empty:
    st.bar_chart(df_vol.set_index("Symbol"))
else:
    st.info("No stocks detected with high volatility.")

# 4️⃣ Inactive Stocks: No Price Change
st.subheader("⛔ Inactive / Suspended Stocks")
inactive_df = df_perf[df_perf["Start Price"] == df_perf["End Price"]]
if not inactive_df.empty:
    st.dataframe(inactive_df)
else:
    st.success("All stocks showed some price movement in the last 7 weeks.")

# -------------------------------------
# ✉️ Send Insights via Email
# -------------------------------------
st.subheader("📧 Email Insights")

email = st.text_input("Enter your email address:")
send_email = st.button("📤 Send Insights")

if send_email and email:
    try:
        # Compose message
        msg = EmailMessage()
        msg["Subject"] = "📊 Your NSE Weekly Insights"
        msg["From"] = "your_email@gmail.com"
        msg["To"] = email

        html_body = "<h2>NSE Weekly Insights</h2>"

        if not buy_df.empty:
            html_body += "<h3>🟢 BUY Recommendations</h3>" + buy_df.to_html(index=False)

        if not inactive_df.empty:
            html_body += "<h3>⛔ Inactive Stocks</h3>" + inactive_df.to_html(index=False)

        if not df_vol.empty:
            html_body += "<h3>⚠️ High Volatility Stocks</h3>" + df_vol.to_html(index=False)

        msg.set_content("Please find your stock insights attached.")
        msg.add_alternative(html_body, subtype="html")

        # SMTP Send (using Gmail example)
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login("your_email@gmail.com", "your_app_password")  # 🔐 Use app password
            smtp.send_message(msg)

        st.success(f"✅ Insights sent to {email}")
    except Exception as e:
        st.error(f"❌ Failed to send email: {e}")
elif send_email:
    st.warning("Please enter a valid email.")

