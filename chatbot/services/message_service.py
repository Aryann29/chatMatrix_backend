from sqlalchemy.orm import Session
from chatbot.models.session import ChatSession
from chatbot.models.message import ChatMessage
from chatbot.schemas.message import ChatMessageCreate, ChatMessageUpdate, ChatMessageSchema
from user.models.user import User

def get_messages(db: Session, session_id: str, user_id: int):
    session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if not session or session.chatbot.user_id != user_id:
        return []
    return db.query(ChatMessage).filter(ChatMessage.session_id == session_id).all()

def get_message(db: Session, message_id: str, user_id: int):
    message = db.query(ChatMessage).filter(ChatMessage.message_id == message_id).first()
    if message and message.session.chatbot.user_id != user_id:
        return None
    return message

def create_message(db: Session, message: ChatMessageCreate, user_id: int):
    session = db.query(ChatSession).filter(ChatSession.session_id == message.session_id).first()
    if not session or session.chatbot.user_id != user_id:
        return None
    db_message = ChatMessage(
        session_id=message.session_id,
        chatbot_id=session.chatbot_id,
        content=message.content,
        role=message.role
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def update_message(db: Session, message_id: str, user_id: int, message: ChatMessageUpdate):
    db_message = get_message(db, message_id, user_id)
    if not db_message:
        return None
    update_data = message.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_message, key, value)
    db.commit()
    db.refresh(db_message)
    return db_message

def delete_message(db: Session, message_id: str, user_id: int):
    db_message = get_message(db, message_id, user_id)
    if db_message:
        db.delete(db_message)
        db.commit()
    return db_message