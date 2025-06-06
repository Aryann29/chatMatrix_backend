from chatbot.models.message import ChatMessage
from chatbot.models.session import ChatSession
from sqlalchemy.orm import Session
from datetime import datetime
from logger import logger

class SQLChatHistory:
    def __init__(self, db: Session, chatbot_id: str, session_id: str = None):
        self.db = db
        self.chatbot_id = chatbot_id

        if session_id:
            existing = self.db.query(ChatSession).filter_by(session_id=session_id).first()
            if not existing:
                logger.debug(f"Session ID '{session_id}' not found. Creating new session in DB.")
                session = ChatSession(session_id=session_id, chatbot_id=chatbot_id, created_at=datetime.utcnow())
                try:
                    self.db.add(session)
                    self.db.commit()
                except Exception as e:
                    logger.error(f"Error creating session with provided ID: {e}")
                    self.db.rollback()
                    raise
            else:
                logger.debug(f"Using existing session_id: {session_id}")
            self.session_id = session_id
        else:
            self.session_id = self._create_session()
            logger.debug(f"Created new session_id: {self.session_id}")

    def _create_session(self):
        try:
            session = ChatSession(chatbot_id=self.chatbot_id, created_at=datetime.utcnow())
            self.db.add(session)
            self.db.commit()
            self.db.refresh(session)
            return session.session_id
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            self.db.rollback()
            raise

    def add_message(self, role: str, content: str):
        try:
            message = ChatMessage(
                session_id=self.session_id,
                chatbot_id=self.chatbot_id,
                role=role,
                content=content,
                timestamp=datetime.utcnow()
            )
            self.db.add(message)
            self.db.commit()
            logger.debug(f"Added message role='{role}' content='{content[:50]}...' to session '{self.session_id}'")
        except Exception as e:
            logger.error(f"Error adding message: {e}")
            self.db.rollback()
            raise

    def get_history(self):
        try:
            logger.debug(f"Fetching messages for session_id: {self.session_id} and chatbot_id: {self.chatbot_id}")
            messages = (
                self.db.query(ChatMessage)
                .filter_by(chatbot_id=self.chatbot_id, session_id=self.session_id)
                .order_by(ChatMessage.timestamp.asc())
                .all()
            )
            logger.debug(f"Fetched {len(messages)} messages from DB for session {self.session_id}")
            
            chat = []
            for msg in messages:
                logger.debug(f"Message role: {msg.role}, content preview: {msg.content[:50]}...")
                chat.append({
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat() if msg.timestamp else None
                })
            
            logger.debug(f"Returning {len(chat)} messages as dictionaries")
            return chat
        except Exception as e:
            logger.error(f"Error fetching chat history: {e}")
            return []
