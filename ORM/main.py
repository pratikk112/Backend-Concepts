from fastapi import FastAPI,Body,Response, status, HTTPException,Depends
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg2
from dotenv import load_dotenv,find_dotenv
from psycopg2.extras import RealDictCursor
import os
import time 
from sqlalchemy.orm import Session


from . import models
from .database import engine  ,Base, get_db
Base.metadata.create_all(bind=engine)



load_dotenv(find_dotenv())
db_user = os.getenv("PG_USER")
db_pw = os.getenv("PG_PW")
db_name = os.getenv('PG_DB_NAME')
db_host = os.getenv('PG_DB_HOST')
 
app = FastAPI()
class Post(BaseModel):
    title:str
    content:str
    published: bool = True

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


@app.get("/sqlalchemy")
def test_posts(db:Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return {"data":posts}



@app.get("/posts")
async def get_docs(db:Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return {"message":posts}


@app.post("/posts",status_code=status.HTTP_201_CREATED)
async def create_post(post:Post,db:Session = Depends(get_db)):
    
    # new_post = models.Post(title = post.title, content = post.content, published = post.published)
    # note instead of writing all like above , we can do one thing we can send it like kwargs after converting that to a dictionary
    # print(post.model_dump())
    new_post = models.Post(**post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"data":new_post}

@app.get('/posts/{id}')
async def get_post(id:int,response: Response,db:Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id==id).first()
    
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND
                            ,detail=f"post with id: {id} was not found")
    return {"post_details":post}


@app.delete("/posts/{id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id:int,db:Session = Depends(get_db)):
    
    
    post = db.query(models.Post).filter(models.Post.id==id)
    if post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with id: {id} not found")   \
    
    post.delete(synchronize_session=False)
    db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)



@app.put("/posts/{id}")
async def update_post(id:int,new_post:Post,db:Session = Depends(get_db)):
    
    post_query= db.query(models.Post).filter(models.Post.id==id)
    post = post_query.first()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with id: {id} not found") 
    
    post_query.update(**new_post.model_dump(),synchronize_session=False)
    db.commit()
    
    return {"data": post}