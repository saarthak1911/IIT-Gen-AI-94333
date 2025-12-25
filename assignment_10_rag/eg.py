import streamlit as st
import os

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# -------------------- FOLDERS --------------------
RESUME_FOLDER = "resumes"
DB_FOLDER = "chroma_db"

os.makedirs(RESUME_FOLDER, exist_ok=True)

# -------------------- EMBEDDINGS --------------------
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# -------------------- VECTOR STORE --------------------
db = Chroma(
    persist_directory=DB_FOLDER,
    embedding_function=embeddings
)

# -------------------- STREAMLIT UI --------------------
st.title("AI Resume Shortlisting App (Beginner)")

menu = st.sidebar.selectbox(
    "Select Option",
    ["Upload Resume", "List Resumes", "Delete Resume", "Shortlist Resumes"]
)

# -------------------- UPLOAD RESUME --------------------
if menu == "Upload Resume":
    st.header("Upload Resumes (Multiple PDFs Allowed)")
    
    files = st.file_uploader(
        "Upload Resume PDFs",
        type="pdf",
        accept_multiple_files=True
    )

    if files:
        for file in files:
            path = os.path.join(RESUME_FOLDER, file.name)

            with open(path, "wb") as f:
                f.write(file.getbuffer())

            loader = PyPDFLoader(path)
            documents = loader.load()

            splitter = RecursiveCharacterTextSplitter(
                chunk_size=800,
                chunk_overlap=100
            )
            chunks = splitter.split_documents(documents)

            for c in chunks:
                c.metadata["file_name"] = file.name

            db.add_documents(chunks)

        db.persist()
        st.success("All resumes uploaded successfully!")


# -------------------- LIST RESUMES --------------------
elif menu == "List Resumes":
    st.header("Uploaded Resumes")

    files = os.listdir(RESUME_FOLDER)
    if files:
        for f in files:
            st.write("📄", f)
    else:
        st.info("No resumes uploaded.")

# -------------------- DELETE RESUME --------------------
elif menu == "Delete Resume":
    st.header("Delete Resume")

    files = os.listdir(RESUME_FOLDER)
    selected = st.selectbox("Select Resume", files)

    if st.button("Delete"):
        db._collection.delete(where={"file_name": selected})
        db.persist()

        os.remove(os.path.join(RESUME_FOLDER, selected))
        st.success("Resume deleted successfully!")

# -------------------- SHORTLIST RESUMES --------------------
elif menu == "Shortlist Resumes":
    st.header("Shortlist Resumes")

    job_desc = st.text_area("Enter Job Description")
    top_k = st.number_input("Number of resumes", 1, 5, 3)

    if st.button("Search"):
        results = db.similarity_search(job_desc, k=top_k)

        st.subheader("Shortlisted Resumes")
        shown = []

        for doc in results:
            name = doc.metadata["file_name"]
            if name not in shown:
                st.write("✅", name)
                shown.append(name)