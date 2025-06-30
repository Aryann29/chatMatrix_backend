from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from logger import logger
from typing import Optional
from sqlalchemy.orm import Session
from chatbot.models.chatbot import Chatbot
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter



def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def load_documents(file_path, chatbot_id):
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    for doc in documents:
        doc.metadata.update({"chatbot_id": chatbot_id})
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return text_splitter.split_documents(documents)

def add_to_vector_db(chunks, chatbot_id):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = Chroma(
        collection_name="chatbots",
        embedding_function=embeddings,
        persist_directory="./chroma_db"
    )

    vector_store.add_documents(documents=chunks)
    logger.info(f"Chunks added to vector DB for chatbot_id={chatbot_id}")

def initialize_chatbot(db: Session, chatbot_id: str, user_id: Optional[int] = None):
    """
    Initialize a RAG chain for a chatbot with chat history support.
    """

    chatbot = db.query(Chatbot).filter(Chatbot.chatbot_id == chatbot_id).first()
    if not chatbot:
        logger.error(f"Chatbot {chatbot_id} not found")
        return None

    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = Chroma(
        collection_name="chatbots",
        embedding_function=embeddings,
        persist_directory="./chroma_db"
    )

    retriever = vector_store.as_retriever(
        search_kwargs={"k": 3, "filter": {"chatbot_id": chatbot_id}}
    )

    model = AzureChatOpenAI(
        azure_deployment="gpt-4o",
        api_version="2024-08-01-preview",
        temperature=0
    )

    system_prompt = chatbot.system_prompt or "You are a helpful assistant. Use the context provided to answer user queries."

    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}"),
    ])

    def convert_to_langchain_messages(messages):
        converted = []
        for msg in messages:
            if isinstance(msg, dict):
                role = msg.get("role")
                content = msg.get("content", "")
                if role == "user":
                    converted.append(HumanMessage(content=content))
                elif role == "assistant":
                    converted.append(AIMessage(content=content))
            else:
                converted.append(msg)
        return converted

    def rag_with_history(inputs, config=None):
        if isinstance(inputs, str):
            question = inputs
        elif isinstance(inputs, dict):
            question = inputs.get("question", inputs.get("input", str(inputs)))
        else:
            question = str(inputs)

        logger.debug(f"Processing question: {question}")

        # Extract chat history manager
        chat_history_manager = None
        if config:
            chat_history_manager = config.get("chat_history_manager")
            if not chat_history_manager:
                configurable = config.get("configurable", {})
                chat_history_manager = configurable.get("chat_history_manager")

        history_messages = []
        if chat_history_manager:
            try:
                messages = chat_history_manager.get_history()
                logger.debug(f"Retrieved {len(messages)} messages from history")

                recent_messages = messages[-5:] if len(messages) > 5 else messages
                history_messages = convert_to_langchain_messages(recent_messages)
            except Exception as e:
                logger.error(f"Error retrieving chat history: {e}")
        else:
            logger.warning("No chat_history_manager provided in config")

        try:
            docs = retriever.invoke(question)
            context = "\n\n".join(doc.page_content for doc in docs)
            logger.debug(f"Retrieved {len(docs)} documents, context length: {len(context)}")
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            context = ""

        prompt_input = {
            "context": context,
            "question": question,
            "history": history_messages
        }

        logger.debug(f"Final prompt input - Context length: {len(context)}, History length: {len(history_messages)}")

        try:
            response = (qa_prompt | model | StrOutputParser()).invoke(prompt_input)
            logger.debug(f"Generated response: {response[:100]}...")
            return response
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I apologize, but I encountered an error while processing your question. Please try again."

    return RunnableLambda(rag_with_history)
