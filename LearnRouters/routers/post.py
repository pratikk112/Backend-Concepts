from typing import List
from .. import models, schemas
from fastapi import APIRouter,Body,Response, status, HTTPException,Depends
from sqlalchemy.orm import Session
from ..database import get_db
router = APIRouter(prefix="/posts",tags=['Users'])
@router.get("/",response_model=List[schemas.Post])
async def get_docs(db:Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts


@router.post("/",status_code=status.HTTP_201_CREATED,response_model = schemas.Post)
async def create_post(post:schemas.PostCreate,db:Session = Depends(get_db)):
    
    new_post = models.Post(**post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.get('/{id}',response_model=schemas.Post)
async def get_post(id:int,response: Response,db:Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id==id).first()
    
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND
                            ,detail=f"post with id: {id} was not found")
    return post


@router.delete("/{id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id:int,db:Session = Depends(get_db)):
    
    
    post = db.query(models.Post).filter(models.Post.id==id)
    if post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with id: {id} not found")   \
    
    post.delete(synchronize_session=False)
    db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)



@router.put("/{id}",response_model=schemas.Post)
async def update_post(id:int,new_post:schemas.PostCreate,db:Session = Depends(get_db)):
    
    post_query= db.query(models.Post).filter(models.Post.id==id)
    post = post_query.first()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with id: {id} not found") 
    
    post_query.update(**new_post.model_dump(),synchronize_session=False)
    db.commit()
    
    return post