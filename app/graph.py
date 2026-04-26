from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional, List, Dict, Any

from .nodes import router_node, tool_node, response_node


# -----------------------------
# 🧠 STATE DEFINITION
# -----------------------------
class AgentState(TypedDict):
    user_input: str
    chat_history: Optional[List[Dict[str, str]]]

    intent: Optional[str]
    task: Optional[str]
    deadline: Optional[str]
    task_id: Optional[int]

    tool_result: Optional[Any]
    response: Optional[str]
    task_query: Optional[str]
    task_number: Optional[int]


# -----------------------------
# ⚙️ BUILD GRAPH
# -----------------------------
def build_graph():
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("router", router_node)
    graph.add_node("tool", tool_node)
    graph.add_node("response", response_node)

    # Flow (simple + linear)
    graph.set_entry_point("router")

    graph.add_edge("router", "tool")
    graph.add_edge("tool", "response")
    graph.add_edge("response", END)

    return graph.compile()


# -----------------------------
# 🚀 INVOKE GRAPH
# -----------------------------
def run_agent(user_input: str, chat_history=None):
    app = build_graph()

    state = {
        "user_input": user_input,
        "chat_history": chat_history or [],
        "intent": None,
        "task": None,
        "deadline": None,
        "task_id": None,
        "tool_result": None,
        "response": None,
    }

    result = app.invoke(state)

    return result["response"]