import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

def safe_error_message(res, default="Something went wrong"):
    try:
        return res.json().get("detail", default)
    except Exception:
        return f"{default} (status code {res.status_code})"

st.set_page_config(
    page_title="RAG Chatbot",
    page_icon="🤖",
    layout="wide"
)

# ---------------- SESSION STATE ----------------
if "token" not in st.session_state:
    st.session_state.token = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_titles" not in st.session_state:
    st.session_state.chat_titles = []

if "pending_email" not in st.session_state:
    st.session_state.pending_email = None

if "otp_verified" not in st.session_state:
    st.session_state.otp_verified = False

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("🤖 RAG Chatbot")

    if not st.session_state.token:
        tab1, tab2 = st.tabs(["Login", "Sign Up"])

        # -------- LOGIN --------
        with tab1:
            login_email = st.text_input("Email", key="login_email")
            login_password = st.text_input("Password", type="password", key="login_password")

            if st.button("Login"):
                res = requests.post(
                    f"{API_URL}/auth/login",
                    json={"email": login_email, "password": login_password}
                )

                if res.status_code == 200:
                    st.session_state.token = res.json()["access_token"]
                    st.success("Logged in successfully")
                    st.rerun()
                else:
                    st.error(safe_error_message(res, "Login failed"))

        # -------- SIGN UP --------
        with tab2:
            signup_email = st.text_input("Email", key="signup_email")
            signup_password = st.text_input("Password", type="password", key="signup_password")

            if st.button("Sign Up"):
                res = requests.post(
                    f"{API_URL}/auth/register",
                    json={"email": signup_email, "password": signup_password}
                )

                if res.status_code == 200:
                    st.session_state.pending_email = signup_email
                    st.success("OTP sent to your email")
                else:
                    st.error(safe_error_message(res, "Signup failed"))

        # -------- OTP VERIFICATION --------
        if st.session_state.pending_email:
            st.divider()
            st.subheader("🔐 Verify OTP")

            otp_code = st.text_input("Enter OTP", key="otp_code")

            if st.button("Verify OTP"):
                res = requests.post(
                    f"{API_URL}/auth/verify-otp",
                    json={
                        "email": st.session_state.pending_email,
                        "code": otp_code
                    }
                )

                if res.status_code == 200:
                    st.session_state.pending_email = None
                    st.session_state.otp_verified = True
                    st.success("Account verified! You can now login.")
                else:
                    st.error(safe_error_message(res, "OTP verification failed"))

    else:
        st.success("✅ Logged in")

        if st.button("🚪 Logout"):
            st.session_state.token = None
            st.session_state.messages = []
            st.session_state.chat_titles = []
            st.rerun()

        st.divider()
        st.subheader("🕘 Chat History")
        for title in st.session_state.chat_titles:
            st.markdown(f"- {title}")

# ---------------- MAIN CHAT AREA ----------------
st.title("💬 Chat")

if not st.session_state.token:
    st.info("Please login to start chatting.")
    st.stop()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Ask your question...")

if prompt:
    if not st.session_state.messages:
        st.session_state.chat_titles.append(prompt[:30])

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    headers = {
        "Authorization": f"Bearer {st.session_state.token}",
        "Content-Type": "application/json"
    }

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            res = requests.post(
                f"{API_URL}/chat/",
                json={"question": prompt},
                headers=headers
            )

            if res.status_code == 200:
                answer = res.json()["answer"]
                st.markdown(answer)
                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )
            else:
                st.error("Something went wrong while chatting")
