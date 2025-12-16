import streamlit as st
import pandasql as ps
import pandas as pd

st.header("File sort using SQl")

file = st.file_uploader("Upload a CSV file:", type = ["csv"])
df = []
if file:
    df = pd.read_csv(file)
    st.dataframe(df)

    query = st.text_input("Enter SQl query:")

    if query:
        result = ps.sqldf(query,{"data" : df})
        st.dataframe(result)

