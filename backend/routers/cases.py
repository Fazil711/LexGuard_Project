from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from core.database import get_db
from models.models import Case, User
from routers.auth import get_current_user
import os
from models.models import CaseMessage, Document
from services.rag_service import delete_case_vectors

router = APIRouter(
    prefix="/api/cases",
    tags=["Cases"]
)

@router.post("/")
async def create_case(
    payload: dict, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_case = Case(
        title=payload.get("title"),
        category=payload.get("category"),
        status="intake",
    )
    
    db.add(new_case)
    db.commit()
    db.refresh(new_case)
    
    return new_case

@router.get("/")
async def list_cases(db: Session = Depends(get_db)):
    return db.query(Case).order_by(Case.created_at.desc()).all()

@router.get("/{case_id}")
async def get_case_details(case_id: str, db: Session = Depends(get_db)):
    case = db.query(Case)\
        .options(joinedload(Case.messages), joinedload(Case.documents))\
        .filter(Case.id == case_id)\
        .first()
        
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case

@router.delete("/{case_id}")
async def delete_case(
    case_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    documents = db.query(Document).filter(Document.case_id == case_id).all()
    for doc in documents:
        if doc.s3_key and os.path.exists(doc.s3_key):
            try:
                os.remove(doc.s3_key)
                print(f"Deleted file: {doc.s3_key}")
            except Exception as e:
                print(f"Error deleting file {doc.s3_key}: {e}")

    delete_case_vectors(case_id)

    db.query(CaseMessage).filter(CaseMessage.case_id == case_id).delete()
    db.query(Document).filter(Document.case_id == case_id).delete()
    
    db.delete(case)
    db.commit()

    return {"message": "Case and all associated data deleted successfully"}