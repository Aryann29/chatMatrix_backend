from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from user.models.user import User
from core.database import get_db
from chatbot.schemas.file import ChatbotFileResponse
from auth.services.auth_service import get_current_active_user
from chatbot.services import file_service
from chatbot.services import chatbot_service
from logger import logger



file_router = APIRouter(
    prefix="/chatbots/{chatbot_id}/files",
    tags=["Chatbot Files"],
)

@file_router.get("/", response_model=List[ChatbotFileResponse])
def get_chatbot_files(
    chatbot_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_chatbot = chatbot_service.get_chatbot(db, chatbot_id, current_user.id)
    if not db_chatbot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chatbot not found or not authorized.")
    # Call the function from the imported module
    files = file_service.get_files_for_chatbot(db, chatbot_id)
    return files

@file_router.get("/{file_id}", response_model=ChatbotFileResponse)
def get_chatbot_file_details(
    chatbot_id: str,
    file_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_chatbot = chatbot_service.get_chatbot(db, chatbot_id, current_user.id)
    if not db_chatbot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chatbot not found or not authorized.")
    # Call the function from the imported module
    file_record = file_service.get_file_by_id(db, file_id, chatbot_id)
    if not file_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found.")
    return file_record

@file_router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chatbot_file_endpoint(
    chatbot_id: str,
    file_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_chatbot = chatbot_service.get_chatbot(db, chatbot_id, current_user.id)
    if not db_chatbot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chatbot not found or not authorized.")

    try:
        # Call the function from the imported module
        deleted_file = file_service.delete_chatbot_file(db, file_id, chatbot_id)
        if not deleted_file:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found.")
        return {"message": "File deleted successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error deleting file {file_id} for chatbot {chatbot_id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete file: {e}")