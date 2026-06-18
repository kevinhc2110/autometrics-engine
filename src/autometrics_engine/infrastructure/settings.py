from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    app_name: str = "Autometrics Engine"

    gemini_api_key: str
    gemini_model: str = "gemini-2.5-flash-lite"

    postgres_dsn: str
    postgres_user: str
    postgres_password: str
    postgres_db: str

    redis_url: str = "redis://localhost:6379/0"

    sqlserver_host: str = ""
    sqlserver_port: int = 1433
    sqlserver_database: str = ""
    sqlserver_user: str = ""
    sqlserver_password: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
