from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta    
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from App.Models.User import User
from sqlalchemy.orm import Session
import hashlib
from passlib.context import CryptContext
SECRET_KEY = "secret-key-strong"  
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
def create_user(db: Session, username: str, email: str, hashed_password: str):
    user = User(username=username, email=email, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str) -> str:
    sha256_pw = hashlib.sha256(password.encode('utf-8')).hexdigest()
    return pwd_context.hash(sha256_pw)
def verify_password(plain_password: str, hashed_password: str) -> bool:
    sha256_pw = hashlib.sha256(plain_password.encode('utf-8')).hexdigest()
    return pwd_context.verify(sha256_pw, hashed_password)
def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        return user_id
    except JWTError:
        return None