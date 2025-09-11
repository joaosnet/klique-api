import os

from dotenv import load_dotenv

load_dotenv()

# Gemini API SettingsGEMINI_WEBAPI
SECRET_KEY = os.getenv('SECRET_KEY')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
SECURE_1PSID = os.getenv('SECURE_1PSID')
SECURE_1PSIDTS = os.getenv('SECURE_1PSIDTS')
GEMINI_SERVICE_PROVIDER = os.getenv('GEMINI_SERVICE_PROVIDER', 'GEMINI_WEBAPI')
GEMINI_WEBAPI_SECURE_1PSID = os.getenv('GEMINI_WEBAPI_SECURE_1PSID')
GEMINI_WEBAPI_SECURE_1PSIDTS = os.getenv('GEMINI_WEBAPI_SECURE_1PSIDTS')
GEMINI_TIMEOUT = int(os.getenv('GEMINI_TIMEOUT', '30'))
GEMINI_AUTO_CLOSE = os.getenv('GEMINI_AUTO_CLOSE', 'true').lower() == 'true'
GEMINI_CLOSE_DELAY = int(os.getenv('GEMINI_CLOSE_DELAY', '10'))
GEMINI_CONCURRENCY_LIMIT = int(os.getenv('GEMINI_CONCURRENCY_LIMIT', '5'))

# Google Cloud Settings
GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
GOOGLE_DRIVE_ROOT_FOLDER_ID = os.getenv('GOOGLE_DRIVE_ROOT_FOLDER_ID')
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')

# Auth Settings
ACCESS_TOKEN_EXPIRE_DAYS = int(os.getenv('ACCESS_TOKEN_EXPIRE_DAYS', '30'))
GMAIL_EMAIL = os.getenv('GMAIL_EMAIL')
GMAIL_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')

# MongoDB Settings
DB_CONNECTION = os.getenv('DB_CONNECTION', 'mongodb')
DB_HOST = os.getenv('DB_HOST', 'mongodb')
DB_PORT = int(os.getenv('DB_PORT', '27017'))
DB_DATABASE = os.getenv('DB_DATABASE', 'klique')
DB_USERNAME = os.getenv('DB_USERNAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')


def get_mongodb_url() -> str:
    """Constructs the MongoDB connection URL from environment variables."""
    if DB_USERNAME and DB_PASSWORD:
        return f'{DB_CONNECTION}://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/'
    return f'{DB_CONNECTION}://{DB_HOST}:{DB_PORT}/'


MONGO_URL = get_mongodb_url()

# Log Settings
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
LOG_ROTATION = os.getenv('LOG_ROTATION', '10 MB')
LOG_RETENTION = os.getenv('LOG_RETENTION', '7 days')
LOG_CONSOLE_ENABLED = (
    os.getenv('LOG_CONSOLE_ENABLED', 'true').lower() == 'true'
)
