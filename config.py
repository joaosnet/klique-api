import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_1PSID = os.getenv("GEMINI_1PSID", "")
GEMINI_1PSIDTS = os.getenv("GEMINI_1PSIDTS", "")
PROXY = os.getenv("HTTP_PROXY") or os.getenv("HTTPS_PROXY")
TIMEOUT = float(os.getenv("GEMINI_TIMEOUT", "30"))
AUTO_CLOSE = os.getenv("GEMINI_AUTO_CLOSE", "false").lower() == "true"
CLOSE_DELAY = float(os.getenv("GEMINI_CLOSE_DELAY", "300"))
CONCURRENCY_LIMIT = int(
    os.getenv("GEMINI_CONCURRENCY", "4")
)  # ajuste conforme sua conta/infra
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30