from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
db_user = os.getenv("PG_USER")
db_pw = os.getenv("PG_PW")
db_name = os.getenv('PG_DB_NAME')
db_host = os.getenv('PG_DB_HOST')

SQLALCHEMY_DATABASE_URL = f"postgresql://{db_user}:{db_pw}@{db_host}/{db_name}"

print(SQLALCHEMY_DATABASE_URL)
# # creating engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

Base = declarative_base()

SessionLocal  = sessionmaker(autocommit = False, autoflush=False,bind=engine)

# create a session dependency

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()