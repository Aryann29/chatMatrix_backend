from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ChatbotFileResponse(BaseModel):
    id: str
    chatbot_id: str
    file_name: str
    file_type: str
    created_at: datetime

    class Config:
        from_attributes = True # Enable ORM mode for Pydantic v2+