from fastapi import FastAPI,Body
from pydantic import BaseModel
from typing import Optional

app = FastAPI()
class Post(BaseModel):
    title:str
    content:str
    published: bool = True
    ratings : Optional[int]= None #it will be optional

@app.get("/")
async def root():
    return {"message":"You are in main page"}

@app.get("/yourdocs")
async def get_docs():
    return {"message":"Here are your docs"}

@app.post("/create_post")
async def create_post(new_post:Post):
    print(new_post.model_dump()) 
    return {"data":new_post}
    