from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_hostname: str = "localhost"  #default value 
    database_password: str 
    database_port: str
    database_name: str
    database_username: str
    secret_key: str
    algorithm: str
    access_token_expires_weeks: int
    email_otp: str
    email_password: str
    short_limit: str
    long_limit: str
    google_client_id: str
    google_client_secret: str

    class Config:
        env_file = ".env"


settings = Settings()
