from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from auth.services.auth_service import get_current_active_user
from core.database import get_db
from user.models.user import User
from chatbot.schemas.session import ChatSessionSchema, ChatSessionCreate, ChatSessionUpdate, GetSessionResponse


session_router = APIRouter(
    prefix='/sessions',
    tags=['Sessions']
)

@session_router.get('/', response_model=GetSessionResponse)
def session_list(chatbot_id: str, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")
    sessions = get_sessions(db, chatbot_id, current_user.id)
    return GetSessionResponse(sessions=sessions)

@session_router.get('/{session_id}', response_model=ChatSessionSchema)
def session_detail(session_id: str, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    session = get_session(db, session_id, current_user.id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@session_router.delete('/{session_id}', response_model=dict)
def session_delete(session_id: str, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")
    deleted_session = delete_session(db, session_id, current_user.id)
    if not deleted_session:
        raise HTTPException(status_code=404, detail="Session not found or not authorized")
    return {"message": "Session deleted"}