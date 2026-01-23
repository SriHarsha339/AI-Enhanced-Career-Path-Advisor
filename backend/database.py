"""
SQLite database with SQLAlchemy for user authentication and query history.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session

# Database file path
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
DATABASE_PATH = DATA_DIR / "career.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# SQLAlchemy setup
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ============= Models =============

class User(Base):
    """User model for authentication."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to queries
    queries = relationship("CareerQuery", back_populates="user")


class CareerQuery(Base):
    """Career query history model."""
    __tablename__ = "career_queries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Nullable for guest queries
    
    # Input fields
    education_level = Column(String(100), nullable=False)
    interests = Column(Text, nullable=False)  # JSON array
    hobbies = Column(Text, nullable=False)  # JSON array
    skills = Column(Text, nullable=False)  # JSON array
    personality_traits = Column(Text, nullable=False)  # JSON array
    extra_info = Column(Text, nullable=True)
    
    # Result fields
    recommendation = Column(Text, nullable=True)  # Full markdown recommendation
    structured_data = Column(Text, nullable=True)  # JSON structured data
    top_career = Column(String(200), nullable=True)  # Featured career title
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to user
    user = relationship("User", back_populates="queries")
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API response."""
        return {
            "id": self.id,
            "queryId": self.id,
            "educationLevel": self.education_level,
            "interests": json.loads(self.interests) if self.interests else [],
            "hobbies": json.loads(self.hobbies) if self.hobbies else [],
            "skills": json.loads(self.skills) if self.skills else [],
            "personalityTraits": json.loads(self.personality_traits) if self.personality_traits else [],
            "extraInfo": self.extra_info,
            "topCareer": self.top_career,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }
    
    def to_full_response(self) -> dict:
        """Convert to full response with recommendation."""
        base = self.to_dict()
        base["recommendation"] = self.recommendation
        base["structuredData"] = json.loads(self.structured_data) if self.structured_data else None
        return base


# ============= Database Functions =============

def init_db():
    """Create all tables."""
    Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    """Get database session (for dependency injection)."""
    db = SessionLocal()
    try:
        return db
    finally:
        pass  # Don't close here, let caller manage


def get_db_context():
    """Context manager for database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============= User Operations =============

def create_user(db: Session, name: str, email: str, hashed_password: str) -> User:
    """Create a new user."""
    user = User(
        name=name,
        email=email,
        hashed_password=hashed_password
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()


# ============= Query Operations =============

def create_query(
    db: Session,
    education_level: str,
    interests: List[str],
    hobbies: List[str],
    skills: List[str],
    personality_traits: List[str],
    extra_info: str = "",
    user_id: Optional[int] = None
) -> CareerQuery:
    """Create a new career query record."""
    query = CareerQuery(
        user_id=user_id,
        education_level=education_level,
        interests=json.dumps(interests),
        hobbies=json.dumps(hobbies),
        skills=json.dumps(skills),
        personality_traits=json.dumps(personality_traits),
        extra_info=extra_info
    )
    db.add(query)
    db.commit()
    db.refresh(query)
    return query


def update_query_result(
    db: Session,
    query_id: int,
    recommendation: str,
    structured_data: dict,
    top_career: str
) -> Optional[CareerQuery]:
    """Update query with recommendation result."""
    query = db.query(CareerQuery).filter(CareerQuery.id == query_id).first()
    if query:
        query.recommendation = recommendation
        query.structured_data = json.dumps(structured_data)
        query.top_career = top_career
        db.commit()
        db.refresh(query)
    return query


def get_query_by_id(db: Session, query_id: int) -> Optional[CareerQuery]:
    """Get query by ID."""
    return db.query(CareerQuery).filter(CareerQuery.id == query_id).first()


def get_user_queries(db: Session, user_id: int, limit: int = 50) -> List[CareerQuery]:
    """Get user's query history."""
    return (
        db.query(CareerQuery)
        .filter(CareerQuery.user_id == user_id)
        .order_by(CareerQuery.created_at.desc())
        .limit(limit)
        .all()
    )


# Initialize database on import
init_db()
