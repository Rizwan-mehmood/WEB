from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import crud, schemas, auth, dependencies, cache
from app.database import engine, Base, get_db
from fastapi.security import OAuth2PasswordRequestForm
from typing import List
Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.post("/signup", response_model=schemas.User)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.post("/login")
def login(
    form_data: auth.OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = auth.authenticate_user(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/addpost", response_model=schemas.Post)
def add_post(
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(dependencies.get_current_active_user),
):
    return crud.create_post(db=db, post=post, user_id=current_user.id)


@app.get("/getposts", response_model=List[schemas.Post])
def get_posts(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(dependencies.get_current_active_user),
):
    cached_posts = cache.get_cached_posts(current_user.id)
    if cached_posts:
        return cached_posts
    posts = crud.get_posts(db, user_id=current_user.id)
    cache.set_cached_posts(current_user.id, posts)
    return posts


@app.delete("/deletepost/{post_id}")
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(dependencies.get_current_active_user),
):
    if not crud.delete_post(db, post_id=post_id, user_id=current_user.id):
        raise HTTPException(status_code=404, detail="Post not found")
    return {"message": "Post deleted successfully"}
