from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.models import User, Book, ChatHistory, StudentProgress
from backend.schemas import ChatRequest, ChatResponse, ChatHistoryOut
from backend.routers.books import get_current_user
from backend.ai_engine import get_ai_response, detect_doubt

router = APIRouter()


# ─────────────────────────────────────────────
# POST /chat/ask
# ─────────────────────────────────────────────
@router.post("/ask", response_model=ChatResponse)
def ask_question(
    request:      ChatRequest,
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_current_user)
):
    """
    Student asks a question.
    Steps:
    1. Find the right book by subject + grade
    2. Detect doubt
    3. Get AI response using RAG
    4. Save to chat_history
    5. Update student_progress
    6. Return answer
    """

    # Step 1 — find book by subject and student's grade
    book = db.query(Book).filter(
    Book.subject.ilike(request.subject),
    Book.grade   == current_user.grade
).first()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No book found for subject '{request.subject}' in grade {current_user.grade}"
        )

    # Step 2 — detect doubt + decide explanation style
    doubt_found = detect_doubt(request.question)
    if doubt_found:
        # Rotate through explanation styles
        last_chat = db.query(ChatHistory).filter(
            ChatHistory.user_id == current_user.id,
            ChatHistory.subject == request.subject
        ).order_by(ChatHistory.timestamp.desc()).first()

        if last_chat and last_chat.explanation_style == "story":
            explanation_style = "example"
        elif last_chat and last_chat.explanation_style == "example":
            explanation_style = "analogy"
        else:
            explanation_style = "story"
    else:
        explanation_style = "normal"

    # Step 3 — get AI response using RAG
    result = get_ai_response(
        question          = request.question,
        book_id           = book.id,
        grade             = current_user.grade,
        language          = request.language,
        explanation_style = explanation_style,
        subject           = request.subject
    )

    ai_answer   = result["answer"]
    doubt_found = result["doubt_detected"]

    # Step 4 — save to chat_history
    chat_record = ChatHistory(
        user_id           = current_user.id,
        book_id           = book.id,
        subject           = request.subject,
        question          = request.question,
        ai_answer         = ai_answer,
        language          = request.language,
        doubt_detected    = doubt_found,
        explanation_style = explanation_style
    )
    db.add(chat_record)
    db.commit()

    # Step 5 — update student progress
    progress = db.query(StudentProgress).filter(
        StudentProgress.user_id == current_user.id,
        StudentProgress.subject == request.subject
    ).first()

    if progress:
        # Update existing progress
        if doubt_found:
            progress.doubt_count += 1
            progress.understanding_score = max(
                0.0, progress.understanding_score - 0.5
            )
        else:
            progress.understanding_score = min(
                10.0, progress.understanding_score + 0.2
            )
        db.commit()
    else:
        # Create new progress record
        new_progress = StudentProgress(
            user_id             = current_user.id,
            book_id             = book.id,
            subject             = request.subject,
            topic               = request.question[:50],
            doubt_count         = 1 if doubt_found else 0,
            understanding_score = 4.5 if doubt_found else 5.2
        )
        db.add(new_progress)
        db.commit()

    # Step 6 — return answer
    return ChatResponse(
        ai_answer         = ai_answer,
        doubt_detected    = doubt_found,
        explanation_style = explanation_style,
        language          = request.language
    )


# ─────────────────────────────────────────────
# GET /chat/history
# ─────────────────────────────────────────────
@router.get("/history", response_model=List[ChatHistoryOut])
def get_chat_history(
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_current_user)
):
    """Returns all past conversations for the logged-in student."""
    history = db.query(ChatHistory).filter(
        ChatHistory.user_id == current_user.id
    ).order_by(ChatHistory.timestamp.desc()).all()
    return history