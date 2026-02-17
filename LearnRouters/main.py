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
from .routers import post, user


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
        



app.include_router(post.router)
app.include_router(user.router)

@app.get("/")
async def root():
    return {"message":"You are in main page"}


