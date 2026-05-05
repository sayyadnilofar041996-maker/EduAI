# EduAI — AI Teacher Web Application


An AI-powered education platform for students from Grade 1 to Grade 10.
Students learn directly from their textbooks — the AI teaches, explains, and adapts based on grade level and understanding.

---

## ✨ Features

- 📚 Admin uploads PDF textbooks assigned to specific grade and subject
- 🎓 Students log in and see only their grade's books and subjects
- 🤖 AI answers questions using RAG — responses come from actual textbook content
- 🧠 Doubt detection — AI changes explanation style when student is confused
- 🌐 Multilingual support — English, Hindi, Marathi
- 📊 Student progress tracking — scores, weak areas, revision suggestions
- 🗂️ Chapter sidebar with accordion, subtopics, and Resume badge
- 🔐 JWT-based authentication for students and admin

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python 3.11) |
| Database | SQLite + SQLAlchemy |
| Authentication | JWT tokens + Passlib |
| PDF Reading | PyMuPDF (pymupdf) |
| AI Model | Groq API — llama-3.3-70b-versatile |
| RAG Pipeline | LangChain + ChromaDB + SentenceTransformers |
| Frontend | Plain HTML + CSS + JavaScript |
| Environment | python-dotenv |
| File Uploads | python-multipart |

---

## 📁 Project Structure

    EduAI/
    ├── backend/
    │   ├── main.py               # FastAPI app entry point
    │   ├── database.py           # SQLAlchemy engine + session
    │   ├── models.py             # Database table models
    │   ├── schemas.py            # Pydantic request/response schemas
    │   ├── ai_engine.py          # RAG pipeline + Groq AI logic
    │   ├── utils.py              # Helper functions
    │   └── routers/
    │       ├── __init__.py
    │       ├── auth.py           # Register + Login
    │       ├── books.py          # Upload + fetch books + chapters
    │       ├── chat.py           # AI chat + history
    │       ├── admin.py          # Admin panel endpoints
    │       └── progress.py       # Student progress endpoints
    ├── books/                    # Uploaded PDF storage
    ├── vectorstore/              # ChromaDB vector index
    ├── frontend/
    │   ├── index.html
    │   ├── dashboard.html
    │   ├── chat.html
    │   ├── admin.html
    │   ├── progress.html
    │   ├── css/
    │   │   └── style.css
    │   └── js/
    │       ├── auth.js
    │       ├── dashboard.js
    │       ├── chat.js
    │       ├── admin.js
    │       └── progress.js
    ├── .env
    ├── .gitignore
    └── README.md

---

## 🗄️ Database Tables

| Table | Key Columns |
|---|---|
| users | id, name, email, password, grade, role, preferred_lang |
| books | id, title, subject, grade, file_path, uploaded_at |
| chat_history | id, user_id, book_id, question, ai_answer, language, doubt_detected |
| student_progress | id, user_id, book_id, topic, doubt_count, understanding_score, weak_areas |
| book_chapters | id, book_id, unit_number, unit_name, chapter_name, chapter_order |

---

## 🔌 API Endpoints

### Auth
| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Register new student |
| POST | `/auth/login` | Login and get JWT token |

### Books
| Method | Endpoint | Description |
|---|---|---|
| POST | `/books/upload` | Admin uploads PDF |
| GET | `/books/{grade}` | Get books for a grade |
| GET | `/books/{book_id}/chapters` | Get chapters of a book |

### Chat
| Method | Endpoint | Description |
|---|---|---|
| POST | `/chat/ask` | Ask AI a question |
| GET | `/chat/history` | Get student chat history |

### Admin
| Method | Endpoint | Description |
|---|---|---|
| GET | `/admin/stats` | Platform statistics |
| GET | `/admin/books` | List all books |
| GET | `/admin/students` | List all students |
| DELETE | `/admin/books/{id}` | Delete a book |

### Progress
| Method | Endpoint | Description |
|---|---|---|
| GET | `/progress/my` | Get student progress |

---

## ⚙️ Setup Instructions

1. **Clone the repository**

       git clone https://github.com/sayyadnilofar041996-maker/EduAI.git
       cd EduAI

2. **Create virtual environment**

       py -3.11 -m venv .venv

3. **Activate virtual environment**

       .venv\Scripts\activate

4. **Install dependencies**

       pip install -r requirements.txt

5. **Configure environment variables**

   Create a `.env` file in the root folder:

       GROQ_API_KEY=your_groq_api_key_here
       SECRET_KEY=your_jwt_secret_key_here

6. **Run the server**

       uvicorn backend.main:app --reload

7. **Open in browser**

       http://127.0.0.1:8000/frontend/

---

## 📸 Screenshots

> Screenshots will be added soon.

| Page | Screenshot |
|---|---|
| Login / Register | docs/screenshots/login.png |
| Student Dashboard | docs/screenshots/dashboard.png |
| AI Chat | docs/screenshots/chat.png |
| Admin Panel | docs/screenshots/admin.png |
| Progress Page | docs/screenshots/progress.png |

---

## 🛣️ Roadmap

- [x] Phase 1 — Planning & folder structure
- [x] Phase 2 — Full backend with RAG
- [x] Phase 3 — Full frontend
- [x] Phase 4 — Student progress page
- [ ] Version 2 — Voice input/output
- [ ] Version 2 — Deployment (Railway / Render)
- [ ] Version 2 — Full screenshots & docs

---

## 👩‍💻 Developer

**Nilofar Sayyad**
GitHub: [@sayyadnilofar041996-maker](https://github.com/sayyadnilofar041996-maker)