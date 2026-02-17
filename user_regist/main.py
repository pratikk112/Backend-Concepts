from fastapi import FastAPI,Body,Response, status, HTTPException,Depends
from pydantic import BaseModel
from typing import Optional,List
from random import randrange
import psycopg2
from dotenv import load_dotenv,find_dotenv
from psycopg2.extras import RealDictCursor
import os
import time 
from sqlalchemy.orm import Session
from .utils import hash

from . import models,schemas
from .database import engine  ,Base, get_db



load_dotenv(find_dotenv())
db_user = os.getenv("PG_USER")
db_pw = os.getenv("PG_PW")
db_name = os.getenv('PG_DB_NAME')
db_host = os.getenv('PG_DB_HOST')



Base.metadata.create_all(bind=engine)
app = FastAPI()


while True:
    try:
        conn = psycopg2.connect(database=db_name,user = db_user,
                                password = db_pw, host = db_host,cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection was succesful")
        break
    except Exception as e:
        print(f"got error while database connection {e}")
        time.sleep(2)
        



my_posts = [
    {"title":"my post 1 ", "content":"from noida", "id":1},
    {"title":"my post 2 ", "content":"from Mahasamund", "id":2}
]

def find_post(id:int):
    for p in my_posts:
        if p['id']==id:
            return p
    
    return "Not found"


@app.get("/")
async def root():
    return {"message":"You are in main page"}




@app.get("/posts",response_model=List[schemas.Post])
async def get_docs(db:Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts


@app.post("/posts",status_code=status.HTTP_201_CREATED,response_model = schemas.Post)
async def create_post(post:schemas.PostCreate,db:Session = Depends(get_db)):
    
    new_post = models.Post(**post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@app.get('/posts/{id}',response_model=schemas.Post)
async def get_post(id:int,response: Response,db:Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id==id).first()
    
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND
                            ,detail=f"post with id: {id} was not found")
    return post


@app.delete("/posts/{id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id:int,db:Session = Depends(get_db)):
    
    
    post = db.query(models.Post).filter(models.Post.id==id)
    if post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with id: {id} not found")   \
    
    post.delete(synchronize_session=False)
    db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)



@app.put("/posts/{id}",response_model=schemas.Post)
async def update_post(id:int,new_post:schemas.PostCreate,db:Session = Depends(get_db)):
    
    post_query= db.query(models.Post).filter(models.Post.id==id)
    post = post_query.first()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with id: {id} not found") 
    
    post_query.update(**new_post.model_dump(),synchronize_session=False)
    db.commit()
    
    return post


@app.post("/users", status_code=status.HTTP_201_CREATED,response_model=schemas.UserOut)
def create_user(user:schemas.UserCreate, db:Session=Depends(get_db)):
    
    check_user = db.query(models.User).filter(models.User.email==user.email).first()
    if check_user != None:
        raise HTTPException(status_code=status.HTTP_226_IM_USED,detail=f"email : {user.email} already in use")
    # hashing password
    hashed_password = hash(user.password)
    user.password = hashed_password
    
    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@app.get("/users/{id}", response_model= schemas.UserOut)
def get_user(id:int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"user with id : {id} not found")
    
    return user