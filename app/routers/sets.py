from fastapi import Body, FastAPI, Response, status, HTTPException, Depends, APIRouter
from .. import models, schemas, oauth2
from sqlalchemy import func
from sqlalchemy.orm import Session
from ..database import get_db
from typing import List, Optional
from app.functions import get_epley, get_brzycki


router = APIRouter(
    # prefix means we don't have to write posts before all the routes
    prefix="/sets",
    tags = ['Sets'])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.SetOut)
# @router.post("/", status_code=status.HTTP_201_CREATED)
def create_set(set: schemas.SetCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    epley = get_epley(weight=set.weight, repetitions=set.repetitions , rir=set.rir)
    brzycki = get_brzycki(weight=set.weight, repetitions=set.repetitions, rir=set.rir)

    print(f"epley: {epley}")
    print(f"brzycki: {brzycki}")

    new_set = models.Set(user_id = current_user.id, epley=epley, brzycki=brzycki, **set.model_dump())

    db.add(new_set)
    db.commit()
    db.refresh(new_set)

    print(new_set)

    # print(new_post.repetitions * new_post.weight)
    
    # •• unpacks the python dict 
    # new_set = models.Set(user_id = current_user.id, **set.model_dump())
    # db.add(new_set)
    # db.commit()
    # db.refresh(new_set)

    return new_set