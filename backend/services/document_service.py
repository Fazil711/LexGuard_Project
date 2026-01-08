import os
import shutil
from fastapi import UploadFile
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from services.rag_service import add_documents_to_db
from core.database import SessionLocal
from models.models import Document
from services.llm_service import analyze_document_text

UPLOAD_DIR = "./uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def save_upload_file(upload_file: UploadFile) -> str:
    file_path = os.path.join(UPLOAD_DIR, upload_file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    return file_path

def process_document(file_path: str, doc_id: str):
    print(f"Processing file: {file_path}")
    docs = []
    
    db = SessionLocal()
    try:
        # 1. Load File
        if file_path.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
            docs.extend(loader.load())
        elif file_path.endswith(".txt"):
            loader = TextLoader(file_path, encoding='utf-8')
            docs.extend(loader.load())
            
        if not docs:
            print("❌ Error: No text found in document.")
            return False

        full_text = "\n".join([d.page_content for d in docs])
        
        # 2. Get Case ID (CRITICAL FOR RAG)
        doc_record = db.query(Document).filter(Document.id == doc_id).first()
        current_case_id = doc_record.case_id if doc_record else "unknown"

        # 3. Split & Embed with Metadata
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)
        
        # --- FIX: Add metadata to every chunk ---
        for split in splits:
            split.metadata["case_id"] = current_case_id
            split.metadata["doc_id"] = doc_id
        
        add_documents_to_db(splits)
        
        # 4. Analyze & Save
        print("Running Legal Analysis...")
        analysis_result = analyze_document_text(full_text)
        
        if doc_record:
            doc_record.extracted_text = full_text
            doc_record.analysis_json = analysis_result
            db.commit()
            print(f"✅ Document {doc_id} processed & saved.")
            
        return True

    except Exception as e:
        print(f"❌ Error processing document: {e}")
        return False
    finally:
        db.close()