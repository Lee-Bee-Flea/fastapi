from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.main import app
from app.config import settings
from app.database import get_db
from app.database import Base

# mote the _test suffix at the end of this string, to reference the testing DB
SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}_test'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

# quote - "this is what allows us to query the database, this is our session object"
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#  fixture - basically a function that runs before the each of out tests
#  default scope is function, meaning they run after each function below
#  issue here is deleting the created user before testing the login functionality
#  by changing to module, they are only run at the start and end of the module

#  IN THE END IRELLEVANT AS NO LONGER NEEDED HERE, BUT STILL IMPORTANT
# function: the default scope, the fixture is destroyed at the end of the test.
# class: the fixture is destroyed during teardown of the last test in the class.
# module: the fixture is destroyed during teardown of the last test in the module.
# package: the fixture is destroyed during teardown of the last test in the package.
# session: the fixture is destroyed at the end of the test session.
@pytest.fixture()
def session():
    # drops all tables
    Base.metadata.drop_all(bind=engine)
    # builds all tables
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
# now client relies on session, so will call it first, before running
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close() 
    #  this swaps out the dependencies
    #  now, any time we use client, it will use the new database
    app.dependency_overrides[get_db] = override_get_db   
    yield TestClient(app)
