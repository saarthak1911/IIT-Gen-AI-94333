import streamlit as st
import os
import shutil
from datetime import datetime

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# -------------------- CONFIG --------------------
RESUME_DIR = "resumes"
CHROMA_DIR = "chroma_db"

os.makedirs(RESUME_DIR, exist_ok=True)

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vectorstore = Chroma(
    persist_directory=CHROMA_DIR,
    embedding_function=embedding_model
)

# -------------------- UTILS --------------------
def load_and_split_pdf(pdf_path):
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )
    return splitter.split_documents(docs)

def add_resume(file_path, file_name):
    docs = load_and_split_pdf(file_path)
    for d in docs:
        d.metadata["file_name"] = file_name
    vectorstore.add_documents(docs)
    vectorstore.persist()

def delete_resume(file_name):
    vectorstore._collection.delete(
        where={"file_name": file_name}
    )
    vectorstore.persist()

def list_resumes():
    if not os.path.exists(RESUME_DIR):
        return []
    return os.listdir(RESUME_DIR)

# -------------------- STREAMLIT UI --------------------
st.set_page_config(page_title="AI Resume Shortlisting", layout="wide")
st.title("📄 AI Enabled Resume Shortlisting Application")

tabs = st.tabs([
    "📤 Upload / Update Resume",
    "📋 List Resumes",
    "🗑 Delete Resume",
    "🎯 Shortlist Resumes"
])

# -------------------- TAB 1: UPLOAD --------------------
with tabs[0]:
    st.header("Upload or Update Resume (PDF)")
    uploaded_file = st.file_uploader("Upload Resume", type=["pdf"])

    if uploaded_file:
        file_path = os.path.join(RESUME_DIR, uploaded_file.name)

        if os.path.exists(file_path):
            st.warning("Resume already exists. It will be updated.")
            delete_resume(uploaded_file.name)
            os.remove(file_path)

        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        add_resume(file_path, uploaded_file.name)
        st.success("Resume uploaded and indexed successfully!")

# -------------------- TAB 2: LIST --------------------
with tabs[1]:
    st.header("Available Resumes")
    resumes = list_resumes()

    if resumes:
        for r in resumes:
            st.write(f"📄 {r}")
    else:
        st.info("No resumes uploaded yet.")

# -------------------- TAB 3: DELETE --------------------
with tabs[2]:
    st.header("Delete Resume")
    resumes = list_resumes()

    selected = st.selectbox("Select Resume", resumes)
    if st.button("Delete"):
        delete_resume(selected)
        os.remove(os.path.join(RESUME_DIR, selected))
        st.success("Resume deleted successfully!")

# -------------------- TAB 4: SHORTLIST --------------------
with tabs[3]:
    st.header("Shortlist Resumes for Job Description")

    job_desc = st.text_area("Enter Job Description")
    top_k = st.number_input(
        "Number of Resumes to Shortlist",
        min_value=1,
        max_value=10,
        value=3
    )

    if st.button("Shortlist"):
        if not job_desc.strip():
            st.error("Please enter a job description.")
        else:
            results = vectorstore.similarity_search(
                job_desc,
                k=top_k
            )

            st.subheader("📌 Shortlisted Resumes")
            shown = set()

            for doc in results:
                fname = doc.metadata.get("file_name")
                if fname not in shown:
                    st.write(f"✅ {fname}")
                    shown.add(fname)