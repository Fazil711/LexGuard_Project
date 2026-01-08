import os
import shutil
from fastapi import UploadFile
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_classic.text_splitter import RecursiveCharacterTextSplitter
from services.rag_service import add_documents_to_db
from core.database import SessionLocal
from models.models import Document
from services.llm_service import analyze_document_text

UPLOAD_DIR = "./uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def save_upload_file(upload_file: UploadFile) -> str:
    """Saves the uploaded file to disk and returns the path"""
    file_path = os.path.join(UPLOAD_DIR, upload_file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
        
    return file_path

def process_document(file_path: str):
    """
    Loads the file, splits it, and adds it to the Vector DB.
    Run this in a background task.
    """
    print(f"Processing file: {file_path}")
    docs = []
    
    try:
        if file_path.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
            docs.extend(loader.load())
        elif file_path.endswith(".txt"):
            loader = TextLoader(file_path, encoding='utf-8')
            docs.extend(loader.load())
            
        # Split documents
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        splits = text_splitter.split_documents(docs)
        
        # Add to Vector DB
        add_documents_to_db(splits)
        
        return True
    except Exception as e:
        print(f"Error processing document: {e}")
        return False
    
def process_document(file_path: str, doc_id: str):
    """
    1. Extract Text
    2. Add to Vector DB (RAG)
    3. Analyze with LLM (Intelligence)
    4. Update DB Record
    """
    print(f"Processing file: {file_path}")
    docs = []
    
    # 1. Load File
    try:
        if file_path.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
            docs.extend(loader.load())
        elif file_path.endswith(".txt"):
            loader = TextLoader(file_path, encoding='utf-8')
            docs.extend(loader.load())
            
        full_text = "\n".join([d.page_content for d in docs])
        
        # 2. RAG: Split & Embed
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)
        add_documents_to_db(splits)
        
        # 3. Intelligence: Analyze
        print("Running Legal Analysis on Document...")
        analysis_result = analyze_document_text(full_text)
        
        # 4. Save to DB
        db = SessionLocal()
        try:
            doc_record = db.query(Document).filter(Document.id == doc_id).first()
            if doc_record:
                doc_record.extracted_text = full_text
                doc_record.analysis_json = analysis_result
                db.commit()
                print(f"Document {doc_id} analysis saved.")
        finally:
            db.close()
            
        return True

    except Exception as e:
        print(f"Error processing document: {e}")
        return False