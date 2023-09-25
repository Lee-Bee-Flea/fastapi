from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models
from .database import engine
from .routers import post, user, auth, vote, sets, strength_foundation
from .config import settings

print(settings.database_username)

# no longer needed since adding alembic
# models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# with * it is effectively a public API that can be called from any origin
origins = ['*']

app.add_middleware(
    # middleware is apparently like a function that runs before every request
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# some tech to grab the routes in the router folder using the router object
app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)
app.include_router(sets.router)
app.include_router(strength_foundation.router)

@app.get("/")
async def root():
    return {"message": "Welcome to my API!! Tweaking"}



    
