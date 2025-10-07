import os

from loguru import logger
from rich.logging import RichHandler

from .config import LOG_CONSOLE_ENABLED, LOG_LEVEL, LOG_RETENTION, LOG_ROTATION

# Garante que a pasta de logs existe
os.makedirs('logs', exist_ok=True)

# 1. Remove o handler padrão que imprime tudo no console
logger.remove()

# Formato padrão para logs em arquivo
file_format = (
    '{time:YYYY-MM-DD HH:mm:ss.SSS tz=America/Sao_Paulo} | {level: <8} |'
    ' {name}:{function}:{line} - {message}'
)

# 2. Adiciona o RichHandler para logs bonitos no console (se habilitado)
if LOG_CONSOLE_ENABLED:
    logger.add(
        RichHandler(markup=True, rich_tracebacks=True),
        level=LOG_LEVEL,
        format='{message}',
    )

# 3. Adiciona handler para salvar TODOS os logs da aplicação
logger.add(
    'logs/app.log',
    level=LOG_LEVEL,
    rotation=LOG_ROTATION,
    retention=LOG_RETENTION,
    format=file_format,
)

# 4. Adiciona handler específico para logs de DEBUG
logger.add(
    'logs/debug.log',
    level='DEBUG',
    rotation='5 MB',
    retention='3 days',
    format=file_format,
)

# 5. Adiciona handler específico para logs de ERROR
logger.add(
    'logs/error.log',
    level='ERROR',
    rotation='5 MB',
    retention='30 days',
    format=file_format,
)

# 6. Adiciona handler específico para webhooks do WhatsApp
logger.add(
    'logs/whatsapp.log',
    filter=lambda record: 'whatsapp' in record['name'].lower(),
    level='INFO',
    rotation=LOG_ROTATION,
    retention=LOG_RETENTION,
    format=file_format,
)

# 7. Adiciona handler específico para logs da gemini_webapi
logger.add(
    'logs/gemini.log',
    filter='gemini_webapi',
    rotation=LOG_ROTATION,
    retention=LOG_RETENTION,
    level='DEBUG',
    format=file_format,
)
