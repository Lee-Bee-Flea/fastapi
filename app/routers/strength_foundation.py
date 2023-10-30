from fastapi import Body, FastAPI, Response, status, HTTPException, Depends, APIRouter
from .. import models, schemas, oauth2
from sqlalchemy import func
from sqlalchemy.orm import Session, aliased
from ..database import get_db
from typing import List, Optional
from app.functions.general_funcs import get_brzycki, get_epley
from app.functions.strength_foundation_funcs import check_exercise_input, get_strength_foundation_session_plan, check_active_programme_exists, query_submissions_for_exercise
from datetime import datetime


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

    # create new bodyweight entry in user_physiology table
    new_bdyweight_entry = models.UserPhysiology(user_id = current_user.id
                                                , measure_type = 'bodyweight'
                                                , measure_unit = 'kg'
                                                , measure = info.start_bodyweight)
    
    db.add(new_bdyweight_entry)
    db.commit()

    confirmation = schemas.StrengthFoundationSignupConfirm(programme_name=programme.name
                                                           , start_date=new_programme_instance.start_at
                                                           , programme_instance_id=new_programme_instance.id)

    return confirmation


@router.put("/cancel_programme/{id}", status_code=status.HTTP_200_OK, response_model=schemas.StrengthFoundationCancelConfirm)
def cancel_programme(id: int, reason: schemas.StrengthFoundationCancel, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    
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


@router.get("/session_plan/{exercise}", status_code=status.HTTP_200_OK, response_model=schemas.SessionPlan)
def session_plan(exercise: str, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    # checks active programme for current user, and returns programme instance record along with strength_foundation_signup record
    active_programme_instance, strength_foundation_signup_instance = check_active_programme_exists(db=db, user_id=current_user.id)

    # takes in user entered exercise, checks its valid, and whether it is included in the active programme
    start_rm, exercise_instance = check_exercise_input(db=db, submitted_exercise=exercise, strength_foundation_signup_instance=strength_foundation_signup_instance)

    # returns sessions already submitted and best RM for given exercise
    total_sessions_submitted, best_rm = query_submissions_for_exercise(db=db, exercise_instance=exercise_instance, programme_instance=active_programme_instance)

    # if first session, use start/estimated RM, otherwise best seen RM in previous sessions
    # if not first session, use best performed RM from previous session
    if total_sessions_submitted == 0:
        input_rm = start_rm
    elif total_sessions_submitted > 0:
        input_rm = best_rm
    
    # build session plan
    session_plan = get_strength_foundation_session_plan(exercise_name=exercise_instance.name
                                                , current_rm=input_rm
                                                , session_number=total_sessions_submitted + 1
                                                , bodyweight=strength_foundation_signup_instance.start_bodyweight)

    return session_plan


# @router.post("/submit_session", status_code=status.HTTP_200_OK, response_model=schemas.SessionPlan)
@router.post("/submit_session", status_code=status.HTTP_200_OK)
def submit_session(session: List[schemas.SessionCreate], db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    active_programme_instance, strength_foundation_signup_instance = check_active_programme_exists(db=db, user_id=current_user.id)
    
    # get users bodyweight for later when creating sets
    user_bodyweight = db.query(models.UserPhysiology). \
        filter(models.UserPhysiology.user_id == current_user.id). \
        filter(models.UserPhysiology.measure_type == 'bodyweight'). \
        order_by(models.UserPhysiology.created_at.desc()). \
        limit(1).first()
    
    # shouldn't ever happen as user creates bodyweight measure on signup
    if not user_bodyweight:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'User must submit a bodyweight reading before submitting sets')
    
    # create a session
    new_session = models.Session(user_id = current_user.id
                                 , programme_instance_id = active_programme_instance.id
                                 , start_at = datetime.now()
                                 , end_at = datetime.now()
                                 , live = False
                                 )
    
    db.add(new_session)
    db.flush()
    db.refresh(new_session)

    # empty list to keep track of exercises submitted, used at the end to check no duplicates (can only submit one exercise per session)
    exercise_list = []
    timestamp_list = []

    # since we are accepting a list of set_groups, we need to cycle through all of them and check logic on each
    for i in range(len(session)):

        # takes in user entered exercise, checks its valid, and whether it is included in the active programme
        start_rm, exercise_instance = check_exercise_input(db=db, submitted_exercise=session[i].exercise_name, strength_foundation_signup_instance=strength_foundation_signup_instance)

        # returns sessions already submitted and best RM for given exercise
        total_sessions_submitted, best_rm = query_submissions_for_exercise(db=db, exercise_instance=exercise_instance, programme_instance=active_programme_instance)
        
        # checks correct session number for where user is up to in programme
        if total_sessions_submitted != session[i].session_number -1:
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST
                                , detail = f'User has completed {total_sessions_submitted} sessions but is trying to submit session number {session[i].session_number}. Submit session {total_sessions_submitted + 1} first')

   
        exercise_list.append(session[i].exercise_name)
        timestamp_list.append(session[i].start)
        timestamp_list.append(session[i].end)

        # create a set group for each exercise being submitted
        new_set_group = models.SetGroup(user_id = current_user.id,
                                        session_id = new_session.id,
                                        exercise_id = exercise_instance.id,
                                        bodyweight = exercise_instance.type=='bodyweight')
        
        db.add(new_set_group)
        db.flush()
        db.refresh(new_set_group)

        #  this cycles through all sets for a given set_group / exercise
        for j in range(len(session[i].set_list)):
            
            if exercise_instance.type == 'bodyweight':
                final_weight = session[i].set_list[j].weight + (user_bodyweight.measure * exercise_instance.bodyweight_ratio)
            else:
                final_weight = session[i].set_list[j].weight

            epley = get_epley(weight=final_weight
                              , repetitions=session[i].set_list[j].repetitions 
                              , rir=session[i].set_list[j].rir)
            brzycki = get_brzycki(weight=final_weight
                                  , repetitions=session[i].set_list[j].repetitions
                                  , rir=session[i].set_list[j].rir)
            
            # getting average RM from epley and brz (only epley if reps > 15 as brz gets weird)
            if session[i].set_list[j].repetitions > 15:
                rep_max = epley
            elif session[i].set_list[j].repetitions <= 15:
                rep_max = round( (epley + brzycki) / 2 , 2)

            new_set = models.Set(user_id = current_user.id
                             , epley=epley
                             , brzycki=brzycki
                             , rep_max=rep_max
                             , weight=session[i].set_list[j].weight
                             , repetitions=session[i].set_list[j].repetitions
                             , rir=session[i].set_list[j].rir
                             , set_group_id=new_set_group.id
                             , set_group_rank=j+1
                             , bodyweight=exercise_instance.type=='bodyweight'
                             , bodyweight_measure=user_bodyweight.measure
                             , bodyweight_ratio=exercise_instance.bodyweight_ratio
                             )
            
            db.add(new_set)

    # this checks no duplicates are in the list of exercises
    if len(exercise_list) != len(set(exercise_list)):
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST
                                , detail = 'Cannot submit two of the same exercises in the same session')
    
    # update new_session start and end values after populating list of timestamps with set_group data
    new_session.start_at = min(timestamp_list)
    new_session.end_at = max(timestamp_list)

    # create all sets of each set group

    db.commit()
    
    return {"message": f"Successfully added new session (id={new_session.id}) with exercises {exercise_list}"}


