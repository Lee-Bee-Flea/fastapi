# deals with all of our environment variables
# variables saved on machine like PATH etc

# could in theory set all of these on our machine, but would be to much work
# instead, set using .env file on prject level

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    class Config:
        env_file = ".env"

settings = Settings()