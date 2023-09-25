from fastapi import HTTPException, status
from app import models
from app.schemas import SessionPlan, SetPlan
from datetime import datetime, timedelta
from sqlalchemy.orm import Session, aliased
from sqlalchemy import func



def get_strength_foundation_session_plan(exercise_name: str, current_rm: float, session_number: int, bodyweight: float):
    
    # instantiate an empty set list for adding to
    set_list = []

    # set total_sets variable
    if session_number == 1:
        total_sets = 3
    else:
        total_sets = 4

    # note - when calculating for pullup, current_rm should include bodyweight + added weight

    # create ratio_list values
    if session_number == 1:
        ratio_list = [0.75, 0.775, 0.8]
        rep_target_list = ['10', '10', '10']
    elif session_number == 2:
        ratio_list = [0.75, 0.775, 0.8, 0.825]
        rep_target_list = ['8', '8', '8', '8+']
    elif session_number == 3:
        ratio_list = [0.775, 0.8, 0.825, 0.85]
        rep_target_list = ['6', '6', '6', '6+']
    elif session_number == 4:
        ratio_list = [0.8, 0.825, 0.85, 0.875]
        rep_target_list = ['5', '5', '5', '5+']
    elif session_number == 5:
        ratio_list = [0.825, 0.85, 0.875, 0.9]
        rep_target_list = ['4', '4', '4', '4+']
    elif session_number == 6:
        ratio_list = [0.85, 0.875, 0.9, 0.925]
        rep_target_list = ['3', '3', '3', '3+']
    elif session_number == 7:
        ratio_list = [0.875, 0.9, 0.925, 0.95]
        rep_target_list = ['2', '2', '2', '2+']

    if exercise_name == 'Pull-up':
        for i in range(0,total_sets):
            weight_calc = (current_rm * ratio_list[i]) - bodyweight
            if weight_calc < 0:
                weight_calc = 0
            set = SetPlan(weight=weight_calc, repetitions=rep_target_list[i])
            set_list.append(set)

    if exercise_name != 'Pull-up':
        for i in range(0,total_sets):
            set = SetPlan(weight=current_rm * ratio_list[i], repetitions=rep_target_list[i])
            set_list.append(set)

    return SessionPlan(exercise_name=exercise_name
                       , session_number=session_number
                       , set_list=set_list
                       , start=datetime.now()
                       , end=datetime.now() + timedelta(hours=1))


# checks a user has an active programme instance, and returns corresponfing signup record
def check_active_programme_exists(db: Session, user_id: int):
    
    # get programme record of Strength Foundation programme
    programme = db.query(models.Programme).filter(models.Programme.name == 'Strength Foundation').first()

    # check user has active programme_instance for strength foundation
    active_programme_query = db.query(models.ProgrammeInstance).filter(models.ProgrammeInstance.user_id == user_id
                                                                    , models.ProgrammeInstance.programme_id == programme.id
                                                                    , models.ProgrammeInstance.status == 'active')
    
    active_programme_instance = active_programme_query.first()

    # if no active programme
    if not active_programme_instance:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND
                            , detail = f'No active Strength Foundation programme for current user')
    
    #  find strength foundation signup record
    strength_foundation_signup_instance = db.query(models.StrengthFoundationSignup).filter(models.StrengthFoundationSignup.programme_instance_id == active_programme_instance.id).first()
    
    return active_programme_instance, strength_foundation_signup_instance


# checks if user entered exercise is valid for strength foundation programme, and is active in current users programme
# also performs logic to calculate start RM for the programme based on bodyweight / barbell exercise
def check_exercise_input(db:Session, submitted_exercise: str, strength_foundation_signup_instance: models.StrengthFoundationSignup):
    
    # check valid exercise name (one of the 5)
    formatted_exercise = submitted_exercise.lower()
    valid_exercises = ['squat', 'deadlift', 'bench press', 'overhead press', 'pull-up', 'pullup']

    if not formatted_exercise in valid_exercises:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND
                            , detail = f'Exercise {submitted_exercise} not in accepted list of exercises. Use "Squat", "Deadlift", "Overhead Press", "Bench Press" or "Pull-up"')
    
    # check exercise is included in programme
    if formatted_exercise == 'squat':
        inclusion_check = strength_foundation_signup_instance.squat
        db_exercise_name = 'Squat'
        db_exercise_type = 'barbell'
        start_rm = strength_foundation_signup_instance.start_squat_rm
    elif formatted_exercise == 'deadlift':
        inclusion_check = strength_foundation_signup_instance.deadlift
        db_exercise_name = 'Deadlift'
        db_exercise_type = 'barbell'
        start_rm = strength_foundation_signup_instance.start_deadlift_rm
    elif formatted_exercise == 'bench press':
        inclusion_check = strength_foundation_signup_instance.bench_press
        db_exercise_name = 'Bench Press'
        db_exercise_type = 'barbell'
        start_rm = strength_foundation_signup_instance.start_bench_press_rm
    elif formatted_exercise == 'overhead press':
        inclusion_check = strength_foundation_signup_instance.overhead_press
        db_exercise_name = 'Overhead Press'
        db_exercise_type = 'barbell'
        start_rm = strength_foundation_signup_instance.start_overhead_press_rm
    elif formatted_exercise in ['pull-up', 'pullup']:
        inclusion_check = strength_foundation_signup_instance.pullup
        db_exercise_name = 'Pull-up'
        db_exercise_type = 'bodyweight'
        start_rm = strength_foundation_signup_instance.start_pullup_rm  + strength_foundation_signup_instance.start_bodyweight

    if inclusion_check == False:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST
                            , detail = f'Exercise {submitted_exercise} is a valid exercise, but has not been included in your current active Strength Foundation programme')
    
    exercise_instance = db.query(models.Exercise).filter(models.Exercise.name == db_exercise_name, models.Exercise.type == db_exercise_type).first()
    
    return start_rm, exercise_instance


# 
def query_submissions_for_exercise(db:Session, exercise_instance: models.Exercise, programme_instance: models.ProgrammeInstance):

    # Define aliases for the tables to use in the query
    pi = aliased(models.ProgrammeInstance)
    s = aliased(models.Session)
    sg = aliased(models.SetGroup)
    e = aliased(models.Exercise)
    se = aliased(models.Set)

    # query to return total sessions completed and best RM performance for a given exercise
    query = db.query(
        func.count(func.distinct(sg.id)).label('sessions_completed'),
        func.max(se.rep_max).label('best_rm')). \
        select_from(pi). \
        join(s, pi.id == s.programme_instance_id). \
        join(sg, s.id == sg.session_id). \
        join(e, sg.exercise_id == e.id). \
        join(se, sg.id == se.set_group_id). \
        filter(e.name == exercise_instance.name). \
        filter(e.type == exercise_instance.type). \
        filter(pi.id == programme_instance.id)
    
    total_sessions_submitted = query.first().sessions_completed
    best_rm = query.first().best_rm

    if total_sessions_submitted == 8:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST
                            , detail = f'Already submitted required 8 sessions for {exercise_instance.name}')

    return total_sessions_submitted, best_rm