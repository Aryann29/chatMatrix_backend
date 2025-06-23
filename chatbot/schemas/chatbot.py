from pydantic import BaseModel, constr, Field
from datetime import datetime
from typing import Optional, List
from fastapi import UploadFile

class ChatbotBase(BaseModel):
    name: constr(min_length=1, max_length=255)
    business_name: constr(min_length=1, max_length=255)
    about_business: str = Field(..., min_length=1)
    system_prompt: Optional[str] = ""

class ChatbotCreate(ChatbotBase):
    pass

class ChatbotUpdate(ChatbotBase):
    name: Optional[constr(min_length=1, max_length=255)] = None
    business_name: Optional[constr(min_length=1, max_length=255)] = None
    about_business: Optional[str] = None
    system_prompt: Optional[str] = None
    knowledge_base: Optional[List[UploadFile]] = None 

class ChatbotSchema(ChatbotBase):
    chatbot_id: str
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CreatedChatbotResponse(BaseModel):
    status: str
    message: str
    chatbot_id: str


