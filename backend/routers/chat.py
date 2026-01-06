from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from models.models import CaseMessage, Case
from services.llm_service import get_chat_response

router = APIRouter(prefix="/api/cases", tags=["Chat"])

@router.post("/{case_id}/messages")
async def send_message(case_id: str, payload: dict, db: Session = Depends(get_db)):
    """
    Receives a user message, gets AI response, saves both to DB.
    """
    user_content = payload.get("content")
    if not user_content:
        raise HTTPException(status_code=400, detail="Message content is required")

    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    user_msg = CaseMessage(
        case_id=case_id,
        sender="user",
        content=user_content
    )
    db.add(user_msg)
    db.commit()

    ai_text = get_chat_response(case_id, user_content)

    ai_msg = CaseMessage(
        case_id=case_id,
        sender="ai",
        content=ai_text
    )
    db.add(ai_msg)
    db.commit()

    return {
        "user_message": user_msg.content,
        "ai_response": ai_msg.content
    }