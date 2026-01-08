from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from core.database import get_db
from models.models import Case
import uuid
from routers.auth import get_current_user
from models.models import User

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
        status="intake"
    )

@router.get("/")
async def list_cases(db: Session = Depends(get_db)):
    return db.query(Case).all()

@router.get("/{case_id}")
async def get_case_details(case_id: str, db: Session = Depends(get_db)):
    case = db.query(Case)\
        .options(joinedload(Case.messages), joinedload(Case.documents))\
        .filter(Case.id == case_id)\
        .first()
        
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case