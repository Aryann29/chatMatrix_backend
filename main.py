from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from core.config_loader import settings
from user.models.user import User  # Import User model
from core import models 
from auth.routes.auth_router import auth_router
from user.routes.user_router import user_router
from chatbot.routes.chatbot_router import chatbot_router
from chatbot.routes.session_router import session_router
from chatbot.routes.message_router import message_router

openapi_tags = [
    {
        "name": "Users",
        "description": "User operations",
    },
    {
        "name": "Health Checks",
        "description": "Application health checks",
    }
]

app = FastAPI(openapi_tags=openapi_tags)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            str(origin).strip("/") for origin in settings.BACKEND_CORS_ORIGINS
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(auth_router, prefix='/api')
app.include_router(user_router, prefix='/api', tags=['Users'])
app.include_router(chatbot_router, prefix='/api', tags=['Chatbots'])
app.include_router(session_router, prefix='/api', tags=['Sessions'])
app.include_router(message_router, prefix='/api', tags=['Messages'])

@app.get("/health", tags=['Health Checks'])
def read_root():
    return {"health": "true"}

