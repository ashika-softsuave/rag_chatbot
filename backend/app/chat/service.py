from sqlalchemy import desc
from backend.app.chat.intent import detect_intent
from backend.app.db.models.conversation import Conversation
from backend.app.db.models.message import Message
from backend.app.onboarding.constants import ONBOARDING_STEPS
from backend.app.rag.retriever import retrieve_context
from backend.app.rag.llm import generate_answer
from backend.app.onboarding.service import (
    onboarding_next_service,
    get_or_create_employee,
    get_next_question
)

# ================= HELPER =================
def answer_with_rag(req, db, convo):
    last_messages = (
        db.query(Message)
        .filter(Message.conversation_id == convo.id)
        .order_by(desc(Message.id))
        .limit(5)
        .all()
    )

    chat_history = ""
    for msg in reversed(last_messages):
        role = "User" if msg.role == "user" else "Assistant"
        chat_history += f"{role}: {msg.content}\n"

    rag_context = retrieve_context(req.question)

    combined_context = f"""
Conversation History:
{chat_history}

Knowledge Base Context:
{rag_context}
"""

    return generate_answer(combined_context, req.question)


# ================= VALIDATION =================
def is_valid_onboarding_answer(step: str, message: str) -> bool:
    message = message.strip()

    if step == "name":
        return len(message) >= 2 and message.replace(" ", "").isalpha()

    if step == "phone":
        return message.isdigit() and len(message) == 10

    if step == "tech_stack":
        return message.lower() in ["python", "java", "node", "qa"]

    if step in ["tenth_percentage", "twelfth_percentage"]:
        return message.isdigit() and 0 <= int(message) <= 100

    if step == "confirm":
        return message.lower() in ["yes", "no"]

    return False


# ================= CHAT SERVICE =================
def chat_service(req, db, current_user):

    employee = get_or_create_employee(db, current_user)

    # -------- NORMALIZE STATE --------
    state = employee.onboarding_state or {}
    state.setdefault("active", False)
    state.setdefault("paused", False)
    state.setdefault("completed", False)
    state.setdefault("step_index", 0)
    state.setdefault("data", {})

    # -------- HARD STOP IF COMPLETED --------
    if state["step_index"] >= len(ONBOARDING_STEPS):
        state.update({
            "active": False,
            "paused": False,
            "completed": True
        })
        employee.onboarding_state = state
        db.commit()

        return {
            "type": "chat",
            "answer": "🎉 Onboarding already completed. How can I help you?"
        }

    onboarding_active = state["active"]
    onboarding_paused = state["paused"]

    print("USER:", req.question)
    print("STATE BEFORE:", state)

    # -------- GET / CREATE CONVERSATION --------
    convo = (
        db.query(Conversation)
        .filter(Conversation.user_id == current_user.id)
        .order_by(desc(Conversation.id))
        .first()
    )

    if not convo:
        convo = Conversation(user_id=current_user.id, title=req.question[:40])
        db.add(convo)
        db.commit()
        db.refresh(convo)

    # ======================================================
    # 1️⃣ START ONBOARDING
    # ======================================================
    if not onboarding_active and not state["completed"]:
        intent = detect_intent(req.question, None)

        if intent == "onboarding_start":
            state.update({
                "active": True,
                "paused": False,
                "step_index": 0,
                "data": {}
            })
            employee.onboarding_state = state
            db.commit()

            return {
                "type": "onboarding",
                "message": get_next_question("name"),
                "step": "name",
                "conversation_id": convo.id
            }

    # ======================================================
    # 2️⃣ ONBOARDING ACTIVE
    # ======================================================
    if onboarding_active:

        # ---------- RESUME MODE ----------
        if onboarding_paused:
            intent = detect_intent(req.question, "paused")

            if intent == "resume_onboarding":
                state["paused"] = False
                employee.onboarding_state = state
                db.commit()

                step = ONBOARDING_STEPS[state["step_index"]]

                return {
                    "type": "onboarding",
                    "message": get_next_question(step),
                    "step": step,
                    "conversation_id": convo.id
                }

            # declined resume → normal chat
            answer = answer_with_rag(req, db, convo)
            return {
                "type": "chat",
                "answer": answer,
                "conversation_id": convo.id
            }

        # ---------- VALIDATE ANSWER FIRST ----------
        current_step = ONBOARDING_STEPS[state["step_index"]]

        if is_valid_onboarding_answer(current_step, req.question):
            res = onboarding_next_service(db, current_user, req.question)

            if res.get("completed"):
                state.update({
                    "active": False,
                    "paused": False,
                    "completed": True
                })
                employee.onboarding_state = state
                db.commit()

                return {
                    "type": "chat",
                    "answer": "🎉 Onboarding completed successfully! How can I help you now?",
                    "conversation_id": convo.id
                }

            return {
                "type": "onboarding",
                "message": res["message"],
                "step": res["step"],
                "conversation_id": convo.id
            }

        # ---------- INTERRUPTION ----------
        state["paused"] = True
        employee.onboarding_state = state
        db.commit()

        answer = answer_with_rag(req, db, convo)
        return {
            "type": "handoff",
            "answer": answer,
            "followup": "Shall we continue onboarding?",
            "conversation_id": convo.id
        }

    # ======================================================
    # 3️⃣ NORMAL CHAT
    # ======================================================
    answer = answer_with_rag(req, db, convo)

    db.add_all([
        Message(conversation_id=convo.id, role="user", content=req.question),
        Message(conversation_id=convo.id, role="assistant", content=answer)
    ])
    db.commit()

    return {
        "type": "chat",
        "answer": answer,
        "conversation_id": convo.id
    }


# ================= CHAT HISTORY =================
def list_conversations_service(db, current_user):
    return (
        db.query(Conversation)
        .filter(Conversation.user_id == current_user.id)
        .order_by(Conversation.id.desc())
        .all()
    )


def get_conversation_messages_service(db, current_user, conversation_id):
    return (
        db.query(Message)
        .join(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        )
        .order_by(Message.id)
        .all()
    )
