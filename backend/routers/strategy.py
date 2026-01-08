from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from models.models import Case, Document
from services.llm_service import generate_case_strategy
import json

router = APIRouter(prefix="/api/cases", tags=["Strategy"])

@router.post("/{case_id}/strategy")
async def get_case_strategy(case_id: str, db: Session = Depends(get_db)):
    # 1. Fetch Case
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    # 2. Fetch Documents for this case
    docs = db.query(Document).filter(Document.case_id == case_id).all()
    
    # 3. Prepare data for AI
    doc_analyses = [d.analysis_json for d in docs if d.analysis_json]
    case_summary = f"Title: {case.title}. Category: {case.category}. Status: {case.status}"
    
    # 4. Generate Strategy
    strategy_response = generate_case_strategy(case_summary, doc_analyses)
    
    return {"strategy": strategy_response}