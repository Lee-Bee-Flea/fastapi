from app import models, oauth2
from app.schemas import SessionPlan, SetCreate, SetPlan
from datetime import datetime, timedelta
from typing import List
from ..database import get_db
from sqlalchemy.orm import Session
from fastapi import Body, FastAPI, Response, status, HTTPException, Depends, APIRouter

def get_epley(weight: float, repetitions: int, rir: int=0):
    epley = round ( weight * ( 1 + ( (repetitions + rir) / 30 ) ) , 2 )
    return epley

def get_brzycki(weight: float, repetitions: int, rir: int=0):
    brzycki = round ( weight * ( 36 / ( 37 - ( repetitions + rir ) ) ), 2 )
    return brzycki

# def db_query_func(db: Session):

#     programme = db.query(models.Programme).filter(models.Programme.name == 'Strength Foundation').first()

#     return programme