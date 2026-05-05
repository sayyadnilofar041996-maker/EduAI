from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.models import User, Book, ChatHistory, BookChapter
from backend.routers.books import get_current_user
import os

router = APIRouter()


# ─────────────────────────────────────────────
# HELPER — admin only guard
# ─────────────────────────────────────────────
def admin_only(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


# ─────────────────────────────────────────────
# GET /admin/stats
# Returns total books, students, chats
# ─────────────────────────────────────────────
@router.get("/stats")
def get_stats(
    db:           Session = Depends(get_db),
    current_user: User    = Depends(admin_only)
):
    total_books    = db.query(Book).count()
    total_students = db.query(User).filter(User.role == "student").count()
    total_chats    = db.query(ChatHistory).count()

    return {
        "total_books":    total_books,
        "total_students": total_students,
        "total_chats":    total_chats
    }


# ─────────────────────────────────────────────
# GET /admin/students
# Returns all registered students
# ─────────────────────────────────────────────
@router.get("/students")
def get_all_students(
    db:           Session = Depends(get_db),
    current_user: User    = Depends(admin_only)
):
    students = db.query(User).filter(User.role == "student").all()
    return [
        {
            "id":             s.id,
            "name":           s.name,
            "email":          s.email,
            "grade":          s.grade,
            "preferred_lang": s.preferred_lang
        }
        for s in students
    ]


# ─────────────────────────────────────────────
# GET /admin/books
# Returns all books (all grades)
# ─────────────────────────────────────────────
@router.get("/books")
def get_all_books(
    db:           Session = Depends(get_db),
    current_user: User    = Depends(admin_only)
):
    books = db.query(Book).order_by(Book.grade, Book.subject).all()
    return [
        {
            "id":          b.id,
            "title":       b.title,
            "subject":     b.subject,
            "grade":       b.grade,
            "file_path":   b.file_path,
            "uploaded_at": b.uploaded_at.strftime("%d %b %Y") if b.uploaded_at else "—"
        }
        for b in books
    ]


# ─────────────────────────────────────────────
# DELETE /admin/books/{book_id}
# Deletes a book + its chapters + PDF file
# ─────────────────────────────────────────────
@router.delete("/books/{book_id}")
def delete_book(
    book_id:      int,
    db:           Session = Depends(get_db),
    current_user: User    = Depends(admin_only)
):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

    # Delete PDF file from disk
    if book.file_path and os.path.exists(book.file_path):
        os.remove(book.file_path)

    # Delete chapters from book_chapters table
    db.query(BookChapter).filter(BookChapter.book_id == book_id).delete()

    # Delete book record
    db.delete(book)
    db.commit()

    return {"message": f"Book '{book.title}' deleted successfully"}