from fastapi import FastAPI,Body,Response, status, HTTPException
from pydantic import BaseModel
from typing import Optional
from random import randrange

app = FastAPI()
class Post(BaseModel):
    title:str
    content:str
    published: bool = True
    ratings : Optional[int]= None #it will be optional

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
    return {"message":my_posts}


@app.post("/posts",status_code=status.HTTP_201_CREATED)
async def create_post(new_post:Post):
    post_dict = new_post.model_dump()
    post_dict['id'] = randrange(0,10000)
    my_posts.append(post_dict) 
    return {"data":post_dict}

@app.get('/posts/{id}')
async def get_post(id:int,response: Response):
    post = find_post(id)
    if post!="Not found":
        return {"post": post}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND
                            ,detail=f"post with id: {id} was not found")

@app.delete("/posts/{id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id:int):
    for i,p in enumerate(my_posts):
        if p['id']==id:
            my_posts.pop(i)
            return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with id: {id} not found")    

@app.put("/posts/{id}")
async def update_post(id:int,new_post:Post):
    new_post = new_post.model_dump()
    new_post['id'] = id
    for i,p in enumerate(my_posts):
        if p['id']==id:
            my_posts[i] = new_post
            return {'messsage' : f"post with id : {id} is updated"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with id: {id} not found") 