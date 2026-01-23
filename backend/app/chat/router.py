from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.auth.dependencies import get_current_user
from backend.app.db.models.user import User

from backend.app.chat.schemas import ChatRequest
from backend.app.chat.service import (
    chat_service,
    list_conversations_service,
    get_conversation_messages_service
)

router = APIRouter(prefix="/chat", tags=["Chat"])


#CHAT
@router.post("/chat")
def chat(
    req: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return chat_service(req, db, current_user)


#LIST CONVERSATIONS
@router.get("/conversations")
def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return list_conversations_service(db, current_user)


# GET CONVERSATION MESSAGES
@router.get("/conversations/{conversation_id}")
def get_conversation_messages(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_conversation_messages_service(
        db, current_user, conversation_id
    )
