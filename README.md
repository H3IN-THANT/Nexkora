# DevAssist

AI-powered developer productivity assistant.

DevAssist is a full-stack AI application designed to help developers with code explanation, code generation, debugging, documentation, knowledge Q&A, and document-based question answering using Retrieval-Augmented Generation (RAG).

## Tech Stack

### Frontend

* Next.js
* TypeScript
* Tailwind CSS

### Backend

* Python
* FastAPI

### AI

* OpenAI API

### RAG

* ChromaDB

### Version Control

* Git
* GitHub

## Project Structure

```text
DevAssist/
├── frontend/
├── backend/
├── docs/
├── .gitignore
└── README.md
```

## Development

The frontend and backend are developed as separate applications.

### Frontend

```bash
cd frontend
npm run dev
```

Frontend:

```text
http://localhost:3000
```

### Backend

```bash
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

Health check:

```text
http://127.0.0.1:8000/health
```

## Current Status

Milestone 1 — Project foundation and development environment.

AI functionality will be added in later milestones.
