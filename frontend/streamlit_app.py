import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="RAG Chatbot", layout="centered")
st.title("🤖 RAG Chatbot")

# ---------------- AUTH ----------------
st.subheader("🔐 Authentication")

token = st.text_input(
    "JWT Token",
    type="password",
    placeholder="Paste your JWT token here"
)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------------- CHAT ----------------
st.subheader("💬 Ask a Question")

question = st.text_input(
    "Your Question",
    placeholder="Type your question here..."
)

ask_btn = st.button("Ask")

if ask_btn:
    st.write("✅ Ask button clicked")

    if not token:
        st.warning("⚠️ Please enter JWT token")
        st.stop()

    if not question.strip():
        st.warning("⚠️ Please enter a question")
        st.stop()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    st.write("📤 Sending request to backend...")

    try:
        res = requests.post(
            f"{API_URL}/chat/",
            json={"question": question},
            headers=headers,
            timeout=30
        )

        st.write("📥 Response status:", res.status_code)
        st.write("📥 Raw response:", res.text)

        if res.status_code == 200:
            answer = res.json().get("answer", "No answer key")
            st.success(answer)
        else:
            st.error("Backend error")

    except Exception as e:
        st.error(f"❌ Exception occurred: {e}")


# ---------------- CHAT HISTORY ----------------
if st.session_state.chat_history:
    st.subheader("📝 Conversation")

    for role, msg in st.session_state.chat_history:
        if role == "You":
            st.markdown(f"**🧑 You:** {msg}")
        else:
            st.markdown(f"**🤖 Bot:** {msg}")
