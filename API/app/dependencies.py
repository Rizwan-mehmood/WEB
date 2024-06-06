from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user

def get_current_active_user(current_user: str = Depends(get_current_user)):
    if current_user is None:
        raise HTTPException(status_code=400, detail="Invalid authentication credentials")
    return current_user
