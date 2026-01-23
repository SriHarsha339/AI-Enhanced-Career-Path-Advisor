"""
JWT Authentication with 7-day token expiry and passlib password hashing.
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# ============= Configuration =============

# Secret key for JWT (in production, use environment variable)
SECRET_KEY = "your-secret-key-change-in-production-use-env-var"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ============= Schemas =============

class Token(BaseModel):
    """Token response schema."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token payload data."""
    user_id: Optional[int] = None
    email: Optional[str] = None


class UserCreate(BaseModel):
    """User registration schema."""
    name: str
    email: str
    password: str


class UserLogin(BaseModel):
    """User login schema."""
    email: str
    password: str


class UserResponse(BaseModel):
    """User response schema (no password)."""
    id: int
    name: str
    email: str


# ============= Password Functions =============

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


# ============= JWT Functions =============

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[TokenData]:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        email: str = payload.get("email")
        
        if user_id is None:
            return None
            
        return TokenData(user_id=user_id, email=email)
    except JWTError:
        return None


def get_token_from_header(authorization: Optional[str]) -> Optional[str]:
    """Extract token from Authorization header."""
    if not authorization:
        return None
    
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    
    return parts[1]


# ============= Auth Helper Functions =============

def authenticate_user(db_session, email: str, password: str):
    """Authenticate user and return user object if valid."""
    from backend.database import get_user_by_email
    
    user = get_user_by_email(db_session, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_user_token(user) -> dict:
    """Create token response for a user."""
    access_token = create_access_token(
        data={"user_id": user.id, "email": user.email}
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    }


def get_current_user_from_token(token: str, db_session):
    """Get current user from token."""
    from backend.database import get_user_by_id
    
    token_data = decode_access_token(token)
    if token_data is None:
        return None
    
    user = get_user_by_id(db_session, token_data.user_id)
    return user
