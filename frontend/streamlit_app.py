import streamlit as st
import requests

#CONFIG
API_URL = "http://127.0.0.1:8000"
ADMIN_EMAIL = "skywave2720@gmail.com"

# PAGE CONFIG
st.set_page_config(
    page_title="RAG Chatbot",
    page_icon="🤖",
    layout="wide"
)

#SESSION STATE
if "token" not in st.session_state:
    st.session_state.token = None
if "role" not in st.session_state:
    st.session_state.role = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None
if "pending_email" not in st.session_state:
    st.session_state.pending_email = None

#HELPERS
def auth_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}

def safe_error_message(res, default="Something went wrong"):
    try:
        return res.json().get("detail", default)
    except Exception:
        return f"{default} (status {res.status_code})"

# SIDEBAR
with st.sidebar:
    st.title("🤖 RAG Chatbot")

    if not st.session_state.token:
        tab1, tab2, tab3 = st.tabs(["User Login", "Admin Login", "Sign Up"])

        #USER LOGIN
        with tab1:
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")

            if st.button("Login as User"):
                with st.spinner("Logging in..."):
                    res = requests.post(
                        f"{API_URL}/auth/login",
                        json={"email": email, "password": password},
                        timeout=5
                    )

                if res.status_code == 200:
                    st.session_state.token = res.json()["access_token"]
                    st.session_state.role = "user"
                    st.rerun()
                else:
                    st.error(safe_error_message(res, "Login failed"))

        #ADMIN LOGIN
        with tab2:
            st.info(f"Admin Email: {ADMIN_EMAIL}")
            admin_password = st.text_input("Admin Password", type="password")

            if st.button("Login as Admin"):
                with st.spinner("Logging in..."):
                    res = requests.post(
                        f"{API_URL}/auth/login",
                        json={"email": ADMIN_EMAIL, "password": admin_password},
                        timeout=5
                    )

                if res.status_code == 200:
                    st.session_state.token = res.json()["access_token"]
                    st.session_state.role = "admin"
                    st.rerun()
                else:
                    st.error("Invalid admin credentials")

        #SIGN UP
        with tab3:
            signup_email = st.text_input("Signup Email")
            signup_password = st.text_input("Signup Password", type="password")

            if st.button("Sign Up"):
                with st.spinner("Signing up..."):
                    res = requests.post(
                        f"{API_URL}/auth/register",
                        json={"email": signup_email, "password": signup_password},
                        timeout=5
                    )

                if res.status_code == 200:
                    st.session_state.pending_email = signup_email
                    st.success("OTP sent to your email")
                else:
                    st.error(safe_error_message(res, "Signup failed"))

        #OTP
        if st.session_state.pending_email:
            st.divider()
            otp = st.text_input("Enter OTP")

            if st.button("Verify OTP"):
                with st.spinner("Verifying OTP..."):
                    res = requests.post(
                        f"{API_URL}/auth/verify-otp",
                        json={"email": st.session_state.pending_email, "code": otp},
                        timeout=5
                    )

                if res.status_code == 200:
                    st.session_state.pending_email = None
                    st.success("Account verified! Please login.")
                else:
                    st.error("OTP verification failed")

    else:
        st.success(f"Logged in as {st.session_state.role.upper()}")

        #NEW CHAT
        if st.button("➕ New Chat"):
            requests.post(
                f"{API_URL}/onboarding/reset",
                headers=auth_headers()
            )
            st.session_state.messages = []
            st.session_state.conversation_id = None
            st.rerun()

        #CHAT HISTORY
        if st.session_state.role == "user":
            st.divider()
            st.subheader("💬 Chat History")

            res = requests.get(
                f"{API_URL}/chat/conversations",
                headers=auth_headers(),
                timeout=5
            )

            if res.status_code == 200:
                for convo in res.json():
                    if st.button(convo["title"], key=f"c{convo['id']}"):
                        st.session_state.conversation_id = convo["id"]

                        msg_res = requests.get(
                            f"{API_URL}/chat/conversations/{convo['id']}",
                            headers=auth_headers(),
                            timeout=5
                        )

                        if msg_res.status_code == 200:
                            st.session_state.messages = [
                                {"role": m["role"], "content": m["content"]}
                                for m in msg_res.json()
                            ]
                        st.rerun()

        #LOGOUT
        if st.button("🚪 Logout"):
            st.session_state.token = None
            st.session_state.role = None
            st.session_state.messages = []
            st.session_state.conversation_id = None
            st.rerun()

