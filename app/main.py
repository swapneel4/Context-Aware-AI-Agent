import os
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Optional
from .config import init_db, get_db_connection
from .graph import run_agent


# -----------------------------
# 🚀 APP INIT
# -----------------------------
app = FastAPI()


# -----------------------------
# 🧹 CLEANUP LOGIC (STARTUP)
# -----------------------------
def cleanup_expired_tasks():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM tasks
        WHERE delete_after <= CURRENT_TIMESTAMP
        """
    )

    conn.commit()
    conn.close()


@app.on_event("startup")
def startup_event():
    init_db()

    # Run cleanup ONLY once per session
    if not os.path.exists("cleanup_done.flag"):
        cleanup_expired_tasks()
        open("cleanup_done.flag", "w").close()

    print("✅ App started")


# -----------------------------
# 📦 REQUEST SCHEMA
# -----------------------------
class ChatRequest(BaseModel):
    message: str
    chat_history: Optional[List[Dict[str, str]]] = []


# -----------------------------
# 💬 CHAT ROUTE
# -----------------------------
@app.post("/chat")
def chat(req: ChatRequest):
    try:
        MAX_HISTORY = 4
        response = run_agent(
            user_input=req.message,
            chat_history=req.chat_history[-MAX_HISTORY:]
        )

        return {
            "status": "success",
            "response": response
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


# -----------------------------
# 🧪 HEALTH CHECK
# -----------------------------
@app.get("/")
def root():
    return {"message": "AI Reminder Agent running 🚀"}