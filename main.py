from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.db.models.user import User
from backend.app.db.models.otp import OTP
from backend.app.db.models.conversation import Conversation
from backend.app.db.models.message import Message
from backend.app.onboarding.router import router as onboarding_router
from backend.app.admin.router import router as admin_router

from backend.app.auth.router import router as auth_router
from backend.app.documents.router import router as doc_router
from backend.app.chat.router import router as chat_router
from backend.app.db.database import engine
from backend.app.db.base import Base

from backend.app.core.config import get_settings
from backend.app.core.logging import setup_logging
from backend.app.core.errors import (
    AppException,
    app_exception_handler,
    unhandled_exception_handler,
)
Base.metadata.create_all(bind=engine)
settings = get_settings()
setup_logging()

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    debug=settings.DEBUG,
)

# ✅ REGISTER ROUTERS (THIS IS THE KEY)
app.include_router(auth_router)
app.include_router(doc_router)
app.include_router(chat_router)
# app.include_router(onboarding_router)

app.include_router(admin_router)
# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "environment": settings.ENVIRONMENT,
    }
