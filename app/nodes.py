from datetime import datetime
from typing import Dict, Any
import json
import logging
import re

# -----------------------------
# 🧠 LOGGER SETUP
# -----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)


# import your tools
from .tools import (
    create_task,
    get_tasks,
    update_task,
    delete_task
)

# import db connection
from .config import get_db_connection, get_llm


# -----------------------------
# 🧠 1. ROUTER NODE
# -----------------------------
def router_node(state: Dict[str, Any]) -> Dict[str, Any]:
    llm = get_llm()

    now = datetime.now()
    user_input = state["user_input"]
    current_date = now.strftime("%Y-%m-%d")
    current_day = now.strftime("%A")  
    chat_history = state.get("chat_history", [])

    logger.info(f"[ROUTER] User input: {user_input}")
    logger.info(f"[ROUTER] Chat history: {chat_history}")

    # ✅ Format history properly
    formatted_history = "\n".join(
        [f"{m['role']}: {m['content']}" for m in chat_history[-3:]]
    )

    prompt = f"""
You are a strict JSON generator.

Return ONLY valid JSON. No markdown, no explanation.

--------------------------------------

INTENTS:
create_task | get_tasks | delete_task | update_task | chat

--------------------------------------

RULES:

- Use "get_tasks" if user asks about tasks/reminders
  (e.g. "what am I forgetting", "show my tasks")

- Use "create_task" ONLY if user clearly states a plan, obligation, or something to remember
- Questions must NEVER be tasks

- "task": full meaningful sentence (or null)

- "deadline":
- Convert to YYYY-MM-DD
  Use CURRENT DATE: {current_date}
  Today is: {current_day}
- Resolve relative dates using BOTH date and day
- Weekdays (e.g. Monday) must be the NEXT occurrence from today
Example:
If today is Saturday (2026-04-18), then Monday = 2026-04-20

- For update/delete:
  - "task_query" = reference to existing task
  - "task" = new content (only for update)
  - "task_number" if user says "task 1"

--------------------------------------

OUTPUT:

{{
  "intent": "create_task | get_tasks | delete_task | update_task | chat",
  "task": "string or null",
  "task_query": "string or null",
  "task_number": "integer or null",
  "deadline": "YYYY-MM-DD or null"
}}

--------------------------------------

INPUT:
{user_input}

HISTORY:
{formatted_history}
"""

    response = llm.invoke(prompt)
    raw = response.content

    logger.info(f"[ROUTER] Raw LLM response: {raw}")

    fallback = {
        "intent": "get_tasks",
        "task": None,
        "deadline": None,
        "task_query": None,
        "task_number": None
    }

    # ✅ Safe JSON extraction
    match = re.search(r"\{.*\}", raw, re.DOTALL)

    if match:
        try:
            parsed = json.loads(match.group())
            logger.info(f"[ROUTER] Parsed output: {parsed}")
        except Exception as e:
            logger.error(f"[ROUTER] JSON parse failed: {str(e)}")
            parsed = fallback
    else:
        logger.error("[ROUTER] No JSON found")
        parsed = fallback

    return {
        **state,
        "intent": parsed.get("intent"),
        "task": parsed.get("task"),
        "deadline": parsed.get("deadline"),
        "task_query": parsed.get("task_query"),
        "task_number": parsed.get("task_number"),
    }


# -----------------------------
# 🛠 2. TOOL NODE
# -----------------------------
def tool_node(state: Dict[str, Any]) -> Dict[str, Any]:
    conn = get_db_connection()

    intent = state.get("intent")
    task = state.get("task")
    deadline = state.get("deadline")
    task_query = state.get("task_query")
    task_number = state.get("task_number")

    logger.info(f"[TOOL] Intent: {intent}")
    logger.info(f"[TOOL] Task: {task}, Deadline: {deadline}")
    logger.info(f"[TOOL] Query: {task_query}, Number: {task_number}")

    result = None

    try:
        if intent == "create_task":
            result = create_task(conn, task, deadline)

        elif intent == "get_tasks":
            result = get_tasks(conn)

        elif intent in ["delete_task", "update_task"]:
            tasks_data = get_tasks(conn)
            tasks = tasks_data.get("tasks", [])

            selected_task = None

            # ✅ by number
            if task_number:
                if 0 < task_number <= len(tasks):
                    selected_task = tasks[task_number - 1]

            # ✅ by query
            elif task_query:
                matches = [
                    t for t in tasks
                    if task_query.lower() in t["task"].lower()
                ]

                if len(matches) == 1:
                    selected_task = matches[0]

                elif len(matches) > 1:
                    result = {
                        "status": "multiple_matches",
                        "matches": matches
                    }

            # ✅ execute
            if selected_task:
                if intent == "delete_task":
                    result = delete_task(conn, selected_task["id"])

                elif intent == "update_task":
                    result = update_task(conn, selected_task["id"], deadline)

            elif result is None:
                result = {
                    "status": "error",
                    "message": "Task not found"
                }

        elif intent == "chat":
            result = None

        else:
            result = "Unknown intent"

        logger.info(f"[TOOL] Result: {result}")

    except Exception as e:
        logger.error(f"[TOOL] Error: {str(e)}")
        result = f"Error: {str(e)}"

    return {
        **state,
        "tool_result": result
    }


# -----------------------------
# 💬 3. RESPONSE NODE
# -----------------------------
def response_node(state: Dict[str, Any]) -> Dict[str, Any]:
    llm = get_llm()

    user_input = state["user_input"]
    intent = state.get("intent")
    tool_result = state.get("tool_result")

    logger.info(f"[RESPONSE] Preparing response for intent: {intent}")
    logger.info(f"[RESPONSE] Tool result: {tool_result}")

    # ✅ handle multiple matches BEFORE LLM
    if isinstance(tool_result, dict) and tool_result.get("status") == "multiple_matches":
        matches = tool_result["matches"]

        formatted = "\n".join([
            f"{i+1}. {t['task']}" for i, t in enumerate(matches)
        ])

        return {
            **state,
            "response": f"I found multiple matching tasks:\n{formatted}\nWhich one do you mean?"
        }

    prompt = f"""
You are a smart AI Reminder Agent.

Respond naturally based on the action result.

Context:
User: "{user_input}"
Action: {intent}
Result: {tool_result}

Rules:

- If create_task:
  → Acknowledge clearly with task + deadline

- If get_tasks:
  → List tasks in numbered format
  → Highlight deadlines

- If delete_task:
  → Confirm deletion (mention task if possible)

- If update_task:
  → Confirm what changed

- If chat:
  → Keep it casual BUT steer toward tasks

- NEVER respond with generic lines like:
  "What can I remind you about today?"

- ALWAYS base response on actual data

Response:
"""

    response = llm.invoke(prompt)

    logger.info(f"[RESPONSE] Final response: {response.content}")

    return {
        **state,
        "response": response.content
    }