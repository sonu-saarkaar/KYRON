# 🚀 KYRON - AI Digital Execution & Autonomous Engineering Agent

**Modern React Frontend + FastAPI Backend with Hermes Agent Intelligence & OpenHands CodeAgent Integration**

---

## ✅ Status: Production-Ready & Tested (100% Green)

Complete end-to-end integration including AI execution, automated document processing, conversational skills/memory, and autonomous software engineering.

---

## 🎯 Quick Start

### Option 1: Run Everything (Easiest)

```powershell
.\RUN_PROJECT.ps1
```

### Option 2: Run Separately

**Backend:**
```powershell
cd backend
python main.py
```

**Frontend:**
```powershell
cd frontend-react
npm install
npm run dev
```

---

## 📋 URLs & Endpoints

- **Backend API**: `http://127.0.0.1:8000`
- **Interactive Swagger Docs**: `http://127.0.0.1:8000/docs`
- **Frontend Dashboard**: `http://localhost:5173`

---

## 🧠 Advanced Agent Architectures Integrated

### 1. Hermes Agent Intelligence (Selective Port)
- **Persistent Memory Manager (`/api/hermes/memory`)**: Structured memory cards with authoritative `<memory-context>` system fencing and prompt injection sanitization.
- **Skills Engine (`/api/hermes/skills`)**: Reusable skills-from-experience, canonical markdown definitions, dynamic trigger phrase matching, and automatic `<skills-context>` prompt injection.
- **Cron Task Scheduler (`/api/hermes/cron`)**: Automated recurring AI jobs powered by `croniter`, background event loop execution, and immediate trigger dispatch.
- **NVIDIA NIM LLM Client**: Strict copy-on-write `ToolMessage` schema sanitization stripping disallowed parameters for zero-error tool calling on NVIDIA NIM.

### 2. OpenHands CodeAgent (Autonomous Software Repair)
- **ReAct Execution Loop**: Iterative *Thought -> Action -> Observation -> Self-Correction* loop for diagnosing and repairing bugs autonomously.
- **Dual-Mode Sandboxing**:
  - **Docker Isolation**: Containerized execution with mounted workspace and network isolation when Docker daemon is active.
  - **Local Sandbox Fallback**: Process sandbox with directory traversal blocking (`resolve_path`), execution timeouts, and environment variable sanitization.
- **Automated Error-to-Fix Retry**: Automated test-runner integration (`pytest` / command-based), failure trace analysis, targeted patch generation, and re-verification until 100% passing.
- **REST Endpoints (`/api/kyron/code-agent`)**:
  - `POST /api/kyron/code-agent/run` — Run autonomous repair loop on any repo/file.
  - `GET /api/kyron/code-agent/status` — Inspect sandbox mode, Docker availability, and active LLM provider.

---

## 📁 Project Structure

```
KYRON/
├── backend/
│   ├── core/                  Configuration & settings (NVIDIA NIM, MongoDB)
│   ├── routes/
│   │   ├── auth.py            Authentication routes
│   │   ├── chat.py            Conversational chat API with Hermes context routing
│   │   ├── hermes.py          Skills, Memory & Cron REST endpoints
│   │   └── code_agent.py      CodeAgent execution & sandbox REST endpoints
│   ├── services/
│   │   ├── llm_client.py      NVIDIA NIM / OpenAI client with ToolMessage sanitizer
│   │   ├── memory_manager.py  Hermes Persistent Memory Card Manager
│   │   ├── skills_engine.py   Hermes Skills-from-Experience Engine
│   │   ├── scheduler.py       Hermes Cron Scheduler & Runner
│   │   └── code_agent.py      OpenHands CodeAgent & SandboxEnvironment
│   ├── tests/
│   │   ├── test_hermes_integration.py  Hermes test suite (100% Green)
│   │   └── test_code_agent.py          CodeAgent & BookMyGaadi bug repair (100% Green)
│   ├── main.py                FastAPI application entrypoint & lifecycles
│   └── requirements.txt       Python dependencies
├── frontend-react/            React 18 Dashboard UI
└── RUN_PROJECT.ps1            One-click startup script
```

---

## 🧪 Automated Test Suites

Run integration test suites:

```powershell
# Hermes Integration Suite (Skills, Memory, Cron, NIM Sanitization, Chat)
python backend/tests/test_hermes_integration.py

# OpenHands CodeAgent Suite (Sandboxing, BookMyGaadi Bug Repair, REST API)
python backend/tests/test_code_agent.py
```

---

**Built with ❤️ using React, FastAPI, Hermes Agent, and OpenHands**
