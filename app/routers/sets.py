from fastapi import Body, FastAPI, Response, status, HTTPException, Depends, APIRouter
from .. import models, schemas, oauth2
from sqlalchemy import func
from sqlalchemy.orm import Session
from ..database import get_db
from typing import List, Optional
from app.functions.general_funcs import get_epley, get_brzycki


router = APIRouter(
    # prefix means we don't have to write posts before all the routes
    prefix="/sets",
    tags = ['Sets'])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.SetOut)
def create_set(set: schemas.SetCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    epley = get_epley(weight=set.weight, repetitions=set.repetitions , rir=set.rir)
    brzycki = get_brzycki(weight=set.weight, repetitions=set.repetitions, rir=set.rir)

    if set.repetitions > 15:
        rep_max = epley
    elif set.repetitions <= 15:
        rep_max = (epley + brzycki) / 2

    print(f"epley: {epley}")
    print(f"brzycki: {brzycki}")

    new_set = models.Set(user_id = current_user.id, epley=epley, brzycki=brzycki, rep_max=rep_max, **set.model_dump())

    db.add(new_set)
    db.commit()
    db.refresh(new_set)

    return new_set


@router.post("/group/", status_code=status.HTTP_201_CREATED, response_model=schemas.SetGroupOut)
def create_set_group(set_group: schemas.SetGroupCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    exercise_id = set_group.exercise_id
    set_list = set_group.set_list
    
    exercise = db.query(models.Exercise).filter(models.Exercise.id == exercise_id).first()

    if not exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Exercise with id {exercise_id} does not exist')
    
    # save whether selected exercise is a bodyweight exercise or not
    if exercise.type == 'bodyweight':
        bodyweight = True
        bodyweight_ratio = exercise.bodyweight_ratio
    else:
        bodyweight = False
        bodyweight_ratio = None

    new_set_group = models.SetGroup(user_id = current_user.id, exercise_id = exercise_id, bodyweight = bodyweight)

    #  these steps allow me to save the set_group entry, then grab its ID for the following set creation
    db.add(new_set_group)
    db.flush()
    db.refresh(new_set_group)
    

    for i in range(len(set_list)):
        print(set_list[i].weight)

        # FOR BODYWEUIGHT SETS ONLY - get final weight, using weight of set, plus bodyweight + bodyweight ratio of exercise
        
        # first get users most recent bodyweight measure
        user_bodyweight = db.query(models.UserPhysiology). \
            filter(models.UserPhysiology.user_id == current_user.id). \
            filter(models.UserPhysiology.measure_type == 'bodyweight'). \
            order_by(models.UserPhysiology.created_at.desc()). \
            limit(1).first()
        
        if not user_bodyweight:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'User must submit a bodyweight reading before submitting sets')
        
        print(user_bodyweight.measure)
        
        if bodyweight == True:
            final_weight = set_list[i].weight + (user_bodyweight.measure * bodyweight_ratio)
        else:
            final_weight = set_list[i].weight

        epley = get_epley(weight=final_weight, repetitions=set_list[i].repetitions , rir=set_list[i].rir)
        brzycki = get_brzycki(weight=final_weight, repetitions=set_list[i].repetitions, rir=set_list[i].rir)

        if set_list[i].repetitions > 15:
            rep_max = epley
        elif set_list[i].repetitions <= 15:
            rep_max = (epley + brzycki) / 2

        new_set = models.Set(user_id = current_user.id
                             , epley=epley
                             , brzycki=brzycki
                             , rep_max=rep_max
                             , weight=set_list[i].weight
                             , repetitions=set_list[i].repetitions
                             , rir=set_list[i].rir
                             , set_group_id=new_set_group.id
                             , set_group_rank=i+1
                             , bodyweight=bodyweight
                             , bodyweight_measure=user_bodyweight.measure
                             , bodyweight_ratio=bodyweight_ratio
                             )
        
        db.add(new_set)
    
    db.commit()

    return set_group
