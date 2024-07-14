from pydantic_settings import BaseSettings
from typing import List
from pydantic import BaseModel, ValidationError

class Settings(BaseSettings):
    sqlalchemy_database_url: str
    postgres_db: str
    postgres_user: str
    postgres_password: str
    secret_key: str
    algorithm: str
    mail_username: str
    mail_password: str
    mail_from: str
    mail_port: int
    mail_server: str
    redis_host: str
    redis_port: int
    cloudinary_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str
    origins: List[str]
    
    class Config:
        env_file = ".env" 
        env_file_encoding = "utf-8"


# settings = Settings()


try: 
    settings = Settings()
    # print(f'\n -------\n{settings.model_dump()}\n-------')

except ValidationError as exc:
     print(repr(exc.errors()[0]['type']))
except Exception as a:
    print('Error is {a} ')
