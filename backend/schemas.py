from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# ─────────────────────────────────────────────
# USER SCHEMAS
# ─────────────────────────────────────────────

class UserRegister(BaseModel):
    """What the API accepts when a new user registers."""
    name:             str
    email:            EmailStr        # Pydantic validates it's a real email format
    password:         str
    grade:            Optional[int] = None   # None for admin, 1–10 for students
    role:             str = "student"
    preferred_lang:   str = "english"


class UserLogin(BaseModel):
    """What the API accepts when a user logs in."""
    email:    EmailStr
    password: str


class UserOut(BaseModel):
    """What the API sends back — notice: NO password."""
    id:             int
    name:           str
    email:          str
    grade:          Optional[int]
    role:           str
    preferred_lang: str

    class Config:
        from_attributes = True   # allows Pydantic to read SQLAlchemy model objects directly


class TokenOut(BaseModel):
    """What the API sends back after successful login."""
    access_token: str
    token_type:   str = "bearer"


# ─────────────────────────────────────────────
# BOOK SCHEMAS
# ─────────────────────────────────────────────

class BookOut(BaseModel):
    """What the API sends back when listing books."""
    id:          int
    title:       str
    subject:     str
    grade:       int
    uploaded_at: datetime

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# CHAT SCHEMAS
# ─────────────────────────────────────────────

class ChatRequest(BaseModel):
    """What the student sends when asking a question."""
    subject:  str
    question: str
    language: str = "english"   # student can request hindi or marathi


class ChatResponse(BaseModel):
    """What the API sends back after Gemini answers."""
    ai_answer:         str
    doubt_detected:    bool
    explanation_style: str
    language:          str


class ChatHistoryOut(BaseModel):
    """One record from chat history."""
    id:                int
    subject:           str
    question:          str
    ai_answer:         str
    doubt_detected:    bool
    explanation_style: str
    timestamp:         datetime

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# STUDENT PROGRESS SCHEMAS
# ─────────────────────────────────────────────

class ProgressOut(BaseModel):
    """What the API sends back for a student's progress on a topic."""
    id:                  int
    subject:             str
    topic:               str
    doubt_count:         int
    understanding_score: float
    weak_areas:          str
    suggested_revision:  str
    last_studied:        datetime

    class Config:
        from_attributes = True