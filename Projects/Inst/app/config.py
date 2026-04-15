from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "env.txt"),
        env_file_encoding="utf-8",
    )

    app_host: str = "127.0.0.1"
    app_port: int = 8000
    app_debug: bool = True

    database_url: str = "sqlite:///./inst_analytics.db"

    instagram_username: str = ""
    instagram_password: str = ""
    instagram_sessionid: str = ""
    instagram_session_path: str = ".instagrapi-session.json"
    reports_dir: str = "reports"

    google_credentials_json: str = ""
    google_credentials_file: str = ""
    google_sheets_spreadsheet_id: str = ""
    google_docs_folder_id: str = ""
    google_export_retries: int = 2


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
