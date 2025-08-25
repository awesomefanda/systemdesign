from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Python Microservice Starter"
    metrics_path: str = "/metrics"

def get_settings():
    return Settings()
