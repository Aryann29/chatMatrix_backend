from pydantic import BaseModel, constr
from datetime import datetime
from typing import Optional, List

class ChatMessageBase(BaseModel):
    session_id: constr(min_length=1, max_length=36)
    content: str
    role: constr(min_length=1, max_length=50)

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessageUpdate(BaseModel):
    session_id: Optional[constr(min_length=1, max_length=36)] = None
    content: Optional[str] = None
    role: Optional[constr(min_length=1, max_length=50)] = None

class ChatMessageSchema(ChatMessageBase):
    message_id: str
    chatbot_id: str
    timestamp: datetime  # <-- match SQLAlchemy model

    class Config:
        from_attributes = True

class GetMessagesResponse(BaseModel):
    messages: List[ChatMessageSchema]

class DeletedMessageResponse(BaseModel):
    status: str
    message: str
    message_id: str
