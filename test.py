import sys
import os

# This adds D:\EduAI to Python's search path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database import engine, Base
from backend.models import User, Book, ChatHistory, StudentProgress

Base.metadata.create_all(bind=engine)
print("✅ All 4 tables created successfully!")