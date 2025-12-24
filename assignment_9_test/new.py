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

load_dotenv()

# ---------------- STREAMLIT UI ----------------
st.title("Explorer : CSV Agent")

with st.sidebar:
    st.header("Select Agent")
    mode = st.selectbox("Select One", ["CSV Agent", "Web Scraper"])

# ---------------- INIT LLM ----------------
llm = init_chat_model(
    model="llama-3.3-70b-versatile",
    model_provider="openai",
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)


if mode == "CSV Agent":
    # ---------------- UPLOAD CSV ----------------
    csv_file = st.file_uploader("Upload a CSV file: ", type=["csv"])

    if csv_file:
        df = pd.read_csv(csv_file)

        st.subheader("CSV Schema")
        st.write(df.dtypes)
    else:

       