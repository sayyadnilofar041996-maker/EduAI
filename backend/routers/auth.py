from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import User
from backend.schemas import UserRegister, UserOut, UserLogin, TokenOut
from backend.utils import hash_password, verify_password, create_access_token

router = APIRouter()


# ─────────────────────────────────────────────
# POST /auth/register
# ─────────────────────────────────────────────
@router.post("/register", response_model=UserOut)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Registers a new user (student or admin).
    Steps:
    1. Check if email already exists
    2. Hash the password
    3. Save user to database
    4. Return user info (no password)
    """

    # Step 1 — check if email already registered
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Step 2 — hash the password
    hashed = hash_password(user_data.password)

    # Step 3 — create new User object and save to database
    new_user = User(
        name           = user_data.name,
        email          = user_data.email,
        password       = hashed,
        grade          = user_data.grade,
        role           = user_data.role,
        preferred_lang = user_data.preferred_lang
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)   # loads the auto-generated id back into new_user

    # Step 4 — return user (UserOut schema hides password automatically)
    return new_user


# ─────────────────────────────────────────────
# POST /auth/login
# ─────────────────────────────────────────────
@router.post("/login", response_model=TokenOut)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    Logs in a user.
    Steps:
    1. Find user by email
    2. Verify password
    3. Create JWT token
    4. Return token
    """

    # Step 1 — find user by email
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Step 2 — verify password
    if not verify_password(user_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Step 3 — create JWT token with user info inside
    token_data = {
        "sub": str(user.id),    # "sub" = subject, standard JWT field
        "role": user.role,
        "grade": user.grade,
        "preferred_lang": user.preferred_lang
    }
    token = create_access_token(data=token_data)

    # Step 4 — return token
    return {"access_token": token, "token_type": "bearer"}