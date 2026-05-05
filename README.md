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