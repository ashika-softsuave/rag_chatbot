from openai import OpenAI
from backend.app.core.config import get_settings

settings = get_settings()
client = OpenAI(api_key=settings.OPENAI_API_KEY)

def generate_answer(context: str, question: str) -> str:
    prompt = f"""
    You are a helpful, friendly assistant.

    Guidelines:
    1. Use conversation history and the knowledge base context when they are relevant.
    2. If the question is a general greeting, introduction, or normal conversational query,
       respond naturally like a chat assistant.
    3. If the question is related to the provided context, answer strictly using that context.
    4. Say "Answer not available in documents" ONLY when the question is clearly about
       the documents but the answer is missing.

    Context:
    {context if context else "No relevant context found."}

    Question:
    {question}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return response.choices[0].message.content
