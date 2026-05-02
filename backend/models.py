from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base


# ─────────────────────────────────────────────
# TABLE 1: users
# ─────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    id               = Column(Integer, primary_key=True, index=True)
    name             = Column(String, nullable=False)
    email            = Column(String, unique=True, index=True, nullable=False)
    password         = Column(String, nullable=False)          # stored as bcrypt hash
    grade            = Column(Integer, nullable=True)          # 1–10 for students; NULL for admin
    role             = Column(String, default="student")       # "student" or "admin"
    preferred_lang   = Column(String, default="english")       # "english", "hindi", "marathi"

    # Relationships — one user has many chat messages and many progress records
    chats    = relationship("ChatHistory",     back_populates="user")
    progress = relationship("StudentProgress", back_populates="user")


# ─────────────────────────────────────────────
# TABLE 2: books
# ─────────────────────────────────────────────
class Book(Base):
    __tablename__ = "books"

    id          = Column(Integer, primary_key=True, index=True)
    title       = Column(String, nullable=False)
    subject     = Column(String, nullable=False)               # e.g. "Science", "Maths"
    grade       = Column(Integer, nullable=False)              # 1–10
    file_path   = Column(String, nullable=False)               # path to PDF in /books/ folder
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    # Relationships — one book appears in many chats and progress records
    chats    = relationship("ChatHistory",     back_populates="book")
    progress = relationship("StudentProgress", back_populates="book")


# ─────────────────────────────────────────────
# TABLE 3: chat_history
# ─────────────────────────────────────────────
class ChatHistory(Base):
    __tablename__ = "chat_history"

    id                = Column(Integer, primary_key=True, index=True)
    user_id           = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id           = Column(Integer, ForeignKey("books.id"), nullable=True)
    subject           = Column(String, nullable=False)
    question          = Column(Text, nullable=False)           # student's question (Text = long string)
    ai_answer         = Column(Text, nullable=False)           # Gemini's reply
    language          = Column(String, default="english")      # language used for this reply
    doubt_detected    = Column(Boolean, default=False)         # True if student said "didn't understand"
    explanation_style = Column(String, default="normal")       # "normal", "story", "example", "diagram"
    timestamp         = Column(DateTime, default=datetime.utcnow)

    # Relationships — each chat belongs to one user and one book
    user = relationship("User", back_populates="chats")
    book = relationship("Book", back_populates="chats")


# ─────────────────────────────────────────────
# TABLE 4: student_progress
# ─────────────────────────────────────────────
class StudentProgress(Base):
    __tablename__ = "student_progress"

    id                  = Column(Integer, primary_key=True, index=True)
    user_id             = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id             = Column(Integer, ForeignKey("books.id"), nullable=True)
    subject             = Column(String, nullable=False)
    topic               = Column(String, nullable=False)       # e.g. "Photosynthesis"
    doubt_count         = Column(Integer, default=0)           # how many times student doubted this topic
    understanding_score = Column(Float, default=5.0)           # 0.0–10.0, updated by backend logic
    weak_areas          = Column(Text, default="")             # comma-separated weak subtopics
    suggested_revision  = Column(Text, default="")             # AI-generated revision suggestion
    last_studied        = Column(DateTime, default=datetime.utcnow)

    # Relationships — each progress record belongs to one user and one book
    user = relationship("User", back_populates="progress")
    book = relationship("Book", back_populates="progress")