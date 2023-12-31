from pydantic_settings import BaseSettings, SettingsConfigDict 

#configuration for variable environment
class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra='ignore', env_file='.env', env_file_encoding='utf-8')
    sqlalchemy_database_url: str
    # secret_key: str
    # algorithm: str
    cloudinary_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str
    
settings = Settings()
