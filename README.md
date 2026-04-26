# 🧠 Context-Aware Reminder & Follow-Up Agent

An intelligent AI-powered reminder system that understands natural language, manages tasks, and provides contextual responses using LLMs and agent-based architecture.

---

## 🚀 Features

- 🧠 Context-aware conversation using LLM (LLaMA 3 via Groq)
- 🔁 Graph-based AI agent workflow (LangGraph)
- 📌 Create, update, delete, and fetch reminders
- 📅 Smart date understanding (e.g., "next Monday", "tomorrow")
- 💬 ChatGPT-like UI using Streamlit
- 🗄️ SQLite database for task storage
- ⚡ FastAPI backend for real-time interaction
- 🧹 Automatic cleanup of expired tasks

---

## 🏗️ Architecture

Frontend (Streamlit UI)  
⬇  
FastAPI Backend (/chat API)  
⬇  
LangGraph Agent (Router → Tool → Response)  
⬇  
LLM (Groq - LLaMA 3)  
⬇  
SQLite Database  

---

## 🛠️ Tech Stack

- Python
- FastAPI
- Streamlit
- LangGraph
- LangChain
- Groq (LLaMA 3)
- SQLite

---

## 📁 Project Structure
├── app/
│ ├── main.py # FastAPI backend
│ ├── graph.py # Agent workflow
│ ├── nodes.py # AI decision logic
│ ├── tools.py # Task operations
│ ├── config.py # DB + LLM setup
│
├── streamlitapp.py # Frontend UI
├── requirements.txt
├── README.md


---

## ▶️ How to Run

### 1️⃣ Install dependencies

```bash
pip install -r requirements.txt
GROQ_API_KEY=your_api_key_here
uvicorn app.main:app --reload
streamlit run streamlitapp.py
