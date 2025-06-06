from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, DateTime
from datetime import datetime, timezone
import uuid
from core.database import Base

class ChatbotFile(Base):
    __tablename__ = "chatbot_files"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    chatbot_id: Mapped[str] = mapped_column(String(36), ForeignKey("chatbots.chatbot_id"), nullable=False, index=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    chatbot: Mapped["Chatbot"] = relationship("Chatbot", back_populates="files")