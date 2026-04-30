# EduAI — AI Teacher Web Application

An AI-powered education platform for students from Grade 1 to Grade 10.

## What it does
- Admin uploads PDF textbooks assigned to specific grade and subject
- Students log in and see only their grade's subjects
- Student asks questions and AI teaches from the actual textbook
- AI response style adjusts based on grade level

## Tech Stack
- **Backend:** FastAPI (Python)
- **Database:** SQLite + SQLAlchemy
- **Authentication:** JWT tokens + Passlib
- **PDF Reading:** PyMuPDF
- **AI:** Google Gemini API (gemini-1.5-flash)
- **Frontend:** HTML + CSS + JavaScript

## Project Structure
EduAI/
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── ai_engine.py
│   ├── utils.py
│   └── routers/
│       ├── auth.py
│       ├── books.py
│       └── chat.py
├── books/
├── frontend/
│   └── index.html
├── .env
├── .gitignore
└── README.md

## Setup Instructions
1. Clone the repository
2. Create virtual environment: `py -3.11 -m venv venv`
3. Activate: `venv\Scripts\activate`
4. Install libraries: `pip install -r requirements.txt`
5. Add your API keys to `.env`
6. Run server: `uvicorn backend.main:app --reload`

## Developer
Nilofar Sayyad

