from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import engine, Base
from backend.routers import auth, books, chat
from fastapi.security import HTTPBearer

security = HTTPBearer()
# ─────────────────────────────────────────────
# Create all database tables on startup
# ─────────────────────────────────────────────
Base.metadata.create_all(bind=engine)

# ─────────────────────────────────────────────
# Create FastAPI app instance
# ─────────────────────────────────────────────
app = FastAPI(
    title="EduAI",
    description="AI-powered education platform for grades 1-10",
    version="1.0.0"
)

# ─────────────────────────────────────────────
# CORS Middleware
# allows your HTML frontend to talk to this backend
# ─────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # in production, replace * with your actual domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
# Register routers
# ─────────────────────────────────────────────
app.include_router(auth.router,  prefix="/auth",  tags=["Auth"])
app.include_router(books.router, prefix="/books", tags=["Books"])
app.include_router(chat.router,  prefix="/chat",  tags=["Chat"])


# ─────────────────────────────────────────────
# Root endpoint — just to verify app is running
# ─────────────────────────────────────────────
@app.get("/")
def root():
    return {"message": "Welcome to EduAI API 🎓"}