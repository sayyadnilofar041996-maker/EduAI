from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import User, StudentProgress
from backend.routers.books import get_current_user

router = APIRouter()


# ─────────────────────────────────────────────
# GET /progress/my
# Returns logged in student's full progress
# ─────────────────────────────────────────────
@router.get("/my")
def get_my_progress(
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_current_user)
):
    progress = db.query(StudentProgress).filter(
        StudentProgress.user_id == current_user.id
    ).all()

    return {
        "progress": [
            {
                "subject":             p.subject,
                "topic":               p.topic,
                "doubt_count":         p.doubt_count,
                "understanding_score": p.understanding_score,
                "weak_areas":          p.weak_areas,
                "suggested_revision":  p.suggested_revision,
                "last_studied":        str(p.last_studied) if p.last_studied else None
            }
            for p in progress
        ]
    }