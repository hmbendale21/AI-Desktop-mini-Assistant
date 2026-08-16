import os
from dotenv import load_dotenv, set_key

ENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")

def init_config():
    if not os.path.exists(ENV_PATH):
        with open(ENV_PATH, "w", encoding="utf-8") as f:
            f.write("# Voice Assistant Configuration\n")
            f.write("GEMINI_API_KEY=\n")
            f.write("OPENAI_API_KEY=\n")
            f.write("GROQ_API_KEY=\n")
            f.write("STT_PROVIDER=auto\n")
            f.write("TTS_SPEED=150\n")
    load_dotenv(ENV_PATH, override=True)

class ConfigManager:
    @staticmethod
    def get(key: str, default: str = "") -> str:
        load_dotenv(ENV_PATH, override=True)
        return os.getenv(key, default)

    @staticmethod
    def set(key: str, value: str):
        init_config()
        set_key(ENV_PATH, key, value)
        os.environ[key] = value

    @staticmethod
    def get_api_key() -> tuple[str, str]:
        """Returns (provider_name, api_key) or ("", "") if none set."""
        gemini = ConfigManager.get("GEMINI_API_KEY")
        openai = ConfigManager.get("OPENAI_API_KEY")
        groq = ConfigManager.get("GROQ_API_KEY")

        stt_pref = ConfigManager.get("STT_PROVIDER", "auto").lower()

        if stt_pref == "gemini" and gemini:
            return ("gemini", gemini)
        elif stt_pref == "openai" and openai:
            return ("openai", openai)
        elif stt_pref == "groq" and groq:
            return ("groq", groq)

        # Auto preference order
        if gemini:
            return ("gemini", gemini)
        if openai:
            return ("openai", openai)
        if groq:
            return ("groq", groq)

        return ("none", "")

init_config()
