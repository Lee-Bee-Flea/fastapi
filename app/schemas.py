from pydantic import BaseModel, EmailStr, PositiveInt
from pydantic.types import conint, confloat
from datetime import datetime
from typing import Optional, List
from enum import Enum

# changed name to Posty to distinguish from Post(Base) from SQLAlchemy models
# this is a pydantic model for reference
# ensures that structure of a Post is adhered to when sending and receiving data

#  this defines the base structure
class PostyBase(BaseModel):
    title: str
    content: str
    published: bool = True

# in this case its for when user sends post to API (below is opposite case)
# used in the path operators that require a post to be sent to API (create, edit)
class PostyCreate(PostyBase):
    # this means its the same as PostyBase
    pass

#  note - this had to come before PostyResponse (below) as it is referenced in PostyResponse
# and python is always read top down
class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    # Pydantic's orm_mode will tell the Pydantic model to read the data even if it is not a dict, 
    # but an ORM model (or any other arbitrary object with attributes).
    class Config:
        orm_mode = True

# this will define what we send back to the user
# often want to exclude certain fields in response - id, password etc
class PostyResponse(PostyBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserOut

    # Pydantic's orm_mode will tell the Pydantic model to read the data even if it is not a dict, 
    # but an ORM model (or any other arbitrary object with attributes).
    class Config:
        orm_mode = True


class PostyOut(BaseModel):
    Post: PostyResponse
    votes: int

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[int] = None

class Votey(BaseModel):
    post_id: int
    direction: conint(ge=0,le=1)

# what a user should provide to create a set
class SetCreate(BaseModel):
    weight: confloat(ge=0)
    repetitions: conint(ge=0)
    rir: Optional[conint(ge=0)] = 0

# what a SessionPlan should give the user
class SetPlan(BaseModel):
    weight: confloat(ge=0)
    # this is a string to handle the 10 or more than (10+) rep cases
    repetitions: str
    rir: Optional[conint(ge=0)] = 0

# what should be returned to a user after creating a set
class SetOut(SetCreate):
    epley: float
    brzycki: float
    rep_max: float
    set_group_rank: Optional[int]
    set_group_id: Optional[str]
    created_at: datetime
    user_id: int

    class Config:
        orm_mode = True


class SetGroupCreate(BaseModel):
    exercise_id: int
    set_list: List[SetCreate]


class SetGroupOut(SetGroupCreate):
    pass


class ExerciseRMPair(BaseModel):
    included: bool
    rep_max: Optional[confloat(ge=0)] = None


class StrengthFoundationSignup(BaseModel):
    start_bodyweight: confloat(ge=0)
    squat: ExerciseRMPair
    deadlift: ExerciseRMPair
    bench_press: ExerciseRMPair
    overhead_press: ExerciseRMPair
    pullup: ExerciseRMPair


class StrengthFoundationSignupConfirm(BaseModel):
    programme_name: str
    start_date: datetime
    programme_instance_id: int


class CancelOptions(str, Enum):
    injured = 'injured'
    difficulty_high = 'too hard'
    difficulty_low = 'too easy'
    starting_new_programme = 'starting new programme'
    restarting_same_programme = 'restarting same programme'


class StrengthFoundationCancel(BaseModel):
    reason: CancelOptions


class StrengthFoundationCancelConfirm(BaseModel):
    programme_name: str
    cancelled_date: datetime
    programme_instance_id: int


class SessionPlan(BaseModel):
    exercise_name: str
    session_number: int
    # added start and end to make copying output into a SessionCreate easier
    start: datetime
    end: datetime
    set_list: List[SetPlan]


class SessionCreate(BaseModel):
    exercise_name: str
    session_number: int
    start: datetime
    end: datetime
    set_list: List[SetCreate]