from sqlalchemy.orm import Session
from app.models import User, Post
from app.schemas import UserCreate, PostCreate
from app.auth import get_password_hash

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_post(db: Session, post: PostCreate, user_id: int):
    db_post = Post(**post.dict(), owner_id=user_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

def get_posts(db: Session, user_id: int):
    return db.query(Post).filter(Post.owner_id == user_id).all()

def delete_post(db: Session, post_id: int, user_id: int):
    db_post = db.query(Post).filter(Post.id == post_id, Post.owner_id == user_id).first()
    if db_post:
        db.delete(db_post)
        db.commit()
        return True
    return False
