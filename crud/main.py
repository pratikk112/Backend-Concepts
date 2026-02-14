from fastapi import FastAPI,Body,Response, status, HTTPException
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg2
from dotenv import load_dotenv,find_dotenv
from psycopg2.extras import RealDictCursor
import os
import time 

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
    ratings : Optional[int]= None #it will be optional

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

@app.get("/posts")
async def get_docs():
    cursor.execute("""SELECT * FROM posts""")
    posts = cursor.fetchall()
    print(posts)
    return {"message":posts}


@app.post("/posts",status_code=status.HTTP_201_CREATED)
async def create_post(new_post:Post):
    post_dict = new_post.model_dump()
    cursor.execute(""" INSERT INTO posts (title,content, published) VALUES (%s,%s,%s) RETURNING *""",(new_post.title, new_post.content, new_post.published))
    updated_post = cursor.fetchone()
    conn.commit()
    return {"data":updated_post}

@app.get('/posts/{id}')
async def get_post(id:int,response: Response):
    cursor.execute("""SELECT * FROM posts WHERE id = %s""",(str(id)))
    post = cursor.fetchone()
    
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND
                            ,detail=f"post with id: {id} was not found")
    return {"post_details":post}

@app.delete("/posts/{id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id:int):
   cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""",(str(id),))
   deleted_post = cursor.fetchone()
   conn.commit()
   if deleted_post == None:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with id: {id} not found")    
   return Response(status_code=status.HTTP_204_NO_CONTENT)



@app.put("/posts/{id}")
async def update_post(id:int,new_post:Post):
    cursor.execute(""" UPDATE posts SET title = %s,content = %s, published = %s WHERE id = %s RETURNING *""",(new_post.title, new_post.content, new_post.published,str(id),))
    updated_post = cursor.fetchone()
    conn.commit()
    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with id: {id} not found") 
    return {"data": updated_post}