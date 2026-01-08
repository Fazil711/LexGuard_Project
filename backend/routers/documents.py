from fastapi import APIRouter, UploadFile, File, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from models.models import Document
from services.document_service import save_upload_file, process_document

router = APIRouter(prefix="/api/cases", tags=["Documents"])

@router.post("/{case_id}/documents")
async def upload_document(
    case_id: str, 
    background_tasks: BackgroundTasks, 
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    file_path = await save_upload_file(file)
    
    new_doc = Document(
        case_id=case_id,
        filename=file.filename,
        s3_key=file_path, 
        extracted_text="Processing...", 
        analysis_json={}
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    
    background_tasks.add_task(process_document, file_path, new_doc.id)
    
    return {"message": "File uploaded and processing started", "doc_id": new_doc.id}