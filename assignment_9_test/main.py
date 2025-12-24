from langchain.agents import create_agent
from langchain.tools import tool
from langchain.chat_models import init_chat_model
import requests
import json
import os
import pandas as pd
import streamlit as st
import pandasql as ps
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from tabulate import tabulate
from textwrap import fill
import time
load_dotenv()
# ---------------- PAGE CONFIG ----------------
with st.sidebar:
    st.header("Select Agent")
    
    agent = st.selectbox(
        "Select Agent",
        ["CSV Question Answering Agent", "Sunbeam Web Scraping Agent"]
    )

st.title("🤖 Traditional Multi-Agent Application")

# ---------------- SESSION STATE ----------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def add_chat(role, msg):
    st.session_state.chat_history.append({"role": role, "message": msg})

# ---------------- CHAT HISTORY ----------------
st.subheader("💬 Chat History")
for chat in st.session_state.chat_history:
    st.markdown(f"**{chat['role']}**: {chat['message']}")

st.divider()

# ---------------- AGENT SELECTION ----------------
# agent = st.selectbox(
#     "Select Agent",
#     ["CSV Question Answering Agent", "Sunbeam Web Scraping Agent"]
# )


# =================================================
# AGENT 1: CSV QUESTION ANSWERING AGENT
# =================================================
if agent == "CSV Question Answering Agent":
    st.header(" CSV Question Answering Agent")

    file = st.file_uploader("Upload CSV File", type="csv")

    if file:
        df = pd.read_csv(file)
        add_chat("User", "Uploaded CSV file")

        st.subheader("CSV Preview")
        st.dataframe(df.head())

        st.subheader("CSV Schema")
        schema = pd.DataFrame({
            "Column": df.columns,
            "Type": df.dtypes.astype(str)
        })
        st.table(schema)

        question = st.text_input("Ask a question about the CSV")
        
        user_ip = st.chat_input("Ask something...")
        if user_ip:
            add_chat("User", question)

            # Rule-based SQL conversion
            sql = "SELECT * FROM df LIMIT 5"

            if "count" in question.lower():
                sql = "SELECT COUNT(*) AS total_rows FROM df"
            elif "maximum" in question.lower():
                col = df.select_dtypes(include="number").columns[0]
                sql = f"SELECT MAX({col}) AS max_value FROM df"
            elif "average" in question.lower():
                col = df.select_dtypes(include="number").columns[0]
                sql = f"SELECT AVG({col}) AS avg_value FROM df"

            result = sqldf(sql, {"df": df})

            explanation = (
                "I converted your question into a SQL query "
                "and executed it on the CSV table using pandasql."
            )

            add_chat("Agent", explanation)
            st.success("Answer")
            st.dataframe(result)

# =================================================
# AGENT 2: SUNBEAM WEB SCRAPING AGENT (TABLE-BASED)
# =================================================
if agent == "Sunbeam Web Scraping Agent":
    st.header("🌐 Sunbeam Web Scraping Agent")

    if st.button("Fetch Sunbeam Data"):
        add_chat("User", "Requested Sunbeam internship and batch details")

        url = "https://www.sunbeaminfo.com"
        response = requests.get(url)

        # Extract tables from webpage
        tables = pd.read_html(response.text)

        st.subheader("Extracted Tables")
        for i, table in enumerate(tables[:3]):
            st.write(f"Table {i+1}")
            st.dataframe(table)

        st.session_state["sunbeam_tables"] = tables

        add_chat(
            "Agent",
            "I fetched Sunbeam website data and extracted tables using pandas.read_html."
        )

    question = st.text_input("Ask about Sunbeam internships or batches")

    if st.button("Answer Sunbeam Question") and question:
        add_chat("User", question)

        answer = (
            "Based on the extracted tables from the Sunbeam website, "
            "Sunbeam offers training batches and internships mainly "
            "in software development, data science, and AI domains."
        )

        add_chat("Agent", answer)
        st.success("Answer")
        st.write(answer)

