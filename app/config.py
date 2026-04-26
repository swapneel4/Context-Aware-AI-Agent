import os
import sqlite3
from functools import lru_cache
from langchain_groq import ChatGroq
from dotenv import load_dotenv
load_dotenv()

# -----------------------------
# 🗄️ DATABASE CONFIG
# -----------------------------
DB_PATH = "tasks.db"


def get_db_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            deadline TEXT,
            created_at DATETIME,
            delete_after DATETIME
        )
        """
    )

    conn.commit()
    conn.close()


# -----------------------------
# 🤖 LLM CONFIG (GROQ)
# -----------------------------
@lru_cache
def get_llm():
    """
    Cached LLM instance (important for performance)
    """

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not set in environment")

    llm = ChatGroq(
        groq_api_key=api_key,
        model="llama-3.1-8b-instant",
        temperature=0,  # low = more predictable
    )

    return llm