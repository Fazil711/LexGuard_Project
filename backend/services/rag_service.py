import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

CHROMA_DB_DIR = "./chroma_db"

print("Loading Embedding Model...")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def get_vector_db():
    """Returns the existing Vector DB instance"""
    return Chroma(
        persist_directory=CHROMA_DB_DIR,
        embedding_function=embeddings
    )

def add_documents_to_db(splits):
    """Adds split documents to the Vector DB"""
    if not splits:
        return
    
    db = get_vector_db()
    db.add_documents(splits)
    print(f"Added {len(splits)} chunks to Vector DB.")

def get_retriever():
    """Returns a retriever for the RAG chain"""
    db = get_vector_db()
    return db.as_retriever(search_kwargs={"k": 3})