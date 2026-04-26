import streamlit as st
import requests

API_URL = "http://localhost:8000/chat"

# -----------------------------
# 🎨 PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="AI Reminder Agent",
    page_icon="🧠",
    layout="centered"
)

# -----------------------------
# 🎨 MODERN CHAT UI CSS
# -----------------------------
st.markdown("""
<style>
.stApp {
    background-color: #091413;
    color: #ffffff;
}

h1 {
    text-align: center;
    color: #b0e4cc;
    margin-bottom: 20px;
}

/* Chat container */
.chat-container {
    max-width: 750px;
    margin: auto;
    padding-bottom: 120px;
}

/* Message rows */
.message-row {
    display: flex;
    margin: 8px 0;
}

.message-row.user {
    justify-content: flex-end;
}

.message-row.assistant {
    justify-content: flex-start;
}

/* Bubbles */
.bubble {
    padding: 12px 16px;
    border-radius: 16px;
    max-width: 65%;
    font-size: 15px;
    line-height: 1.4;
    word-wrap: break-word;
}

.user .bubble {
    background-color: #408a71;
    color: #ffffff;
    border-bottom-right-radius: 4px;
}

.assistant .bubble {
    background-color: #285a48;
    color: #b0e4cc;
    border-bottom-left-radius: 4px;
}

/* Fixed input */
.stChatInput {
    position: fixed;
    bottom: 20px;
    left: 0;
    width: 100%;
    padding: 0 20px;
    background-color: #091413;
}

.stChatInput > div {
    max-width: 900px;
    margin: auto;
    border: 1px solid #285a48;
    border-radius: 12px;
    background-color: #091413;
}

textarea {
    background-color: #091413 !important;
    color: #ffffff !important;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# 🧠 SESSION STATE
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------
# 💬 RENDER CHAT
# -----------------------------
def render_chat():
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)

    for msg in st.session_state.messages:
        role = msg["role"]
        st.markdown(f"""
        <div class="message-row {role}">
            <div class="bubble">{msg["content"]}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# 🚀 UI
# -----------------------------
st.title("🧠 AI Reminder Agent")

render_chat()

# -----------------------------
# ⌨️ INPUT (ChatGPT style)
# -----------------------------
if prompt := st.chat_input("Type your message..."):

    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    # Prepare chat history
    chat_history = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ]

    # Call backend
    try:
        res = requests.post(
            API_URL,
            json={
                "message": prompt,
                "chat_history": chat_history
            }
        )
        data = res.json()
        bot_reply = data.get("response", "Something went wrong")

    except Exception:
        bot_reply = "Backend not reachable"

    # Add assistant response
    st.session_state.messages.append({
        "role": "assistant",
        "content": bot_reply
    })

    st.rerun()