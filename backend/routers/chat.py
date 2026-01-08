from sqlalchemy.orm import Session
from core.database import get_db
from models.models import CaseMessage, Case
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from services.document_service import save_upload_file 
from services.llm_service import get_chat_response, transcribe_audio

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


@router.post("/{case_id}/voice")
async def send_voice_message(
    case_id: str, 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    """
    1. Upload Audio
    2. Transcribe to Text (Whisper)
    3. Process as normal Chat Message
    """
    # 1. Save Audio File Temporarily
    file_path = await save_upload_file(file)
    
    # 2. Transcribe
    transcribed_text = transcribe_audio(file_path)
    if not transcribed_text:
        raise HTTPException(status_code=500, detail="Failed to transcribe audio")
        
    # 3. Save "User" Message (The transcribed text)
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    user_msg = CaseMessage(
        case_id=case_id,
        sender="user", 
        content=f"[Voice Input]: {transcribed_text}" 
    )
    db.add(user_msg)
    db.commit()

    # 4. Get AI Response (Same as text chat!)
    ai_text = get_chat_response(case_id, transcribed_text)

    ai_msg = CaseMessage(
        case_id=case_id,
        sender="ai",
        content=ai_text
    )
    db.add(ai_msg)
    db.commit()

    return {
        "transcription": transcribed_text,
        "ai_response": ai_text
    }