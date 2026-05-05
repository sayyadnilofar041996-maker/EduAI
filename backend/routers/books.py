from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
import os, shutil
from backend.database import get_db
from backend.models import User, Book, BookChapter
from backend.schemas import BookOut, ChapterOut
from backend.utils import decode_access_token
from fastapi.security import OAuth2PasswordBearer
from backend.ai_engine import index_pdf, extract_chapters_from_pdf

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

BOOKS_DIR = "books"


# ─────────────────────────────────────────────
# HELPER — Get current logged in user from token
# ─────────────────────────────────────────────
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user


# ─────────────────────────────────────────────
# POST /books/upload  (admin only)
# ─────────────────────────────────────────────
@router.post("/upload", response_model=BookOut)
def upload_book(
    title:   str        = Form(...),
    subject: str        = Form(...),
    grade:   int        = Form(...),
    file:    UploadFile = File(...),
    db:      Session    = Depends(get_db),
    current_user: User  = Depends(get_current_user)
):
    # Only admin can upload
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can upload books"
        )

    # Save PDF file to /books/ folder
    os.makedirs(BOOKS_DIR, exist_ok=True)
    file_path = os.path.join(BOOKS_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Save book record to database
    book = Book(
        title=title,
        subject=subject,
        grade=grade,
        file_path=file_path
    )
    db.add(book)
    db.commit()
    db.refresh(book)

    # Index PDF into ChromaDB for RAG
    try:
        index_pdf(file_path, book.id)
    except Exception as e:
        print(f"Warning: Could not index PDF: {e}")

    # Extract chapters and save to book_chapters table
    try:
        chapters = extract_chapters_from_pdf(file_path, book.id)
        for ch in chapters:
            chapter = BookChapter(
                book_id=book.id,
                unit_number=ch.get("unit_number"),
                unit_name=ch.get("unit_name"),
                chapter_name=ch.get("chapter_name"),
                chapter_order=ch.get("chapter_order")
            )
            db.add(chapter)
        db.commit()
    except Exception as e:
        print(f"Warning: Could not extract chapters: {e}")

    return book


# ─────────────────────────────────────────────
# GET /books/{grade}  (student sees their grade)
# ─────────────────────────────────────────────
@router.get("/{grade}", response_model=List[BookOut])
def get_books_by_grade(
    grade: int,
    db:    Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    books = db.query(Book).filter(Book.grade == grade).all()
    return books


# ─────────────────────────────────────────────
# GET /books/{book_id}/chapters
# ─────────────────────────────────────────────
@router.get("/{book_id}/chapters", response_model=List[ChapterOut])
def get_book_chapters(
    book_id: int,
    db:      Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check book exists
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

    chapters = db.query(BookChapter)\
                 .filter(BookChapter.book_id == book_id)\
                 .order_by(BookChapter.chapter_order)\
                 .all()

    return chapters