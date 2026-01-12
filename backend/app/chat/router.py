from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.db.models.conversation import Conversation
from backend.app.db.models.message import Message
from backend.app.chat.schemas import ChatRequest, ChatResponse
from backend.app.rag.retriever import retrieve_context
from backend.app.rag.llm import generate_answer
from backend.app.auth.dependencies import get_current_user
from backend.app.db.models.user import User

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
def chat(
    req: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # ✅ JWT protected
):
    context = retrieve_context(req.question)
    answer = generate_answer(context, req.question)

    convo = Conversation(user_id=current_user.id)  # ✅ multi-user safe
    db.add(convo)
    db.commit()
    db.refresh(convo)

    db.add_all([
        Message(conversation_id=convo.id, role="user", content=req.question),
        Message(conversation_id=convo.id, role="assistant", content=answer)
    ])
    db.commit()

    return {"answer": answer}
