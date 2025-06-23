from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from chatbot.models.chatbot import Chatbot
from chatbot.models.file import ChatbotFile
from chatbot.schemas.chatbot import ChatbotCreate, ChatbotUpdate, CreatedChatbotResponse
from user.models.user import User
import uuid
import os
import shutil
from fastapi import UploadFile, HTTPException
from logger import logger
from typing import List, Optional

def get_chatbots(db: Session, user_id: int):
    return db.query(Chatbot).filter(Chatbot.user_id == user_id).all()

def get_chatbot(db: Session, chatbot_id: str, user_id: int):
    return db.query(Chatbot).filter(Chatbot.chatbot_id == chatbot_id, Chatbot.user_id == user_id).first()

async def save_upload_file(upload_file: UploadFile, folder_path: str) -> str:
    if not upload_file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    os.makedirs(folder_path, exist_ok=True)
    file_location = os.path.join(folder_path, upload_file.filename)
    with open(file_location, "wb") as f:
        content = await upload_file.read()
        f.write(content)
    return file_location

def save_chatbot_info(chatbot_id: str, name: str, business_name: str, about_business: str, system_prompt: str, user_id: int, db: Session):
    db_chatbot = Chatbot(
        chatbot_id=chatbot_id,
        user_id=user_id,
        name=name,
        business_name=business_name,
        about_business=about_business,
        system_prompt=system_prompt
    )
    db.add(db_chatbot)
    db.commit()
    db.refresh(db_chatbot)
    return db_chatbot

async def create_chatbot(db: Session, chatbot: ChatbotCreate, user_id: int, knowledge_base: Optional[List[UploadFile]] = None):
    try:
        chatbot_id = str(uuid.uuid4())
        folder_path = f"uploads/chatbot/{chatbot_id}"

        system_prompt = chatbot.system_prompt or f"""You are a helpful assistant for {chatbot.business_name}.
        Context about {chatbot.business_name}:
        {chatbot.about_business}

        Your role:
        - Provide comprehensive assistance to customers with their queries about {chatbot.business_name}'s products, services, policies, returns, terms & conditions, etc., using the provided context from company documents.
        - Answer questions about the business using the provided context from company documents
        - Provide accurate information based on the company's official documentation
        - Remember details from recent conversation for better assistance
        - Be professional, friendly, and helpful

        Guidelines:
        - ALWAYS use the provided context from documents when available
        - If information isn't in the documents, politely say you don't have that specific information
        - For personal questions or conversation references, use the chat history
        - Keep responses concise and relevant to business inquiries
        - If you need clarification, ask specific questions

        Context from company documents:
        {{context}}
        Question: {{question}}"""

        db_chatbot = save_chatbot_info(
            chatbot_id=chatbot_id,
            name=chatbot.name,
            business_name=chatbot.business_name,
            about_business=chatbot.about_business,
            system_prompt=system_prompt,
            user_id=user_id,
            db=db
        )

        if knowledge_base:
            from chatbot.services.rag_service import load_documents, add_to_vector_db
            from langchain_chroma import Chroma
            from langchain_google_genai import GoogleGenerativeAIEmbeddings

            # Step 1: Delete existing vectors for this chatbot_id
            try:
                embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
                vector_store = Chroma(
                    collection_name="chatbots",
                    embedding_function=embeddings,
                    persist_directory="./chroma_db"
                )
                vector_store._collection.delete(where={"chatbot_id": chatbot_id})
                logger.info(f"Deleted old vector entries for chatbot_id={chatbot_id}")
            except Exception as e:
                logger.error(f"Error deleting previous vectors: {e}")

            # Step 2: Delete old file records from DB
            db.query(ChatbotFile).filter_by(chatbot_id=chatbot_id).delete()

            # Step 3: Clear old folder (if exists)
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)
            os.makedirs(folder_path, exist_ok=True)

            # Step 4: Process and save all files
            for file in knowledge_base:
                saved_path = await save_upload_file(file, folder_path)
                chunks = load_documents(saved_path, chatbot_id)
                add_to_vector_db(chunks, chatbot_id=chatbot_id)

                db.add(ChatbotFile(
                    chatbot_id=chatbot_id,
                    file_name=file.filename,
                    file_type="pdf"
                ))

            db.commit()

        return db_chatbot

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error during chatbot creation: {e}")
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error during chatbot creation: {e}")
        raise

async def update_chatbot(db: Session, chatbot_id: str, user_id: int, chatbot: ChatbotUpdate, knowledge_base: Optional[List[UploadFile]] = None):
    try:
        db_chatbot = get_chatbot(db, chatbot_id, user_id)
        if not db_chatbot:
            return None
        update_data = chatbot.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_chatbot, key, value)
        if knowledge_base:
            from chatbot.services.rag_service import load_documents, add_to_vector_db
            folder_path = f"uploads/chatbot/{chatbot_id}"
            os.makedirs(folder_path, exist_ok=True)
            for file in knowledge_base:
                existing_file = db.query(ChatbotFile).filter_by(
                    chatbot_id=chatbot_id, 
                    file_name=file.filename
                ).first()
                if existing_file:
                    logger.info(f"File {file.filename} already exists for chatbot {chatbot_id}, skipping...")
                    continue
                saved_path = await save_upload_file(file, folder_path)
                chunks = load_documents(saved_path, chatbot_id)
                add_to_vector_db(chunks, chatbot_id=chatbot_id)
                db.add(ChatbotFile(
                    chatbot_id=chatbot_id,
                    file_name=file.filename,
                    file_type="pdf"
                ))
            logger.info(f"Added new files to knowledge base for chatbot_id={chatbot_id}")
        db.commit()
        db.refresh(db_chatbot)
        return db_chatbot
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error during chatbot update: {e}")
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error during chatbot update: {e}")
        raise
def delete_chatbot(db: Session, chatbot_id: str, user_id: int):
    try:
        db_chatbot = get_chatbot(db, chatbot_id, user_id)
        if not db_chatbot:
            return None
        folder_path = f"uploads/chatbot/{chatbot_id}"
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
        db.delete(db_chatbot)
        db.commit()
        return db_chatbot
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error during chatbot deletion: {e}")
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error during chatbot deletion: {e}")
        raise