from openai import OpenAI
from backend.app.core.config import get_settings

settings = get_settings()
client = OpenAI(api_key=settings.OPENAI_API_KEY)

def generate_answer(context: str, question: str) -> str:
    prompt = f"""
You are a helpful assistant.

Use BOTH:
1. Conversation history
2. Knowledge base context

Answer the question clearly.
If the answer is not found in either, say:
"Answer not available in documents".
Context:
{context}

Question:
{question}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return response.choices[0].message.content
