from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# This is the path to our SQLite database file
# It will be created automatically when we run the app
SQLALCHEMY_DATABASE_URL = "sqlite:///./eduai.db"

# Engine is the actual connection to the database
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# SessionLocal is used to talk to the database
# Each request gets its own session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is the parent class for all our models (tables)
Base = declarative_base()

# This function gives us a database session
# We will use this in every API endpoint
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()