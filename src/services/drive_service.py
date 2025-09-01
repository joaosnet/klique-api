import io
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build, Resource
from googleapiclient.http import MediaIoBaseUpload
from ..config import settings
from loguru import logger

class DriveService:
    def __init__(self, credentials_path: str):
        """
        Inicializa o serviço do Google Drive.
        """
        try:
            creds = service_account.Credentials.from_service_account_file(
                credentials_path,
                scopes=['https://www.googleapis.com/auth/drive']
            )
            self.service: Resource = build('drive', 'v3', credentials=creds)
            logger.info("Serviço do Google Drive inicializado com sucesso.")
        except Exception as e:
            logger.error(f"Falha ao inicializar o serviço do Google Drive: {e}")
            raise

    def get_or_create_user_folder(self, user_uid: str) -> str:
        """
        Procura por uma pasta com o nome do user_uid dentro da pasta raiz.
        Se não existir, cria a pasta.
        Retorna o ID da pasta do usuário.
        """
        root_folder_id = settings.GOOGLE_DRIVE_ROOT_FOLDER_ID
        query = f"'{root_folder_id}' in parents and name='{user_uid}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        
        try:
            response = self.service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
            files = response.get('files', [])

            if files:
                folder_id = files[0].get('id')
                logger.info(f"Pasta do usuário '{user_uid}' encontrada com ID: {folder_id}")
                return folder_id
            else:
                logger.info(f"Pasta do usuário '{user_uid}' não encontrada. Criando...")
                file_metadata = {
                    'name': user_uid,
                    'mimeType': 'application/vnd.google-apps.folder',
                    'parents': [root_folder_id]
                }
                folder = self.service.files().create(body=file_metadata, fields='id').execute()
                folder_id = folder.get('id')
                logger.info(f"Pasta do usuário '{user_uid}' criada com ID: {folder_id}")
                return folder_id
        except Exception as e:
            logger.error(f"Erro ao obter ou criar a pasta do usuário '{user_uid}': {e}")
            raise

    def upload_image(self, image_data: bytes, user_folder_id: str, filename: str) -> str:
        """
        Faz o upload de uma imagem para a pasta do usuário no Google Drive.
        Retorna o ID do arquivo criado.
        """
        try:
            file_metadata = {
                'name': filename,
                'parents': [user_folder_id]
            }
            media = MediaIoBaseUpload(io.BytesIO(image_data), mimetype='image/jpeg', resumable=True)
            file = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            file_id = file.get('id')
            logger.info(f"Imagem '{filename}' enviada para a pasta '{user_folder_id}' com ID: {file_id}")
            return file_id
        except Exception as e:
            logger.error(f"Erro ao fazer upload da imagem '{filename}': {e}")
            raise

def get_drive_service() -> DriveService:
    """
    Função para obter uma instância do DriveService.
    """
    credentials_path = settings.GOOGLE_APPLICATION_CREDENTIALS
    if not os.path.exists(credentials_path):
        raise FileNotFoundError(f"Arquivo de credenciais não encontrado em: {credentials_path}")
    return DriveService(credentials_path)
