from flask import Blueprint, render_template
from config import Config

settings_bp = Blueprint("settings", __name__)


@settings_bp.route("/")
def view_settings():
    config = Config()
    # Mask API key
    api_key = config.LLM_APIKEY
    masked_key = (api_key[:4] + "****" + api_key[-4:]) if len(api_key) > 8 else "****" if api_key else ""

    settings = {
        "HTTP_PORT": config.HTTP_PORT,
        "USER_LIST": config.USER_LIST,
        "DATABASE_TYPE": config.DATABASE_TYPE,
        "DATABASE_URL": config.DATABASE_URL,
        "LLM_TYPE": config.LLM_TYPE or "(disabled)",
        "LLM_URL": config.LLM_URL or "(not set)",
        "LLM_PORT": config.LLM_PORT or "(not set)",
        "LLM_APIKEY": masked_key or "(not set)",
        "LLM_MODEL": config.LLM_MODEL or "(not set)",
        "LLM_Enabled": "Yes" if config.llm_enabled else "No",
    }
    return render_template("settings.html", settings=settings)
