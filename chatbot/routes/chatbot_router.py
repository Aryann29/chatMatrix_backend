from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from auth.services.auth_service import get_current_active_user
from core.database import get_db
from user.models.user import User
from chatbot.schemas.chatbot import ChatbotSchema, ChatbotCreate, ChatbotUpdate, CreatedChatbotResponse
from chatbot.services.chatbot_service import get_chatbots, get_chatbot, create_chatbot, update_chatbot, delete_chatbot
from chatbot.services.chat_history import SQLChatHistory
from chatbot.schemas.session import ChatSessionCreate
from chatbot.services.query_chatbot import ask_chatbot
from chatbot.models.chatbot import Chatbot

chatbot_router = APIRouter(
    prefix='/chatbots',
    tags=['Chatbots']
)

@chatbot_router.get('/', response_model=List[ChatbotSchema])
def chatbot_list(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")
    chatbots = get_chatbots(db, current_user.id)
    return chatbots

@chatbot_router.get('/{chatbot_id}', response_model=ChatbotSchema)
def chatbot_detail(chatbot_id: str, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    chatbot = get_chatbot(db, chatbot_id, current_user.id)
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    return chatbot

@chatbot_router.post('/', response_model=CreatedChatbotResponse, status_code=status.HTTP_201_CREATED)
async def chatbot_create(
    name: str = Form(...),
    business_name: str = Form(...),
    about_business: str = Form(...),
    system_prompt: str = Form(None),
    knowledge_base: List[UploadFile] = File(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")
    chatbot_data = ChatbotCreate(
        name=name,
        business_name=business_name,
        about_business=about_business,
        system_prompt=system_prompt
    )
    db_chatbot = await create_chatbot(db, chatbot_data, current_user.id, knowledge_base)

    if not db_chatbot:
        raise HTTPException(status_code=400, detail="Failed to create chatbot")
    return CreatedChatbotResponse(
        status="success",
        message="Chatbot created successfully",
        chatbot_id=db_chatbot.chatbot_id
    )

@chatbot_router.put('/{chatbot_id}', response_model=CreatedChatbotResponse)
async def chatbot_update(
    chatbot_id: str,
    name: str = Form(None),
    business_name: str = Form(None),
    about_business: str = Form(None),
    system_prompt: str = Form(None),
    knowledge_base: Optional[List[UploadFile]] = File(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")
    chatbot_data = ChatbotUpdate(
        name=name,
        business_name=business_name,
        about_business=about_business,
        system_prompt=system_prompt
    )
    updated_chatbot = await update_chatbot(db, chatbot_id, current_user.id, chatbot_data, knowledge_base)
    if not updated_chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    return CreatedChatbotResponse(
        status="success",
        message="Chatbot updated successfully",
        chatbot_id=chatbot_id
    )

@chatbot_router.delete('/{chatbot_id}', response_model=CreatedChatbotResponse)
def chatbot_delete(chatbot_id: str, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")
    deleted_chatbot = delete_chatbot(db, chatbot_id, current_user.id)
    if not deleted_chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    return CreatedChatbotResponse(
        status="success",
        message="Chatbot and related data deleted successfully",
        chatbot_id=chatbot_id
    )

@chatbot_router.post('/{chatbot_id}/chat', response_model=dict)
def interact_chatbot(
    chatbot_id: str,
    query: str,
    session_id: str | None = None,
    db: Session = Depends(get_db)
):
    """
    Public endpoint to interact with a chatbot. Creates a new session if session_id is not provided.
    """
    chat_history = SQLChatHistory(db=db, chatbot_id=chatbot_id, session_id=session_id)
    session_id = chat_history.session_id 

    chatbot = db.query(Chatbot).filter(Chatbot.chatbot_id == chatbot_id).first()
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")

    if not session_id:
        session = create_session(db, ChatSessionCreate(chatbot_id=chatbot_id))
        if not session:
            raise HTTPException(status_code=400, detail="Failed to create session")
        session_id = session.session_id

    answer, session_id = ask_chatbot(db, chatbot_id, query, session_id)
    if "error" in answer.lower():
        raise HTTPException(status_code=500, detail=answer)

    return {
        "answer": answer,
        "session_id": session_id
    }