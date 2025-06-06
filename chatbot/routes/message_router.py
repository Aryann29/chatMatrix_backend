from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from auth.services.auth_service import get_current_active_user
from core.database import get_db
from user.models.user import User
from chatbot.schemas.message import ChatMessageSchema, ChatMessageCreate, ChatMessageUpdate, GetMessagesResponse, DeletedMessageResponse
from chatbot.services.message_service import get_messages, get_message, create_message, update_message, delete_message

message_router = APIRouter(
    prefix='/messages',
    tags=['Messages']
)

@message_router.get('/', response_model=GetMessagesResponse)
def message_list(session_id: str, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")
    messages = get_messages(db, session_id, current_user.id)
    return GetMessagesResponse(messages=messages)

@message_router.get('/{message_id}', response_model=ChatMessageSchema)
def message_detail(message_id: str, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    message = get_message(db, message_id, current_user.id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return message

@message_router.post('/', response_model=ChatMessageSchema, status_code=status.HTTP_201_CREATED)
def message_create(message: ChatMessageCreate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")
    created_message = create_message(db, message, current_user.id)
    if not created_message:
        raise HTTPException(status_code=404, detail="Session not found or not authorized")
    return created_message

@message_router.put('/{message_id}', response_model=ChatMessageSchema)
def message_update(message_id: str, message: ChatMessageUpdate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")
    updated_message = update_message(db, message_id, current_user.id, message)
    if not updated_message:
        raise HTTPException(status_code=404, detail="Message not found or not authorized")
    return updated_message

@message_router.delete('/{message_id}', response_model=DeletedMessageResponse)
def message_delete(message_id: str, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")
    deleted_message = delete_message(db, message_id, current_user.id)
    if not deleted_message:
        raise HTTPException(status_code=404, detail="Message not found or not authorized")
    return DeletedMessageResponse(
        status="success",
        message="Message deleted successfully",
        message_id=message_id
    )