from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import os
import requests

from groq import Groq
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MCP_URL = "http://localhost:8000"

# =====================================================
# MODELS
# =====================================================

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

# =====================================================
# MCP HELPERS
# =====================================================

def fetch_mcp_context():

    try:
        r = requests.get(f"{MCP_URL}/resources/context://tasks")
        return r.json()
    except:
        return {"pending_tasks": []}


def call_mcp_tool(tool_name, args):

    r = requests.post(
        f"{MCP_URL}/tools/{tool_name}",
        json=args
    )

    return r.json()

# =====================================================
# GROQ AGENT WITH TOOL CALLING
# =====================================================

def groq_agent(user_message, context):

    system_prompt = f"""
You are a Context-Aware Reminder Agent.

MCP Context:
{context}

If user mentions deadlines or commitments,
respond using JSON:

{{
  "tool": "save_task",
  "args": {{"task":"...", "due_date":"..."}}
}}

Otherwise reply normally.
"""

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
    )

    return completion.choices[0].message.content

# =====================================================
# CHAT ENDPOINT
# =====================================================

@app.post("/chat", response_model=ChatResponse)
async def chat(data: ChatRequest):

    context = fetch_mcp_context()

    llm_output = groq_agent(data.message, context)

    # =================================================
    # TRY TOOL CALL PARSING
    # =================================================

    try:
        import json
        parsed = json.loads(llm_output)

        if "tool" in parsed:

            tool_result = call_mcp_tool(
                parsed["tool"],
                parsed["args"]
            )

            return ChatResponse(
                response=f"✅ Task saved successfully.\n{tool_result}"
            )

    except:
        pass

    return ChatResponse(response=llm_output)

@app.get("/")
async def root():
    return {"status": "Agent running"}

if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=8001, reload=True)
