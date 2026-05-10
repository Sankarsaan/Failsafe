from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import models, schemas, database

SECRET_KEY = "super-secret-key-for-failsafe-demo"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 1 day

import bcrypt

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

from fastapi import Request

def get_current_user(request: Request, db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = request.headers.get("Authorization")
    if token and token.startswith("Bearer "):
        token = token.split(" ")[1]
    else:
        token = request.cookies.get("auth_token")
        
    if not token:
        print("DEBUG AUTH: No token found in Authorization header or auth_token cookie.")
        raise credentials_exception

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            print("DEBUG AUTH: Token decoded but no 'sub' (email) found.")
            raise credentials_exception
    except JWTError as e:
        print(f"DEBUG AUTH: JWT decode error: {e}")
        raise credentials_exception
        
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        print(f"DEBUG AUTH: User with email {email} not found in database.")
        raise credentials_exception
    return user

def get_current_hod(current_user: models.User = Depends(get_current_user)):
    if current_user.role != models.RoleEnum.admin:
        raise HTTPException(status_code=403, detail="Not enough privileges. HOD required.")
    return current_user
