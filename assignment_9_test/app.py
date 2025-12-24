from langchain.agents import create_agent
from langchain.tools import tool
from langchain.chat_models import init_chat_model
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

# ---------------- UPLOAD CSV ----------------
csv_file = st.file_uploader("Upload a CSV file: ", type=["csv"])

if csv_file:
    df = pd.read_csv(csv_file)

    st.subheader("CSV Schema")
    st.write(df.dtypes)

    # ---------------- TOOL ----------------
    @tool
    def csv_analyser(question: str) -> dict:
        """
        Converts user question into SQL, executes it on CSV,
        and returns result with explanation.
        """
        try:
            # Prompt to generate SQL
            sql_prompt = f"""
            Table Name: data
            Table Schema: {df.dtypes}
            Question: {question}

            Rules:
            - Generate ONLY a valid SQL query
            - Use table 'data' only
            - No explanation
            - If not possible, return Error
            """

            sql_query = llm.invoke(sql_prompt).content.strip()

            if sql_query.lower() == "error":
                return {"output": "❌ Unable to generate SQL query."}

            # Execute SQL
            result_df = ps.sqldf(sql_query, {"data": df})

            # Explanation
            explain_prompt = f"""
            Explain the result of this SQL query in simple English
            in 4–5 lines.

            SQL Query:
            {sql_query}
            """

            explanation = llm.invoke(explain_prompt).content.strip()

            return {
                "output": f"""
🧾 SQL Query:
{sql_query}

📊 Query Result:
{result_df}

🧠 Explanation:
{explanation}
"""
            }

        except Exception as e:
            return {"output": f"❌ Error: {e}"}

    # ---------------- CREATE AGENT ----------------
    agent = create_agent(
        model=llm,
        tools=[csv_analyser],
        system_prompt=(
            "You are a CSV data analysis expert. "
            "Always use the csv_analyser tool to answer user questions."
        )
    )

    # ---------------- USER INPUT ----------------
    user_input = st.chat_input("Ask anything about this CSV") or st.file_uploader("Or upload another CSV file: ", type=["csv"])

    if user_input:
        with st.spinner("Agent is thinking..."):
            response = agent.invoke({"input": user_input})

        st.subheader("🤖 Agent Answer")
        st.write(response["output"])
