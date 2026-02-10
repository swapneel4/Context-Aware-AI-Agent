from mcp.server.fastmcp import FastMCP
from datetime import datetime
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# =====================================================
# ⚙️ LOAD ENV
# =====================================================

load_dotenv()

# =====================================================
# 🧠 CREATE FAST MCP SERVER
# =====================================================

mcp = FastMCP("ContextAwareReminderAgent")

# =====================================================
# 🗄️ MONGODB CONNECTION
# =====================================================

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("MONGO_URI not found in .env")

mongo_client = MongoClient(MONGO_URI)
db = mongo_client["reminder_agent_db"]
memory_collection = db["memory"]

# =====================================================
# 🧰 TOOL: SAVE TASK
# =====================================================

@mcp.tool()
def save_task(task: str, due_date: str) -> dict:
    """
    Save a reminder task into MongoDB.
    """

    memory_collection.insert_one({
        "task": task,
        "due_date": due_date,
        "created_at": datetime.now().isoformat()
    })

    return {"status": "saved", "task": task}

# =====================================================
# 🧰 TOOL: GET TASKS
# =====================================================

@mcp.tool()
def get_tasks() -> list:
    """
    Retrieve all pending tasks.
    """

    return list(memory_collection.find({}, {"_id": 0}))

# =====================================================
# 📦 RESOURCE: CONTEXT PROVIDER
# =====================================================

@mcp.resource("context://tasks")
def context_tasks():
    """
    MCP context resource for pending tasks.
    """

    tasks = list(memory_collection.find({}, {"_id": 0}))

    return {
        "current_time": datetime.now().isoformat(),
        "pending_tasks": tasks
    }

# =====================================================
# ▶️ RUN MCP SERVER (IMPORTANT FIX)
# =====================================================

if __name__ == "__main__":
    mcp.run(
        transport="streamable-http"
    )

