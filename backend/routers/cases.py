from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from models.models import Case
import uuid

router = APIRouter(
    prefix="/api/cases",
    tags=["Cases"]
)

@router.post("/")
async def create_case(payload: dict, db: Session = Depends(get_db)):
    new_case = Case(
        title=payload.get("title", "Untitled Case"),
        category=payload.get("category", "General"),
        status="intake"
    )
    db.add(new_case)
    db.commit()
    db.refresh(new_case)
    return new_case

@router.get("/")
async def list_cases(db: Session = Depends(get_db)):
    return db.query(Case).all()

@router.get("/{case_id}")
async def get_case_details(case_id: str, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case