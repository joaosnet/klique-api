from loguru import logger
from rich.logging import RichHandler

# 1. Remove o handler padrão que imprime tudo no console
logger.remove()

# 2. Adiciona o RichHandler para logs bonitos no console (exceto gemini_webapi)
logger.add(
    RichHandler(markup=True),
    level='INFO',
    filter=lambda record: 'gemini_webapi' not in record['name'],
    format='{message}',
)

# 3. Adiciona o handler para salvar os logs da gemini_webapi em um arquivo
logger.add(
    'logs/gemini.log',
    filter='gemini_webapi',
    rotation='10 MB',
    retention='7 days',
    level='DEBUG',
    format='{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} '
    + '| {name}:{function}:{line} - {message}',
)
