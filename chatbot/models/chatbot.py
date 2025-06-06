from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, ForeignKey, DateTime
from datetime import datetime, timezone
import uuid
from typing import TYPE_CHECKING
from core.database import Base

if TYPE_CHECKING:
    from user.models.user import User
    from chatbot.models.session import ChatSession
    from chatbot.models.message import ChatMessage
    from chatbot.models.file import ChatbotFile

class Chatbot(Base):
    __tablename__ = "chatbots"

    chatbot_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    business_name: Mapped[str] = mapped_column(String(255), nullable=False)
    about_business: Mapped[str] = mapped_column(Text, nullable=False)
    system_prompt: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc),
                                                 onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="chatbots")
    files: Mapped[list["ChatbotFile"]] = relationship("ChatbotFile", back_populates="chatbot", cascade="all, delete-orphan")
    sessions: Mapped[list["ChatSession"]] = relationship("ChatSession", back_populates="chatbot", cascade="all, delete-orphan")
    messages: Mapped[list["ChatMessage"]] = relationship("ChatMessage", back_populates="chatbot", cascade="all, delete-orphan")
