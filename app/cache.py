from pathlib import Path

from .logger import logger

CACHE_DIR = Path('/tmp')
LAST_STATUS_IMAGE_PATH = CACHE_DIR / 'klique_last_status.png'
LAST_STATUS_ID_PATH = CACHE_DIR / 'klique_last_status_id.txt'


class StatusImageCache:
    """
    Cache simples para armazenar a última imagem e o ID do último status postado.
    """

    def save_status_image(self, image_bytes: bytes):
        """Salva a imagem de status mais recente no sistema de arquivos."""
        try:
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            with open(LAST_STATUS_IMAGE_PATH, 'wb') as f:
                f.write(image_bytes)
            logger.info(
                f'📁 Imagem de status salva no cache: {LAST_STATUS_IMAGE_PATH}'
            )
        except Exception as e:
            logger.error(f'❌ Erro ao salvar imagem de status no cache: {e}')

    def get_last_status_image(self) -> bytes | None:
        """Recupera a última imagem de status do cache."""
        if not LAST_STATUS_IMAGE_PATH.exists():
            logger.warning('🖼️ Nenhuma imagem de status encontrada no cache.')
            return None
        try:
            with open(LAST_STATUS_IMAGE_PATH, 'rb') as f:
                return f.read()
        except Exception as e:
            logger.error(f'❌ Erro ao ler imagem de status do cache: {e}')
            return None

    def save_last_status_id(self, status_id: str):
        """Salva o ID do último status postado."""
        try:
            with open(LAST_STATUS_ID_PATH, 'w') as f:
                f.write(status_id)
            logger.info(f'🆔 ID do status salvo no cache: {status_id}')
        except Exception as e:
            logger.error(f'❌ Erro ao salvar ID do status no cache: {e}')

    def get_last_status_id(self) -> str | None:
        """Recupera o ID do último status postado."""
        if not LAST_STATUS_ID_PATH.exists():
            return None
        try:
            with open(LAST_STATUS_ID_PATH, 'r') as f:
                return f.read().strip()
        except Exception as e:
            logger.error(f'❌ Erro ao ler ID do status do cache: {e}')
            return None

    def clear_cache(self):
        """Limpa os arquivos de cache."""
        try:
            if LAST_STATUS_IMAGE_PATH.exists():
                LAST_STATUS_IMAGE_PATH.unlink()
                logger.info('🗑️ Cache de imagem de status limpo.')
            if LAST_STATUS_ID_PATH.exists():
                LAST_STATUS_ID_PATH.unlink()
                logger.info('🗑️ Cache de ID de status limpo.')
        except Exception as e:
            logger.error(f'❌ Erro ao limpar o cache: {e}')


# Instância única do cache para ser usada em toda a aplicação
status_image_cache = StatusImageCache()
