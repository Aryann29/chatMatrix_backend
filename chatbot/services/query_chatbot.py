# app/services/interact_chatbot.py
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from chatbot.models.chatbot import Chatbot
from chatbot.services.chat_history import SQLChatHistory
from chatbot.services.rag_service import initialize_chatbot
from logger import logger

load_dotenv()

def ask_chatbot(db: Session, chatbot_id: str, query: str, session_id: str = None):
    try:
        chat_history = SQLChatHistory(db=db, chatbot_id=chatbot_id, session_id=session_id)
        session_id = chat_history.session_id  
        
        chat_history.add_message(role="user", content=query)
        logger.debug(f"User query added to chat history for session {session_id}")
        
        chatbot = db.query(Chatbot).filter_by(chatbot_id=chatbot_id).first()
        if not chatbot:
            logger.error(f"Chatbot with id {chatbot_id} not found.")
            return "Chatbot not found.", session_id

        rag_chain = initialize_chatbot(db=db, chatbot_id=chatbot_id)
        
        history = chat_history.get_history()
        logger.debug(f"Passing {len(history)} messages from history to RAG chain")
        
        config = {
            "configurable": {
                "session_id": session_id,
            },
            "chat_history_manager": chat_history  
        }
        
        logger.debug(f"Config structure: {list(config.keys())}")
        logger.debug(f"Chat history manager type: {type(chat_history)}")

        answer = rag_chain.invoke(query, config=config)
        
        chat_history.add_message(role="assistant", content=answer)
        logger.debug(f"Assistant answer added to chat history for session {session_id}")
        
        return answer, session_id
        
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}", exc_info=True)
        return "A database error occurred.", session_id
    except Exception as e:
        logger.error(f"Error in ask_chatbot: {e}", exc_info=True)
        return f"An error occurred: {str(e)}", session_id