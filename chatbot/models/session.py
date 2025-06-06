from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, DateTime
from datetime import datetime, timezone
import uuid
from typing import TYPE_CHECKING
from core.database import Base

if TYPE_CHECKING:
    from chatbot.models.chatbot import Chatbot
    from chatbot.models.message import ChatMessage

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    session_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    chatbot_id: Mapped[str] = mapped_column(ForeignKey("chatbots.chatbot_id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc),
                                                 onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    chatbot: Mapped["Chatbot"] = relationship("Chatbot", back_populates="sessions")
    messages: Mapped[list["ChatMessage"]] = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
