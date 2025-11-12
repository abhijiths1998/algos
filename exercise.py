# app.py
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, date
import matplotlib.pyplot as plt

# ---------- DB helpers ----------
DB_PATH = "progress.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS workouts (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   entry_date TEXT,
                   workout_type TEXT,
                   exercise TEXT,
                   sets INTEGER,
                   reps INTEGER,
                   assistance_level TEXT,
                   dead_hang_seconds REAL,
                   negative_seconds REAL,
                   notes TEXT
                 )""")
    conn.commit()
    conn.close()

def insert_row(row):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""INSERT INTO workouts (entry_date, workout_type, exercise, sets, reps,
                 assistance_level, dead_hang_seconds, negative_seconds, notes)
                 VALUES (?,?,?,?,?,?,?,?,?)""",
              (row['entry_date'], row['workout_type'], row['exercise'], row['sets'],
               row['reps'], row['assistance_level'], row['dead_hang_seconds'],
               row['negative_seconds'], row['notes']))
    conn.commit()
    conn.close()

def read_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM workouts ORDER BY entry_date", conn, parse_dates=['entry_date'])
    conn.close()
    return df

# ---------- App ----------
st.set_page_config(page_title="Pull-up Progress Tracker", layout="wide")
st.title("🏋️ Pull-up Progress Tracker (Streamlit)")

init_db()

# Left: data entry
with st.sidebar:
    st.header("Log workout")
    entry_date = st.date_input("Date", value=date.today())
    workout_type = st.selectbox("Type", ["Pull", "Push", "Core", "Full Body", "Mobility", "Other"])
    exercise = st.selectbox("Exercise", ["Assisted Pull-up", "Dead Hang", "Negative", "Australian Row", "Chin Hold", "Pushups", "Other"])
    sets = st.number_input("Sets", min_value=0, max_value=20, value=3)
    reps = st.number_input("Reps (per set or total)", min_value=0, max_value=200, value=0)
    assistance_level = st.text_input("Assistance (e.g. foot-assist, band level, chair)", value="")
    dead_hang_seconds = st.number_input("Dead hang seconds (total)", min_value=0.0, value=0.0, step=0.5)
    negative_seconds = st.number_input("Negative descent seconds (avg)", min_value=0.0, value=0.0, step=0.5)
    notes = st.text_area("Notes", value="")
    if st.button("Save entry"):
        row = {
            "entry_date": entry_date.isoformat(),
            "workout_type": workout_type,
            "exercise": exercise,
            "sets": int(sets),
            "reps": int(reps),
            "assistance_level": assistance_level,
            "dead_hang_seconds": float(dead_hang_seconds),
            "negative_seconds": float(negative_seconds),
            "notes": notes
        }
        insert_row(row)
        st.success("Saved ✅")

# Main: data table + visualizations + personal metrics
st.subheader("Logged sessions")
df = read_data()
if df.empty:
    st.info("No data yet — log your first session in the sidebar.")
else:
    # show raw table
    st.dataframe(df[['entry_date','workout_type','exercise','sets','reps','assistance_level','dead_hang_seconds','negative_seconds','notes']])

    # quick aggregate metrics
    st.markdown("### Key metrics")
    latest = df.iloc[-1]
    col1, col2, col3 = st.columns(3)
    col1.metric("Latest dead hang (s)", f"{latest.dead_hang_seconds:.1f}")
    col2.metric("Latest negative (s)", f"{latest.negative_seconds:.1f}")
    col3.metric("Latest assisted reps", int(latest.reps))

    # progress charts: dead hang over time, negative seconds over time, assisted reps over time
    st.markdown("### Progress charts")
    # convert column types properly
    df['entry_date'] = pd.to_datetime(df['entry_date']).dt.date
    # dead hang plot
    if df['dead_hang_seconds'].sum() > 0:
        fig, ax = plt.subplots()
        hang = df.groupby('entry_date')['dead_hang_seconds'].max().reset_index()
        ax.plot(hang['entry_date'], hang['dead_hang_seconds'], marker='o')
        ax.set_title("Max dead hang (seconds) over time")
        ax.set_xlabel("Date")
        ax.set_ylabel("Seconds")
        ax.grid(True)
        st.pyplot(fig)
    else:
        st.write("No dead hang data yet.")

    # negative plot
    if df['negative_seconds'].sum() > 0:
        fig2, ax2 = plt.subplots()
        neg = df.groupby('entry_date')['negative_seconds'].max().reset_index()
        ax2.plot(neg['entry_date'], neg['negative_seconds'], marker='o')
        ax2.set_title("Max negative descent (seconds) over time")
        ax2.set_xlabel("Date")
        ax2.set_ylabel("Seconds")
        ax2.grid(True)
        st.pyplot(fig2)
    else:
        st.write("No negative data yet.")

    # assisted reps (filter exercise contains "Assisted" or "Pull")
    reps_df = df[df['exercise'].str.contains("Assisted|Pull|Chin", case=False, na=False)]
    if not reps_df.empty:
        fig3, ax3 = plt.subplots()
        reps = reps_df.groupby('entry_date')['reps'].max().reset_index()
        ax3.plot(reps['entry_date'], reps['reps'], marker='o')
        ax3.set_title("Max assisted reps over time")
        ax3.set_xlabel("Date")
        ax3.set_ylabel("Reps")
        ax3.grid(True)
        st.pyplot(fig3)

    # filter / export
    st.markdown("### Export & tools")
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", csv, "pullup_progress.csv", "text/csv")
    if st.button("Clear all data (danger)"):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM workouts")
        conn.commit()
        conn.close()
        st.experimental_rerun()
