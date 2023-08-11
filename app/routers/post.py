from fastapi import Body, FastAPI, Response, status, HTTPException, Depends, APIRouter
from .. import models, schemas, oauth2
from sqlalchemy import func
from sqlalchemy.orm import Session
from ..database import get_db
from typing import List, Optional


router = APIRouter(
    # prefix means we don't have to write posts before all the routes
    prefix="/posts",
    tags = ['Posts'])

@router.get("/", response_model=List[schemas.PostyOut])
def test_posts(db: Session = Depends(get_db),
                # this checks the user is logged in and returns the users id
                # used in lots of paths that require login to access
               current_user: int = Depends(oauth2.get_current_user),
               limit: int = 10,
            #    allows users to skip over search results
               skip: int = 0,
               search: Optional[str] = ""):

    # posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()

    # JOINS in sqlalchemy
    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    
    # if you wanted to return all posts by current user
    # posts = db.query(models.Post).filter(models.Post.owner_id == current_user.id).all()
    
    return posts

# @app.get("/posts")
# def get_posts():
    
#     cursor.execute("""SELECT * FROM posts """)
#     posts = cursor.fetchall()
    
#     return posts


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostyResponse)
def create_posts(post: schemas.PostyCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):


    print(current_user.email)
    
    # •• unpacks the python dict 
    new_post = models.Post(owner_id = current_user.id, **post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post

# @app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.PostyResponse)
# def create_posts(post: schemas.PostyCreate):
    
#     cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """, (post.title, post.content, post.published))
#     new_post = cursor.fetchone()
#     conn.commit()

#     return new_post


@router.get("/{id}", response_model=schemas.PostyOut)
def get_post(id: int, response: Response, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    # post = db.query(models.Post).filter(models.Post.id == id).first()

    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND
                            , detail = f'post with id {id} was not found')
    return post

# @app.get("/posts/{id}")
# def get_post(id: int, response: Response):
    
#     # strange issue where comma after str(id) has to be included to allow blank searches of id of 2+ digits
#     cursor.execute("""SELECT * FROM posts WHERE id = %s """, ( str(id),) )
#     post = cursor.fetchone()

#     if not post:
#         raise HTTPException(status_code = status.HTTP_404_NOT_FOUND
#                             , detail = f'post with id {id} was not found')
#     return post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    deleted_post_query = db.query(models.Post).filter(models.Post.id == id)

    deleted_post = deleted_post_query.first()

    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND
                            , detail=f'post with id {id} was not found')
    
    # prevents deleting a post that doesn't belong to the user
    if deleted_post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN
                            , detail='Not authorized to perform requested action')
    
    deleted_post_query.delete(synchronize_session=False)
    db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# @app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_post(id: int):
    
#     cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", ( str(id),) )
#     deleted_post = cursor.fetchone()
#     conn.commit()

#     if deleted_post == None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND
#                             , detail=f'post with id {id} was not found')
    
#     return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}", response_model=schemas.PostyResponse)
def update_post(id: int, post: schemas.PostyCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    post_query = db.query(models.Post).filter(models.Post.id == id)

    updated_post = post_query.first()  

    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND
                            , detail=f'post with id {id} was not found')
    
    # prevents updating a post that doesn't belong to the user
    if updated_post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN
                            , detail='Not authorized to perform requested action')
    
    post_query.update(post.model_dump(), synchronize_session=False)

    db.commit()
    
    return post_query.first()

# @app.put("/posts/{id}")
# def update_post(id: int, post: schemas.PostyCreate):
    
#     cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING * """, (post.title, post.content, post.published, str(id),))
#     updated_post = cursor.fetchone()
#     conn.commit()

#     if updated_post == None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND
#                             , detail=f'post with id {id} was not found')
    
#     return updated_post

