import sqlite3
from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Influencer Outreach", layout="wide")
st.title("EDXSO AI Micro-Influencer Outreach")
p = Path("data/influencers.csv")
if not p.exists():
    st.info("Run main.py first to generate data/influencers.csv")
    st.stop()
df = pd.read_csv(p)
a,b,c = st.columns(3)
a.metric("Discovered", len(df)); b.metric("Qualified", int((df.status == "Qualified").sum())); c.metric("Emails Found", int((df.contact_email != "Not Found").sum()))
st.dataframe(df, use_container_width=True)
st.subheader("Qualified creators")
st.dataframe(df[df.status == "Qualified"], use_container_width=True)
if Path("data/outreach.db").exists():
    with sqlite3.connect("data/outreach.db") as conn:
        log = pd.read_sql_query("SELECT * FROM outreach_log ORDER BY id DESC", conn)
    st.subheader("Outreach tracker")
    st.dataframe(log, use_container_width=True)
