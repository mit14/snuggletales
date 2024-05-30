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
    EMAIL_PASSWORD: str

    class Config:
        env_file = ".env"


settings = Settings()
