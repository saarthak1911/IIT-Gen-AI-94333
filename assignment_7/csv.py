from langchain.chat_models import init_chat_model
import os
import pandas as pd
import pandasql as ps
import streamlit as st

st.header("CSV SQL Query with LLM")

llm = init_chat_model(
    model = "llama-3.3-70b-versatile",
    model_provider = "openai",
    base_url = "https://api.groq.com/openai/v1",
    api_key = os.getenv("GROQ_API_KEY")
)
conversation = [
    {"role": "system", "content": "You are SQLite expert developer with 10 years of experience."}
]


csv_file = st.file_uploader("Upload a CSV file", type=["csv"])
# csv_file = input("Enter path of a CSV file: ")

if csv_file:

    df = pd.read_csv(csv_file)
    st.write("CSV schema: ")
    st.write(df.dtypes)


    user_input = st.chat_input("Ask anything about this CSV? ")

    if user_input:
        
        # create llm input for sql query generation

        llm_input = f"""
            Table Name: data
            Table Schema: {df.dtypes}
            Question: {user_input}
            Instruction:
                write the query based on table schema dont use any other table or assume.
                Write a SQL query for the above question. 
                
                Generate SQL query only in plain text format and nothing else.
                If you cannot generate the query, then output 'Error'.
                dont provide any explanation or additional text.
        """
        #print sql query on user input
        result = llm.invoke(llm_input)
        # st.write("Your Question:")
        # st.write(user_input)
        st.write("SQL Query:")
        st.success(result.content)
        query = result.content

        # user generated sql query for printing the table data
        result_table = ps.sqldf(query,{"data": df})
        st.write("\nQuery Result:")
        st.write(result_table)

        #crete new llm for explaination in simple english

        llm_input_2 = f"""
            Table Name: data  
            Table Schema: {df.dtypes}
            SQL Query: {result.content}
            Instruction:
                If SQL query is 'Error', then output 'You cannot generate the query'.
                explian the result of the SQL query on the above table in simple English.
                dont give Result Explanation or any additional text.
                just explain in simple English. in 2-4 sentences.
        """

        #print simlple explaination of the sql query result in english
        result_2 = llm.invoke(llm_input_2)
        st.write("Explaination of the Result:")
        st.success(result_2.content)