from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
import os, shutil
from backend.database import get_db
from backend.models import User, Book
from backend.schemas import BookOut
from backend.utils import decode_access_token
from fastapi.security import OAuth2PasswordBearer
from backend.ai_engine import index_pdf

router = APIRouter()

# This tells FastAPI where to find the token in the request
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

BOOKS_DIR = "books"  # folder where PDFs are saved


# ─────────────────────────────────────────────
# HELPER — Get current logged in user from token
# ─────────────────────────────────────────────
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Reads JWT token from request header.
    Returns the logged-in User object.
    Raises 401 if token is invalid or expired.
    """
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
    title:   str         = Form(...),
    subject: str         = Form(...),
    grade:   int         = Form(...),
    file:    UploadFile  = File(...),
    db:      Session     = Depends(get_db),
    current_user: User   = Depends(get_current_user)
):
    """
    Admin uploads a PDF textbook.
    Steps:
    1. Check user is admin
    2. Save PDF file to /books/ folder
    3. Save book info to database
    4. Index PDF into ChromaDB for RAG
    5. Return book info
    """

    # Step 1 — only admin can upload
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can upload books"
        )

    # Step 2 — save PDF to /books/ folder
    # Create folder if it doesn't exist
    os.makedirs(BOOKS_DIR, exist_ok=True)

    # Build a clean file path: books/grade5_science.pdf
    file_name = f"grade{grade}_{subject.lower()}_{file.filename}"
    file_path = os.path.join(BOOKS_DIR, file_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Step 3 — save book info to database
    new_book = Book(
        title     = title,
        subject   = subject,
        grade     = grade,
        file_path = file_path
    )
    db.add(new_book)
    db.commit()
    db.refresh(new_book)

    # Step 4 — Index PDF into ChromaDB for RAG
    index_pdf(file_path, new_book.id)

    # Step 5 — return book info
    return new_book


# ─────────────────────────────────────────────
# GET /books/{grade}  (students see their grade)
# ─────────────────────────────────────────────
@router.get("/{grade}", response_model=List[BookOut])
def get_books_by_grade(
    grade:        int,
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_current_user)
):
    """
    Returns all books for a specific grade.
    Students can only fetch their own grade's books.
    Admins can fetch any grade.
    """

    # Students can only see their own grade
    if current_user.role == "student" and current_user.grade != grade:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own grade's books"
        )

    books = db.query(Book).filter(Book.grade == grade).all()
    return books