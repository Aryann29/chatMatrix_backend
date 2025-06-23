from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from chatbot.models.file import ChatbotFile
from logger import logger
import os
import shutil

from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

def get_files_for_chatbot(db: Session, chatbot_id: str) -> List[ChatbotFile]:
    """
    Retrieves all file records associated with a specific chatbot.
    """
    logger.info(f"Fetching files for chatbot_id: {chatbot_id}")
    return db.query(ChatbotFile).filter(ChatbotFile.chatbot_id == chatbot_id).all()

def get_file_by_id(db: Session, file_id: str, chatbot_id: str) -> Optional[ChatbotFile]:
    """
    Retrieves a specific file record by its ID and associated chatbot ID.
    """
    logger.info(f"Fetching file_id: {file_id} for chatbot_id: {chatbot_id}")
    return db.query(ChatbotFile).filter(
        ChatbotFile.id == file_id,
        ChatbotFile.chatbot_id == chatbot_id
    ).first()

def delete_chatbot_file(db: Session, file_id: str, chatbot_id: str) -> Optional[ChatbotFile]:
    """
    Deletes a specific chatbot file record, its physical file, and its vector embeddings.
    Returns the deleted ChatbotFile object if successful, None otherwise.
    """
    db_file = get_file_by_id(db, file_id, chatbot_id)
    if not db_file:
        logger.warning(f"File with ID {file_id} not found for chatbot {chatbot_id}.")
        return None

    try:

        try:
            embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
            vector_store = Chroma(
                collection_name="chatbots",
                embedding_function=embeddings,
                persist_directory="./chroma_db" 
            )
            
            vector_store._collection.delete(where={"chatbot_id": chatbot_id, "source": db_file.file_name})
            logger.info(f"Deleted vector embeddings for file: '{db_file.file_name}' (chatbot_id: {chatbot_id})")
        except Exception as e:

            logger.warning(f"Error deleting vector embeddings for file '{db_file.file_name}' (chatbot_id: {chatbot_id}): {e}")


        folder_path = os.path.join("uploads", "chatbot", chatbot_id)
        file_location = os.path.join(folder_path, db_file.file_name)
        
        if os.path.exists(file_location):
            os.remove(file_location)
            logger.info(f"Deleted physical file: {file_location}")
        else:
            logger.warning(f"Physical file not found at: {file_location}. Skipping file system deletion.")


        db.delete(db_file)
        db.commit()
        logger.info(f"ChatbotFile record '{file_id}' deleted successfully from DB for chatbot '{chatbot_id}'.")
        return db_file

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error during file deletion (file_id: {file_id}, chatbot_id: {chatbot_id}): {e}", exc_info=True)

        raise
    except Exception as e:
        db.rollback() 
        logger.error(f"Error during file deletion (file_id: {file_id}, chatbot_id: {chatbot_id}): {e}", exc_info=True)

        raise