# edit session
# check session belongs to current user
# check programme instance isn't completed and is strength foundation and is active

# @router.put("/edit/session/{id}")
@router.put("/edit/session/{id}", response_model=schemas.SessionEditResponse)
def edit_session(id: int, session: schemas.SessionEdit, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    session_query = db.query(models.Session).filter(models.Session.id == id)

    updated_session = session_query.first()  

    if updated_session == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND
                            , detail=f'Session with id {id} was not found')
    
    # prevents updating a session that doesn't belong to the user
    if updated_session.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN
                            , detail='Not authorized to perform requested action')
    
    programme_record = db.query(models.Programme).filter(models.Programme.name == 'Strength Foundation').first()

    programme_instance_record = db.query(models.ProgrammeInstance).filter(models.ProgrammeInstance.id == updated_session.programme_instance_id).first()

    # if session has a programme_instance that isn't strength foundation  (id = 26)
    if not programme_instance_record or programme_record.id != programme_instance_record.programme_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND
                            , detail=f'Session with id {id} is not associated with a Strength Foundation Programme')
    
    # if programme instance is no longer active (id = 27)
    if programme_instance_record.status != 'active':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN
                            , detail='Cannot edit a session belonging to a non-active programme')
    
    session_query.update(session.model_dump(), synchronize_session=False)

    db.commit()
    
    return session_query.first()


# delete sessionsss
# check session belongs to current user
# check programme instance isn't completed
# what happend if user deletes a session number 4, when they have already submitted 5?
# prevent deletion unless most recent session?