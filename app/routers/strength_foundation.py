from fastapi import Body, FastAPI, Response, status, HTTPException, Depends, APIRouter
from .. import models, schemas, oauth2
from sqlalchemy import func
from sqlalchemy.orm import Session
from ..database import get_db
from typing import List, Optional
from app.functions import get_epley, get_brzycki


router = APIRouter(
    # prefix means we don't have to write posts before all the routes
    prefix="/strength_foundation",
    tags = ['Strength Foundation'])


@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=schemas.StrengthFoundationSignupConfirm)
def signup(info: schemas.StrengthFoundationSignup, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    # get programme record of Strength Foundation programme
    programme = db.query(models.Programme).filter(models.Programme.name == 'Strength Foundation').first()

    # check no active programmes in programme_instances table
    active_programmes = db.query(models.ProgrammeInstance).filter(models.ProgrammeInstance.status == 'active'
                                                                  , models.ProgrammeInstance.user_id == current_user.id).first()
    if active_programmes:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Current user is already enrolled in an active programme")
    
    # make sure all included exercises have associated RM's
    if info.squat.included == True and info.squat.rep_max is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Squat included in programme signup without rep max value")
    
    if info.deadlift.included == True and info.deadlift.rep_max is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Deadlift included in programme signup without rep max value")
    
    if info.bench_press.included == True and info.bench_press.rep_max is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bench Press included in programme signup without rep max value")
    
    if info.overhead_press.included == True and info.overhead_press.rep_max is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Overhead Press included in programme signup without rep max value")
    
    if info.pullup.included == True and info.pullup.rep_max is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Pullup included in programme signup without rep max value")


    # create new programme instance
    new_programme_instance = models.ProgrammeInstance(user_id = current_user.id
                                                      , programme_id = programme.id
                                                      , status = 'active'
                                                      )
    
    db.add(new_programme_instance)
    db.flush()
    db.refresh(new_programme_instance)
    
    # create new strength_foundation_signups entry
    new_sf_signup = models.StrengthFoundationSignup(programme_instance_id = new_programme_instance.id
                                                    , user_id = current_user.id
                                                    , start_bodyweight = info.start_bodyweight
                                                    , squat = info.squat.included
                                                    , deadlift = info.deadlift.included
                                                    , bench_press = info.bench_press.included
                                                    , overhead_press = info.overhead_press.included
                                                    , pullup = info.pullup.included
                                                    , start_squat_rm = info.squat.rep_max
                                                    , start_deadlift_rm = info.deadlift.rep_max
                                                    , start_bench_press_rm = info.bench_press.rep_max
                                                    , start_overhead_press_rm = info.overhead_press.rep_max
                                                    , start_pullup_rm = info.pullup.rep_max)
    
    db.add(new_sf_signup)
    db.commit()

    confirmation = schemas.StrengthFoundationSignupConfirm(programme_name=programme.name
                                                           , start_date=new_programme_instance.start_at
                                                           , programme_instance_id=new_programme_instance.id)

    return confirmation


@router.put("/cancel/{id}", status_code=status.HTTP_200_OK, response_model=schemas.StrengthFoundationCancelConfirm)
def signup(id: int, reason: schemas.StrengthFoundationCancel, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    # get programme record of Strength Foundation programme
    programme = db.query(models.Programme).filter(models.Programme.name == 'Strength Foundation').first()

    # check programme_instance exists, that it's a Strength Foundation programme, belonging to current user and is active
    programme_instance_query = db.query(models.ProgrammeInstance).filter(models.ProgrammeInstance.id == id
                                                                    , models.ProgrammeInstance.user_id == current_user.id
                                                                    , models.ProgrammeInstance.programme_id == programme.id
                                                                    , models.ProgrammeInstance.status == 'active')
    
    programme_instance_to_cancel = programme_instance_query.first()
    
    # if no active programme
    if not programme_instance_to_cancel:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND
                            , detail = f'No active Strength Foundation programme instance record with id {id}')

    
    # update programme_instances table:
    # status = 'cancelled', cancelled_at = now, cancelled_reason = reason
    cancellation_reason = schemas.CancelOptions(reason.reason)

    programme_instance_query.update({'status': 'cancelled'
                                     , 'cancelled_at': func.current_timestamp()
                                     , 'cancelled_reason': cancellation_reason}
                                     , synchronize_session=False)
    db.commit()

    return_object = schemas.StrengthFoundationCancelConfirm(programme_name=programme.name
                                                            , cancelled_date=programme_instance_to_cancel.cancelled_at
                                                            , programme_instance_id=programme_instance_to_cancel.id
                                                            )

    return return_object