#ADMIN DASHBOARD
# if st.session_state.token and st.session_state.role == "admin":
#     st.title("🪑 Admin Seating Dashboard")
#
#     res = requests.get(
#         f"{API_URL}/admin/seating/status",
#         headers=auth_headers(),
#         timeout=5
#     )
#
#     if res.status_code != 200:
#         st.error("Failed to load seating status")
#         st.stop()
#
#     for tech, seats in res.json().items():
#         st.subheader(tech.upper())
#         st.write(seats)
#
#     st.stop()
# ================= ADMIN DASHBOARD =================
# if st.session_state.token and st.session_state.role == "admin":
#     st.title("🪑 Admin Seating Dashboard")
#
#     headers = {"Authorization": f"Bearer {st.session_state.token}"}
#     res = requests.get(f"{API_URL}/admin/seating/status", headers=headers)
#
#     if res.status_code != 200:
#         st.error("Failed to load seating status")
#         st.stop()
#
#     seating_data = res.json()
#
#     # LEGEND
#     st.markdown("### Legend")
#     st.markdown("⬜ Empty seat &nbsp;&nbsp; ❌ Occupied seat")
#     st.divider()
#
#     for tech, info in seating_data.items():
#         rows = info["rows"]
#         cols = info["columns"]
#         occupied = {(s["row"], s["col"]) for s in info["occupied"]}
#
#         st.subheader(f"🪑 {tech.upper()}")
#
#         # Draw matrix
#         for r in range(rows):
#             row_display = ""
#             for c in range(cols):
#                 if (r, c) in occupied:
#                     row_display += "❌ "
#                 else:
#                     row_display += "⬜ "
#             st.markdown(row_display)
#
#         st.divider()
#
#     st.stop()
# ================= ADMIN DASHBOARD =================
if st.session_state.token and st.session_state.role == "admin":
    st.title("🪑 Admin Seating Dashboard")

    headers = {
        "Authorization": f"Bearer {st.session_state.token}"
    }

    # 🔹 FETCH SEATING DATA FROM BACKEND
    res = requests.get(
        f"{API_URL}/admin/seating/status",
        headers=headers,
        timeout=5
    )

    if res.status_code != 200:
        st.error("Failed to load seating data")
        st.stop()

    seating_data = res.json()  # ✅ THIS WAS MISSING

    # ---------- LEGEND ----------
    st.markdown("### Legend")
    st.markdown("⬜ Empty seat &nbsp;&nbsp; ❌ Occupied seat")
    st.divider()

    # ---------- MATRIX RENDER ----------
    for tech, seats in seating_data.items():
        st.subheader(tech.upper())

        total_seats = len(seats)
        cols = 5   # admin-configured column size
        rows = (total_seats + cols - 1) // cols

        index = 0
        for _ in range(rows):
            row_display = ""
            for _ in range(cols):
                if index < total_seats:
                    row_display += "❌ " if seats[index] == "X" else "⬜ "
                else:
                    row_display += "⬜ "
                index += 1

            st.markdown(row_display)

        st.divider()

    st.stop()

#USER CHAT
st.title("💬 "
         ""
         ""
         "Chat")

if not st.session_state.token:
    st.info("Please login to start chatting.")
    st.stop()

#DISPLAY CHAT
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

#CHAT INPUT
prompt = st.chat_input("Type your message...")

if prompt:
    headers = {
        "Authorization": f"Bearer {st.session_state.token}",
        "Content-Type": "application/json"
    }

    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    payload = {
        "question": prompt,
        "conversation_id": st.session_state.conversation_id
    }

    res = requests.post(
        f"{API_URL}/chat/chat",
        json=payload,
        headers=headers,
        timeout=10
    )

    if res.status_code != 200:
        st.error("Chat request failed")
        st.stop()

    data = res.json()

    #SAVE CONVERSATION ID
    if "conversation_id" in data:
        st.session_state.conversation_id = data["conversation_id"]

    # HANDLE RESPONSE TYPES
    if data["type"] == "chat":
        reply = data["answer"]
    elif data["type"] == "handoff":
        reply = f"{data['answer']}\n\n_{data['followup']}_"
    elif data["type"] == "onboarding":
        reply = data["message"]
    else:
        reply = "Unknown response type"

    st.session_state.messages.append(
        {"role": "assistant", "content": reply}
    )
    st.rerun()
