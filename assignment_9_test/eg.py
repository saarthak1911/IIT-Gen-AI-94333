import streamlit as st
from langchain.agents import create_agent
from langchain.tools import tool
from langchain.chat_models import init_chat_model
from langchain.agents.middleware import wrap_model_call

import pandas as pd
from pandasql import ps
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Multi-Agent AI App", layout="wide")
st.title("Streamlit Agent")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "df" not in st.session_state:
    st.session_state.df = None

@wrap_model_call
def model_logging(request, handler):
    print("\nBefore model call", "-" * 20)
    response = handler(request)
    print("After model call", "-" * 20)
    return response

@wrap_model_call
def limit_model_context(request, handler):
    request.messages = request.messages[-5:]
    return handler(request)

@tool
def csv_qa(uploaded_file):
    """
    Converts user question into SQL, executes it on CSV
    Answer questions from uploaded CSV using SQL.
    """
    try:
        df = st.session_state.df
        if df is None:
            return "Please upload a CSV file first."

        q = question.lower()

        # ✅ NEW: column-specific handling
        if "product name" in q or "product_name" in q:
            sql = "SELECT product_name FROM df"

        elif "count" in q:
            sql = "SELECT COUNT(*) AS total_rows FROM df"

        elif "average" in q:
            col = df.select_dtypes(include="number").columns[0]
            sql = f"SELECT AVG({col}) AS average_value FROM df"

        elif "max" in q:
            col = df.select_dtypes(include="number").columns[0]
            sql = f"SELECT MAX({col}) AS max_value FROM df"

        else:
            sql = "SELECT * FROM df LIMIT 5"

        result = sqldf(sql, {"df": df})

        st.table(result)
        return "The table above shows the result in a proper tabular format."

    except Exception as e:
      return f"CSV Error: {e}"


@tool
def scrape_sunbeam(question: str):
    """
    USE THIS TOOL ONLY IF the user asks about Sunbeam internships or courses.
    """
    try:
        url = "https://www.sunbeaminfo.com/"
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(separator=" ")

        return f"""
Information fetched directly from Sunbeam website:

{text[:1200]}

Explanation:
I visited the Sunbeam website and extracted internship and training related data.
"""

    except Exception as e:
        return f"Scraping Error: {e}"

llm = init_chat_model(
    model="google/gemma-3-4b",
    model_provider="openai",
    base_url="http://127.0.0.1:1234/v1",
    api_key="not-needed"
)

agent = create_agent(
    model=llm,
    tools=[csv_qa, scrape_sunbeam],
    middleware=[model_logging, limit_model_context],
    system_prompt="""
You are a strict tool-based assistant.

Rules:
- if user asks about table please refer uploaded_file
- CSV questions → csv_qa tool
- if user ask about general knowledge, answer directly
- if you think user is asking about any type of question related to table or csv data, use csv_qa tool
- Sunbeam questions → scrape_sunbeam tool
- Never hallucinate
- Explain in simple English
- Give answer in the proper english format
"""
)

with st.sidebar:
    st.header("Upload CSV")
    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
    if uploaded_file:
        st.session_state.df = pd.read_csv(uploaded_file)
        st.success("CSV uploaded successfully")
        st.dataframe(st.session_state.df.head())

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask something...")

if user_input:
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    if any(word in user_input.lower() for word in ["csv", "count", "average", "max", "file"]):
        ai_msg = csv_qa.run(user_input)

    elif any(word in user_input.lower() for word in ["sunbeam", "intern", "internship", "batch", "course"]):
        ai_msg = scrape_sunbeam.run(user_input)

    else:
        result = agent.invoke({
            "messages": [
                {"role": "user", "content": user_input}
            ]
        })
        ai_msg = result["messages"][-1].content

    st.session_state.messages.append(
        {"role": "assistant", "content": ai_msg}
    )

    with st.chat_message("assistant"):
        st.markdown(ai_msg)