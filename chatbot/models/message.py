from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, ForeignKey, DateTime
from datetime import datetime, timezone
import uuid
from typing import TYPE_CHECKING
from core.database import Base

if TYPE_CHECKING:
    from chatbot.models.session import ChatSession
    from chatbot.models.chatbot import Chatbot

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    message_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column(ForeignKey("chat_sessions.session_id"), nullable=False, index=True)
    chatbot_id: Mapped[str] = mapped_column(ForeignKey("chatbots.chatbot_id"), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    session: Mapped["ChatSession"] = relationship("ChatSession", back_populates="messages")
    chatbot: Mapped["Chatbot"] = relationship("Chatbot", back_populates="messages")
