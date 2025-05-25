from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Use test database if running tests
if os.environ.get("TESTING"):
    DATABASE_URL = "sqlite:///:memory:"
else:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./navy.db")

# Only create directory if using SQLite and the directory name is not empty
if DATABASE_URL.startswith("sqlite"):
    DATABASE_PATH = DATABASE_URL.replace("sqlite:///", "")
    dir_name = os.path.dirname(DATABASE_PATH)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)

# Database setup
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class Ship(Base):
    """SQLAlchemy model for ships table"""
    __tablename__ = "ships"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    year_built = Column(Integer)
    commissioned_date = Column(Integer, nullable=True)
    stricken_date = Column(Integer, nullable=True)
    country_of_origin = Column(String, nullable=True)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 