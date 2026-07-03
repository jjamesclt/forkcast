import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent


class Config:
    HTTP_PORT = int(os.getenv("HTTP_PORT", "5005"))
    USER_LIST = [u.strip() for u in os.getenv("USER_LIST", "").split(",") if u.strip()]
    DATABASE_TYPE = os.getenv("DATABASE_TYPE", "sqlite")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/forkcast.db")

    # For SQLite, ensure the directory exists
    if DATABASE_URL.startswith("sqlite:///") and not DATABASE_URL.startswith("sqlite:////"):
        # Relative path — resolve against project dir
        db_path = DATABASE_URL.replace("sqlite:///", "")
        db_full_path = BASE_DIR / db_path
        db_full_path.parent.mkdir(parents=True, exist_ok=True)
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_full_path}"
    else:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # LLM settings
    LLM_TYPE = os.getenv("LLM_TYPE", "")
    LLM_URL = os.getenv("LLM_URL", "")
    LLM_PORT = os.getenv("LLM_PORT", "")
    LLM_APIKEY = os.getenv("LLM_APIKEY", "")
    LLM_MODEL = os.getenv("LLM_MODEL", "")

    @property
    def llm_enabled(self):
        return bool(self.LLM_TYPE and self.LLM_URL)
