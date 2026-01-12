import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.title("RAG Chatbot")

# 🔐 TEMP: Paste token here (from /auth/login)
token = st.text_input("JWT Token", type="password")

question = st.text_input("Ask a question")

if st.button("Ask"):
    if not token:
        st.warning("Please enter JWT token")
    else:
        headers = {
            "Authorization": f"Bearer {token}"
        }

        res = requests.post(
            f"{API_URL}/chat/",
            json={"question": question},
            headers=headers
        )

        if res.status_code == 200:
            st.success(res.json()["answer"])
        else:
            st.error(f"Error: {res.status_code} - {res.text}")
