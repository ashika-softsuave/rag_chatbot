from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

INTENTS = {
    "onboarding_start",
    "onboarding_answer",
    "resume_onboarding",
    "reject_onboarding",
    "general_chat"
}

def detect_intent(message: str, session_mode: str | None = None) -> str:
    """
    True natural-language intent detection using LLM.
    Deterministic, frontend/backend consistent.
    """

    system_prompt = """
You are a strict intent classification engine for an HR onboarding chatbot.

You MUST return ONLY ONE label from this list:
- onboarding_start
- onboarding_answer
- resume_onboarding
- reject_onboarding
- general_chat

Rules:
- Do NOT explain
- Do NOT add punctuation
- Do NOT add extra words
- Return the label ONLY
"""

    user_prompt = f"""
Conversation state:
- onboarding_active: {session_mode == "onboarding"}
- onboarding_paused: {session_mode == "paused"}

User message:
\"\"\"{message}\"\"\"

Intent:
"""

    response = client.responses.create(
        model="gpt-4o-mini",
        input=[{"role": "system", "content": system_prompt},
               {"role": "user", "content": user_prompt},
              ],
        temperature=0,
        max_output_tokens=16
    )

    intent = response.output_text.strip().lower()

    # HARD SAFETY GUARANTEE
    if intent not in INTENTS:
        return "general_chat"

    #  STATE-AWARE CORRECTIONS
    if session_mode == "onboarding":
        if intent in {"onboarding_start", "resume_onboarding"}:
            return "onboarding_answer"

    if session_mode == "paused":
        if intent == "onboarding_answer":
            return "resume_onboarding"

    return intent
