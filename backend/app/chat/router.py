from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc

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
    current_user: User = Depends(get_current_user)
):
    # --------------------------------------------------
    # 1️⃣ Fetch last 5 messages for this user (memory)
    # --------------------------------------------------
    last_messages = (
        db.query(Message)
        .join(Conversation)
        .filter(Conversation.user_id == current_user.id)
        .order_by(desc(Message.id))
        .limit(5)
        .all()
    )

    # Keep correct chronological order
    last_messages = list(reversed(last_messages))

    chat_history = ""
    for msg in last_messages:
        role = "User" if msg.role == "user" else "Assistant"
        chat_history += f"{role}: {msg.content}\n"

    # --------------------------------------------------
    # 2️⃣ Retrieve RAG context
    # --------------------------------------------------
    rag_context = retrieve_context(req.question)

    # --------------------------------------------------
    # 3️⃣ Combine memory + RAG context
    # --------------------------------------------------
    combined_context = f"""
Conversation History:
{chat_history}

Knowledge Base Context:
{rag_context}
"""

    # --------------------------------------------------
    # 4️⃣ Generate answer using LLM
    # --------------------------------------------------
    answer = generate_answer(combined_context, req.question)

    # --------------------------------------------------
    # 5️⃣ Store conversation & messages (same as before)
    # --------------------------------------------------
    convo = Conversation(user_id=current_user.id)
    db.add(convo)
    db.commit()
    db.refresh(convo)

    db.add_all([
        Message(conversation_id=convo.id, role="user", content=req.question),
        Message(conversation_id=convo.id, role="assistant", content=answer)
    ])
    db.commit()

    return {"answer": answer}
