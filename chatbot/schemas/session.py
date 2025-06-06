from pydantic import BaseModel, constr
from datetime import datetime
from typing import Optional, List

class ChatSessionBase(BaseModel):
    chatbot_id: constr(min_length=1, max_length=36)

class ChatSessionCreate(ChatSessionBase):
    pass 

class ChatSessionUpdate(ChatSessionBase):
    chatbot_id: Optional[constr(min_length=1, max_length=36)] = None

class ChatSessionSchema(ChatSessionBase):
    session_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class GetSessionResponse(BaseModel):
    sessions: List[ChatSessionSchema]