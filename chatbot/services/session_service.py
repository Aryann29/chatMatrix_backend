from sqlalchemy.orm import Session
from chatbot.models.chatbot import Chatbot
from chatbot.models.session import ChatSession
from chatbot.schemas.session import ChatSessionCreate, ChatSessionUpdate, ChatSessionSchema
from user.models.user import User

def get_sessions(db: Session, chatbot_id: str, user_id: int):

    chatbot = db.query(Chatbot).filter(Chatbot.chatbot_id == chatbot_id, Chatbot.user_id == user_id).first()
    if not chatbot:
        return []
    return db.query(ChatSession).filter(ChatSession.chatbot_id == chatbot_id).all()

def get_session(db: Session, session_id: str, user_id: int):
    session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if session and session.chatbot.user_id != user_id:
        return None
    return session


def delete_session(db: Session, session_id: str, user_id: int):
    db_session = get_session(db, session_id, user_id)
    if db_session:
        db.delete(db_session)
        db.commit()
    return db_session



