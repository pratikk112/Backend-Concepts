from .. import models, schemas,utils
from fastapi import APIRouter,Body,Response, status, HTTPException,Depends
from sqlalchemy.orm import Session
from ..database import get_db
router = APIRouter(prefix="/users",tags=['Users'])

@router.post("/", status_code=status.HTTP_201_CREATED,response_model=schemas.UserOut)
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

@router.get("/{id}", response_model= schemas.UserOut)
def get_user(id:int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"user with id : {id} not found")
    
    return user