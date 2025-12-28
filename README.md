text
# 🤖 Multi‑Agent Web Generator

AI‑powered **multi‑agent system** that turns a simple idea into a complete **full‑stack web project** – with an orchestrated pipeline for **prompt enhancement, frontend generation, and backend generation**.

---

## 🚀 Overview

This project takes a plain English idea (for example: “SaaS dashboard for freelancers”) and uses multiple AI agents to:

- 🧠 Enhance and structure the idea into a clean project specification (JSON).
- 🎨 Generate a **Next.js 14 + Tailwind + shadcn/ui** frontend.
- 🛠 Generate an **Express.js + PostgreSQL (Neon)** backend.
- 🧩 Return ready‑to‑use source code that you can save, run, and extend.

---

## 🧱 Tech Stack

- **AI & Orchestration**
  - Python async agents
  - Google Gemini 2.5‑flash (via API)
- **Backend Orchestrator**
  - Python (FastAPI or similar)
  - `google-generativeai` SDK
  - Custom `agents/` modules
- **Generated Frontend**
  - Next.js 14 (App Router)
  - TypeScript
  - Tailwind CSS
  - shadcn/ui
- **Generated Backend**
  - Node.js
  - Express.js
  - PostgreSQL (Neon DB)

---

## 🏗️ Project Structure

```multiagent-ai/
├─ backend/
│ ├─ app/
│ │ ├─ main.py # API entrypoint
│ │ ├─ master_agent.py # Orchestrates all AI agents
│ │ └─ agents/
│ │ ├─ prompt_enhancer.py
│ │ ├─ frontend_generator.py
│ │ └─ backend_generator.py
│ ├─ .env.example # Example env vars (no secrets)
│ └─ requirements.txt
├─ .gitignore
├─ README.md
└─ ...
```
text

---

## ⚙️ How It Works

1. **User Idea → JSON Spec**
   - User sends a short idea string (e.g. “multi‑tenant billing dashboard”).
   - `prompt_enhancer.py` calls Gemini and returns a structured JSON:
     - `project_name`
     - `enhanced_prompt`
     - `features`
     - `pages`
     - `components`
     - `tech_stack`

2. **JSON Spec → Frontend Code**
   - `frontend_generator.py` uses the enhanced JSON to generate:
     - `app/page.tsx`
     - `app/layout.tsx`
     - `package.json`
   - Code is tailored for **Next.js 14 + Tailwind + shadcn/ui**.

3. **JSON Spec → Backend Code**
   - `backend_generator.py` uses the same JSON to generate:
     - `server.js`
     - `package.json`
   - Uses **Express.js + PostgreSQL (Neon)** as the base.

4. **Master Orchestrator**
   - `master_agent.py` coordinates everything:
     - Receives the user idea.
     - Calls prompt enhancer → frontend generator → backend generator.
     - Returns a combined response with all generated code.

---

## 🧪 Example Orchestrator Endpoint

app/master_agent.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from agents.prompt_enhancer import enhance_prompt
from agents.frontend_generator import generate_frontend
from agents.backend_generator import generate_backend

router = APIRouter()

class GenerateRequest(BaseModel):
idea: str

class GenerateResponse(BaseModel):
project_name: str
enhanced_prompt: dict
frontend_code: dict
backend_code: dict

@router.post("/generate", response_model=GenerateResponse)
async def generate_project(payload: GenerateRequest):
"""
End‑to‑end pipeline:
1. Enhance raw idea.
2. Generate frontend.
3. Generate backend.
4. Return a complete project bundle.
"""

text
# 1) Enhance the prompt
enhanced = await enhance_prompt(payload.idea)
if not enhanced.get("success"):
    raise HTTPException(
        status_code=500,
        detail=f"Prompt enhancement failed: {enhanced.get('details')}"
    )

enhanced_data = enhanced["enhanced_prompt"]
project_name = enhanced_data.get("project_name", "generated-project")

# 2) Generate frontend
frontend = await generate_frontend(enhanced_data)
if not frontend.get("success"):
    raise HTTPException(
        status_code=500,
        detail=f"Frontend generation failed: {frontend.get('details')}"
    )

# 3) Generate backend
backend = await generate_backend(enhanced_data)
if not backend.get("success"):
    raise HTTPException(
        status_code=500,
        detail=f"Backend generation failed: {backend.get('details')}"
    )

return GenerateResponse(
    project_name=project_name,
    enhanced_prompt=enhanced_data,
    frontend_code=frontend["frontend_code"],
    backend_code=backend["backend_code"],
)
text

---

## 🔑 Environment Setup

1. **Create env file from example**

cd backend
cp .env.example .env # or create manually

text

2. **Fill your secrets in `.env`**

GEMINI_API_KEY=your_gemini_api_key_here
NEON_DB_URL=your_neon_postgres_url_here

text

> `.env` is ignored by Git. Only `.env.example` is committed.

---

## ▶️ Running the Backend

cd backend

(Optional) Create and activate virtualenv
python -m venv venv
venv\Scripts\activate # Windows

source venv/bin/activate # macOS / Linux
Install dependencies
pip install -r requirements.txt

Run the API server (example)
uvicorn app.main:app --reload --port 8000

text

You can now send a `POST` request to:

POST http://localhost:8001/generate
Content-Type: application/json

{
"idea": "AI-powered SaaS dashboard for managing client invoices"
}

text

---

## 🧠 Agents Summary

| Agent              | Responsibility                                      |
|--------------------|-----------------------------------------------------|
| Prompt Enhancer    | Turn user idea into rich, structured JSON spec      |
| Frontend Generator | Produce Next.js 14 + Tailwind + shadcn/ui frontend |
| Backend Generator  | Produce Express.js + PostgreSQL backend boilerplate |
| Master Agent       | Orchestrate the full pipeline                       |

---

## 🛡️ Security Notes

- Real API keys and DB URLs live **only in `.env`** (never committed).
- `.env.example` shows the required variables with placeholder values.
- If a secret is ever pushed accidentally, rotate/regenerate it immediately.

---

## 🤝 Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/awesome-idea`
3. Commit changes: `git commit -m "Add awesome feature"`
4. Push branch: `git push origin feature/awesome-idea`
5. Open a Pull Request.

---

## 📬 Author

- **Name:** Dhruv Gaur  
- **GitHub:** [@Dhruvgaur-git](https://github.com/Dhruvgaur-git)  

If you use this to generate something cool, feel free to share it! 🚀
