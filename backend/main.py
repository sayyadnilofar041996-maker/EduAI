from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer
from backend.database import engine, Base
from backend.routers import auth, books, chat
from backend.routers import admin              # ✅ NEW

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
# ─────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
app.include_router(admin.router, prefix="/admin", tags=["Admin"])  # ✅ NEW

# ─────────────────────────────────────────────
# Serve frontend files
# ─────────────────────────────────────────────
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# ─────────────────────────────────────────────
# Root endpoint
# ─────────────────────────────────────────────
@app.get("/")
def root():
    return {"message": "Welcome to EduAI API 🎓"}