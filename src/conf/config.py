from pydantic_settings import BaseSettings, SettingsConfigDict 

#configuration for variable environment
class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra='ignore', env_file='.env', env_file_encoding='utf-8')
    # sqlalchemy_database_url: str
    # secret_key: str
    # algorithm: str
    # mail_username: str
    # mail_password: str
    # mail_from: str
    # mail_port: int
    # mail_server: str
    # redis_host: str = 'localhost'
    # redis_port: int = 6379
    cloudinary_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str
    
# import cloudinary
# from pydantic_settings import BaseSettings


# def init_cloudinary():
#     cloudinary.config(
#         cloud_name=settings.cloudinary_name,
#         api_key=settings.cloudinary_api_key,
#         api_secret=settings.cloudinary_api_secret,
#         secure=True
#     )


# class Settings(BaseSettings):
#     sqlalchemy_database_url: str = "postgresql+psycopg2://user:password@localhost:5432/postgres"
#     secret_key: str = "secretkey"
#     algorithm: str = "HS256"

#     mail_username: str = "example@meta.ua"
#     mail_password: str = "secretPassword"
#     mail_from: str = "example@meta.ua"
#     mail_port: int = 465
#     mail_server: str = "smtp.meta.ua"

#     redis_host: str = "localhost"
#     redis_port: int = 6379
#     redis_password: str = "secretPassword"

#     cloudinary_name: str = "name"
#     cloudinary_api_key: str = "1234567890"
#     cloudinary_api_secret: str = "secret"

#     class Config:
#         env_file = ".env"
#         env_file_encoding = "utf-8"


settings = Settings()
