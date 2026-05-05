from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import json
from backend.database import Base


# ─────────────────────────────────────────────
# TABLE 1: users
# ─────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    id               = Column(Integer, primary_key=True, index=True)
    name             = Column(String, nullable=False)
    email            = Column(String, unique=True, index=True, nullable=False)
    password         = Column(String, nullable=False)
    grade            = Column(Integer, nullable=True)
    role             = Column(String, default="student")
    preferred_lang   = Column(String, default="english")

    chats    = relationship("ChatHistory",     back_populates="user")
    progress = relationship("StudentProgress", back_populates="user")


# ─────────────────────────────────────────────
# TABLE 2: books
# ─────────────────────────────────────────────
class Book(Base):
    __tablename__ = "books"

    id          = Column(Integer, primary_key=True, index=True)
    title       = Column(String, nullable=False)
    subject     = Column(String, nullable=False)
    grade       = Column(Integer, nullable=False)
    file_path   = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    chats    = relationship("ChatHistory",     back_populates="book")
    progress = relationship("StudentProgress", back_populates="book")

    # ← NEW — one book has many chapters
    chapters = relationship("BookChapter", back_populates="book", cascade="all, delete")


# ─────────────────────────────────────────────
# TABLE 3: chat_history
# ─────────────────────────────────────────────
class ChatHistory(Base):
    __tablename__ = "chat_history"

    id                = Column(Integer, primary_key=True, index=True)
    user_id           = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id           = Column(Integer, ForeignKey("books.id"), nullable=True)
    subject           = Column(String, nullable=False)
    question          = Column(Text, nullable=False)
    ai_answer         = Column(Text, nullable=False)
    language          = Column(String, default="english")
    doubt_detected    = Column(Boolean, default=False)
    explanation_style = Column(String, default="normal")
    timestamp         = Column(DateTime, default=datetime.utcnow)

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
    topic               = Column(String, nullable=False)
    doubt_count         = Column(Integer, default=0)
    understanding_score = Column(Float, default=5.0)
    weak_areas          = Column(Text, default="")
    suggested_revision  = Column(Text, default="")
    last_studied        = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="progress")
    book = relationship("Book", back_populates="progress")


# ─────────────────────────────────────────────
# TABLE 5: book_chapters  ← NEW
# ─────────────────────────────────────────────
class BookChapter(Base):
    __tablename__ = "book_chapters"

    id             = Column(Integer, primary_key=True, index=True)
    book_id        = Column(Integer, ForeignKey("books.id"), nullable=False)
    unit_number    = Column(Integer, nullable=False)
    unit_name      = Column(String,  nullable=False)
    chapter_name   = Column(String,  nullable=False)
    chapter_order  = Column(Integer, nullable=False)

    book = relationship("Book", back_populates="chapters")