import firebase_admin
import os
from firebase_admin import auth, credentials
from fastapi import HTTPException, status

from src.config import settings
from src.logger import logger


class FirebaseService:
    def __init__(self):
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate(settings.GOOGLE_APPLICATION_CREDENTIALS)
                firebase_admin.initialize_app(cred)
            logger.info("Firebase Admin SDK inicializado com sucesso.")
        except Exception as e:
            logger.error(f"Erro ao inicializar o Firebase Admin SDK: {e}")
            # Em um ambiente de produção, você pode querer lidar com isso de forma mais robusta
            raise RuntimeError("Não foi possível inicializar o Firebase Admin SDK.") from e

    def verify_firebase_token(self, token: str) -> dict:
        """
        Verifica um token de ID do Firebase e retorna os dados do usuário.

        Args:
            token: O token de ID do Firebase enviado pelo cliente.

        Returns:
            Um dicionário com os dados do usuário decodificados.

        Raises:
            HTTPException: Se o token for inválido, expirado ou revogado.
        """
        try:
            # Remove o prefixo "Bearer " se ele existir
            if token.startswith("Bearer "):
                token = token.split("Bearer ")[1]
                
            decoded_token = auth.verify_id_token(token)
            return decoded_token
        except auth.ExpiredIdTokenError:
            logger.warning("Token do Firebase expirado.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expirado. Por favor, faça login novamente.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except auth.InvalidIdTokenError:
            logger.warning("Token do Firebase inválido.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido. Por favor, faça login novamente.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            logger.error(f"Erro inesperado ao verificar o token do Firebase: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao processar a autenticação.",
                headers={"WWW-Authenticate": "Bearer"},
            )
