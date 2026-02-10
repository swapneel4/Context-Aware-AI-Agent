import streamlit as st
import requests
from datetime import datetime

# =====================================================
# ⚙️ CONFIG
# =====================================================

API_URL = "http://localhost:8000/chat"  # FastAPI endpoint

st.set_page_config(
    page_title="Context-Aware Reminder Agent",
    page_icon="🧠",
    layout="wide"
)

# =====================================================
# 🧠 SESSION STATE
# =====================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

# =====================================================
# 🎨 UI HEADER
# =====================================================

st.title("🧠 Context-Aware Reminder & Follow-Up Agent")
st.caption(
    "GenAI Prototype — MCP + LLM Tool Selection + Context Memory"
)

# Sidebar (future MCP dashboard)
with st.sidebar:
    st.header("📌 Agent Status")
    st.write("Model: llama-3.1-8b-instant")
    st.write("Context Mode: MCP Enabled")
    st.divider()
    st.info(
        "This agent remembers commitments and suggests reminders automatically."
    )

# =====================================================
# 💬 CHAT DISPLAY
# =====================================================

chat_container = st.container()

with chat_container:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.chat_message("user").write(msg["content"])
        else:
            st.chat_message("assistant").write(msg["content"])

# =====================================================
# ⌨️ USER INPUT
# =====================================================

user_input = st.chat_input("Type your message...")

if user_input:
    # Add user message to session
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    st.chat_message("user").write(user_input)

    # =================================================
    # 🚀 CALL BACKEND AGENT (FastAPI)
    # =================================================
    try:
        payload = {
            "message": user_input,
            "timestamp": datetime.now().isoformat()
        }

        response = requests.post(API_URL, json=payload)

        if response.status_code == 200:
            data = response.json()
            agent_reply = data.get("response", "No response from agent.")

        else:
            agent_reply = f"⚠️ Backend error: {response.status_code}"

    except Exception as e:
        agent_reply = f"❌ Connection error: {str(e)}"

    # =================================================
    # 🤖 SHOW AGENT RESPONSE
    # =================================================
    st.session_state.messages.append(
        {"role": "assistant", "content": agent_reply}
    )

    st.chat_message("assistant").write(agent_reply)
