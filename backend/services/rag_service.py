import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

CHROMA_DB_DIR = "./chroma_db"

print("Loading Embedding Model...")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def get_vector_db():
    return Chroma(
        persist_directory=CHROMA_DB_DIR,
        embedding_function=embeddings
    )

def add_documents_to_db(splits):
    if not splits:
        return
    db = get_vector_db()
    db.add_documents(splits)
    print(f"✅ Added {len(splits)} chunks to Vector DB.")

def get_retriever(case_id: str = None):
    """
    Returns a retriever that filters by case_id to ensure we only 
    read relevant documents.
    """
    db = get_vector_db()
    
    search_kwargs = {"k": 4} 
    
    if case_id:
        search_kwargs["filter"] = {"case_id": case_id}
        
    return db.as_retriever(search_kwargs=search_kwargs)

def delete_case_vectors(case_id: str):
    """
    Deletes all vector embeddings associated with a specific case_id.
    """
    db = get_vector_db()
    try:
        db.delete(where={"case_id": case_id})
        print(f"✅ Deleted vectors for case: {case_id}")
        return True
    except Exception as e:
        print(f"⚠️ Error deleting vectors for case {case_id}: {e}")
        return False