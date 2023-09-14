from pydantic import BaseModel, EmailStr
from pydantic.types import conint
from datetime import datetime
from typing import Optional

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
    weight: float
    repetitions: int
    rir: Optional[int] = 0

# what should be returned to a user after creating a set
class SetOut(SetCreate):
    epley: float
    brzycki: float
    set_group_rank: Optional[int]
    set_group_id: Optional[str]
    created_at: datetime
    user_id: int

    class Config:
        orm_mode = True