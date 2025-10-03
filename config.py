from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    mongodb_uri: str = Field(..., alias="MONGODB_URI")
    database_name: str = Field(..., alias="DATABASE_NAME")
    db_port: int = Field(default=27017, alias="DB_PORT")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
