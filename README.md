# ChatMatrix

**ChatMatrix** is a SaaS platform that allows users to create and manage AI-powered chatbots with minimal effort. These chatbots can be easily embedded into any website via a simple HTML snippet. The platform emphasizes Retrieval-Augmented Generation (RAG), LangChain, and modern AI tooling to deliver intelligent, context-aware conversations.

## Key Features

* **Custom AI Chatbots**: Users can create multiple personalized chatbots.
* **LangChain & RAG Integration**: Built with a focus on advanced retrieval and reasoning using LangChain and RAG.
* **Google Gemini Embeddings**: Uses Google Gemini for document embeddings.
* **Chroma Vector Store**: Efficient and scalable vector storage.
* **Embeddable Widgets**: Easily generate scripts to embed chatbots in any website.
* **Session-Based Memory**: Tracks and stores chat history per session using PostgreSQL.
* **API-Driven**: RESTful API for chatbot configuration, chat sessions, and integration.

## Tech Stack

* **AI / LLMs**: LangChain, Gemini Embeddings, Azure OpenAI (configurable)
* **Vector Store**: Chroma
* **Backend**: FastAPI (async)
* **ORM**: SQLAlchemy 2.0
* **Migrations**: Alembic
* **Database**: PostgreSQL
* **Environment Management**: Type-safe `.env` via Pydantic
* **Containerization**: Docker & Docker Compose

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/chatmatrix.git
cd chatmatrix
```

### 2. Set Up Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # For Linux/macOS
# OR
.venv\Scripts\activate  # For Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.local .env
# Update DATABASE_URL, GEMINI_API_KEY, OPENAI_API_KEY, etc.
```

### 5. Run Migrations

```bash
alembic upgrade head
```

### 6. Start Development Server

```bash
uvicorn main:app --reload
```

### 7. (Optional) Run with Docker Compose

```bash
docker-compose up --build
```

## AI & RAG Architecture

ChatMatrix integrates RAG-based pipelines using LangChain:

* **Embedding**: Documents are embedded using Google Gemini.
* **Storage**: Chroma is used as the vector store backend.
* **Retrieval**: LangChain's RetrievalQA system fetches relevant chunks from Chroma.
* **LLM Interface**: Queries are passed to Azure OpenAI (or any pluggable LLM provider).

This design allows users to build smart, context-aware chatbots over their own documents.

## Current API Functionality

* `POST /api/chatbots` - Create chatbot
* `GET /api/chatbots/{id}` - Retrieve chatbot configuration
* `POST /api/chatbots/{id}/query` - Query a chatbot with optional session tracking
* `GET /api/chatbots/{id}/history/{session_id}` - Get session chat history

## Roadmap

* [x] LangChain + RAG backend with Gemini embeddings
* [x] Vector storage using Chroma
* [x] Session-based chat message storage
* [x] Basic chatbot creation and querying APIs
* [ ] User authentication system
* [ ] Admin panel for managing chatbots
* [ ] Embeddable widget generator
* [ ] User document upload support (PDF, text)
* [ ] Frontend UI (React)
* [ ] Dockerized production-ready deployment

## License

MIT License

---

Want to contribute? Open an issue or discussion to get started!
