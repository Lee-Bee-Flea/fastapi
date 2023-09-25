from fastapi import Body, FastAPI, Response, status, HTTPException, Depends, APIRouter
from .. import models, schemas, oauth2
from sqlalchemy import func
from sqlalchemy.orm import Session
from ..database import get_db
from typing import List, Optional
from app.functions.general_funcs import get_brzycki, get_epley, db_query_func

router = APIRouter(
    # prefix means we don't have to write posts before all the routes
    prefix="/test",
    tags = ['Test'])

@router.get("/", status_code=status.HTTP_200_OK)
def test(db: Session = Depends(get_db)):

    programme = db_query_func(db=db)


    return programme.description