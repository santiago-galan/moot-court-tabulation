from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_name: str = "Moot Court Tabulation System"
    db_path: str = str(BASE_DIR / "mcts.db")
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: list[str] = ["*"]
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = ""
    ngrok_auth_token: str = ""

    @property
    def database_url(self) -> str:
        return f"sqlite:///{self.db_path}"

    model_config = {"env_prefix": "MCTS_"}


settings = Settings()
