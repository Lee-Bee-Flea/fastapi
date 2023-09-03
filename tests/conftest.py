#  special file pytest uses where you can put fixtures to be made available to entire tests directory

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app import models
from app.main import app
from app.oauth2 import create_access_token
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


@pytest.fixture
def test_user(client):
    user_data = {"email":"hello1234@gmail.com",
                 "password":"password123"}
    res = client.post("/users/", json=user_data)

    assert res.status_code == 201
    new_user = res.json()
    new_user['password'] = user_data['password']
    return new_user


@pytest.fixture
def test_user2(client):
    user_data = {"email":"goodbye1234@gmail.com",
                 "password":"password123"}
    res = client.post("/users/", json=user_data)

    assert res.status_code == 201
    new_user = res.json()
    new_user['password'] = user_data['password']
    return new_user


@pytest.fixture
def token(test_user):
    return create_access_token({"user_id": test_user['id']})


@pytest.fixture
def authorized_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }

    return client


@pytest.fixture
def test_posts(test_user, session, test_user2):
    posts_data = [{
        "title": "first title",
        "content": "first content",
        "owner_id": test_user['id']
    }, {
        "title": "2nd title",
        "content": "2nd content",
        "owner_id": test_user['id']
    },
        {
        "title": "3rd title",
        "content": "3rd content",
        "owner_id": test_user['id']
    }, {
        "title": "3rd title",
        "content": "3rd content",
        "owner_id": test_user2['id']
    }]

    def create_post_model(post):
        return models.Post(**post)

    post_map = map(create_post_model, posts_data)
    posts = list(post_map)

    session.add_all(posts)
    # session.add_all([models.Post(title="first title", content="first content", owner_id=test_user['id']),
    #                 models.Post(title="2nd title", content="2nd content", owner_id=test_user['id']), models.Post(title="3rd title", content="3rd content", owner_id=test_user['id'])])
    session.commit()

    posts = session.query(models.Post).all()
    return posts