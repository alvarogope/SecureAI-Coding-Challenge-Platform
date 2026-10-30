# SecureAI Coding Challenge Generator
 
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=flat&logo=react&logoColor=61DAFB)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=flat&logo=openai&logoColor=white)
![Clerk](https://img.shields.io/badge/Clerk-6C47FF?style=flat&logo=clerk&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat&logo=sqlite&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
 
A full-stack AI-powered coding challenge platform. Users log in, select a difficulty, and receive a dynamically generated multiple-choice coding challenge — no static database required. Every challenge is unique, produced in real time by an OpenAI pipeline. User sessions, challenge history, and daily quotas are all persisted and tracked.
 
---
 
## Features
 
- **AI-Generated Challenges** — GPT produces unique coding questions on every request, eliminating the need for a static challenge database
- **Clerk Authentication** — Full sign-in/sign-up flow with session management split across frontend and backend
- **Challenge History** — Each user's past attempts, answers, and results are stored and displayed in a History panel
- **Daily Quota System** — Tracks and limits the number of challenges per user per day (resets every 24 hours)
- **Route Protection** — Authentication enforced at a granular level on the frontend; protected API endpoints on the backend
- **Secure by Design** — API keys stored in `.env` files excluded from version control; CORS middleware restricts requests to the frontend domain only

---

## Preview

### Sign In
![Sign In](assets/sign-in.png)

### Generate a Challenge
![Challenge Generator](assets/preview.png)

### Challenge History
![History](assets/history.png)

---

## Architecture
 
```
┌─────────────────────┐         ┌──────────────────────┐
│   React (Vite)      │ ──────▶ │   FastAPI (Python)   │
│   Plain CSS         │         │   Uvicorn server     │
│   Clerk React SDK   │         │   SQLAlchemy ORM     │
└─────────────────────┘         └──────────┬───────────┘
                                            │
                          ┌─────────────────┼──────────────────┐
                          ▼                 ▼                  ▼
                    OpenAI API         Clerk Webhooks       SQLite DB
                  (challenge gen)    (user session sync)  (persistence)
```

---

## Project Structure
 
```
AI-Coding-Challenge-Platform/
├── backend/
│   ├── server.py              # Entry point - starts Uvicorn
│   ├── pyproject.toml         # Python dependencies
│   └── src/
│       ├── app.py             # FastAPI app - CORS, routers
│       ├── ai_generator.py    # OpenAI integration - challenge generation
│       ├── utils.py           # Clerk request authentication helper
│       ├── database/
│       │   ├── models.py      # SQLAlchemy ORM models + DB setup
│       │   └── db.py          # DB query functions
│       └── routes/
│           ├── challenge.py   # /api/generate-challenge, /api/my-history, /api/quota
│           └── webhook.py     # /webhooks/clerk - user creation sync
├── frontend/
│   └── src/
│       ├── main.jsx           # App entry - ClerkProvider wrapper
│       ├── App.jsx            # Root component and routing
│       ├── app.css            # Global styles
│       ├── auth/
│       │   ├── ClerkProviderWithRoutes.jsx  # Route protection wrapper
│       │   └── AuthenticationPage.jsx       # Sign-in / sign-up UI
│       ├── challenge/
│       │   ├── ChallengeGenerator.jsx       # Main challenge interface
│       │   └── MCQChallenge.jsx             # Multiple choice question display
│       ├── history/
│       │   └── HistoryPanel.jsx             # User history view
│       ├── layout/
│       │   └── Layout.jsx                   # Navbar and page shell
│       └── utils/
│           └── api.js                       # Authenticated fetch helper
└── README.md
```

---

## Getting Started
 
### Prerequisites
 
- Python 3.14+
- Node.js 18+
- An [OpenAI API key](https://platform.openai.com/)
- A [Clerk](https://clerk.com/) account
 
### Backend Setup
 
```bash
cd backend
pip install .
```
 
Create a `.env` file inside `backend/`:
 
```
OPENAI_API_KEY=your_openai_api_key
CLERK_SECRET_KEY=your_clerk_secret_key
CLERK_WEBHOOK_SECRET=your_clerk_webhook_secret
```
 
Start the server:
 
```bash
python server.py
```
 
API available at `http://localhost:8000`
 
### Frontend Setup
 
```bash
cd frontend
npm install
```
 
Create a `.env` file inside `frontend/`:
 
```
VITE_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key
```
 
Start the dev server:
 
```bash
npm run dev
```
 
App available at `http://localhost:5173`

---

## API Endpoints
 
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/generate-challenge` | Generate a new AI challenge `{"difficulty": "easy\|medium\|hard"}` |
| GET | `/api/my-history` | Get the authenticated user's challenge history |
| GET | `/api/quota` | Get the authenticated user's remaining daily quota |
| POST | `/webhooks/clerk` | Clerk webhook - creates quota record on user sign-up |
 
> All `/api/*` endpoints require a valid Clerk session token.

---

## Tech Stack
 
| Layer | Technology |
|---|---|
| Frontend | React (Vite), Plain CSS, Clerk React SDK |
| Backend | FastAPI, Uvicorn, Python 3.14+ |
| Auth | Clerk (session management, webhooks, route protection) |
| AI | OpenAI GPT (dynamic challenge generation) |
| Database | SQLite, SQLAlchemy ORM |
