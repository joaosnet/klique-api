import random
import smtplib
from datetime import timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from ..config import (
    ACCESS_TOKEN_EXPIRE_DAYS,
    GMAIL_EMAIL,
    GMAIL_PASSWORD,
    GOOGLE_CLIENT_ID,
)
from ..database import (
    get_mail_confirmation_collection,
)
from ..dependencies import (
    authenticate_token,
    authenticate_user,
    create_access_token,
    get_current_active_user,
    get_password_hash,
    get_token_from_header,
    get_users_collection,
    invalidate_token,
    verify_password,
)
from ..logger import logger
from .schemas import (
    ChangePasswordRequest,
    DefautMessage,
    GoogleLoginRequest,
    RequestChangeEmail,
    SearchByEmailRequest,
    Token,
    User,
    ValidToken,
)

router = APIRouter()


@router.post('/auth/google', response_model=Token, tags=['auth'])
async def google_login(
    request: GoogleLoginRequest, db_users=Depends(get_users_collection)
):
    try:
        id_info = id_token.verify_oauth2_token(
            request.token, google_requests.Request(), GOOGLE_CLIENT_ID
        )
        email = id_info.get('email')
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Email not found in Google token',
            )

        user = db_users.find_one({'email': email})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='User not registered',
            )

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_DAYS)
        access_token = create_access_token(
            data={'sub': user['email']}, expires_delta=access_token_expires
        )
        return {'access_token': access_token, 'token_type': 'bearer'}

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid Google token',
        )


@router.post('/token', response_model=Token, tags=['auth'])
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db_users=Depends(get_users_collection),
):
    user = await authenticate_user(
        db_users, form_data.username, form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_DAYS)
    access_token = create_access_token(
        data={'sub': user['email']}, expires_delta=access_token_expires
    )
    return {'access_token': access_token, 'token_type': 'bearer'}


@router.post('/auth/valid_token', tags=['auth'], response_model=ValidToken)
async def valid_token(
    token: str = Depends(get_token_from_header),
    db_users=Depends(get_users_collection),
):
    try:
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Authorization Token not found',
            )

        auth_result = await authenticate_token(token, db_users=db_users)

        if isinstance(auth_result, HTTPException):
            raise auth_result

        request = ValidToken(success=True, message='Token válido').model_dump(
            by_alias=True, exclude_unset=True
        )
        return request
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f'Unknown error: {e}', exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post('/auth/logout', tags=['auth'], response_model=ValidToken)
async def logout(token: str = Depends(get_token_from_header)):
    try:
        if not token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Token não fornecido. Não é possível fazer logout.',
            )

        if invalidate_token(token):
            return ValidToken(
                success=True, message='Logout feito com sucesso!'
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Não foi possível fazer logout!',
        )
    except HTTPException:
        logger.info('', exc_info=True)
        raise
    except Exception as e:
        logger.info(str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Erro Desconhecido: {str(e)}',
        )


@router.post(
    '/auth/changePassword', tags=['auth'], response_model=DefautMessage
)
async def change_password(
    request: ChangePasswordRequest,
    db_users=Depends(get_users_collection),
):
    try:
        request = request.model_dump(by_alias=True, exclude_unset=True)
        email = request['email']
        password = request['password']
        new_password = request['new_password']
        # Verificar se o usuário existe
        user = db_users.find_one({'email': email})

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Não há conta com esse email',
            )

        # Validar tamanho mínimo da nova senha
        if len(new_password) < 6:  # noqa: PLR2004
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Senha precisa ter no minimo 6 caracteres!',
            )

        # Verificar senha atual
        if not verify_password(password, user['password']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='A senha antiga não confere',
            )

        # Atualizar senha
        hashed_password = get_password_hash(new_password)
        db_users.update_one(
            {'email': email}, {'$set': {'password': hashed_password}}
        )

        # Verificar se o usuário se cadastrou com o Google
        if user.get('google'):
            # Atualizar senha na conta do Google
            google_update_result = await update_google_password(
                email, new_password
            )
            if not google_update_result['success']:
                raise HTTPException(
                    status_code=500,
                    detail=google_update_result['message'],
                )

        # Enviar alerta para o Google
        alert_result = await send_alert_to_google(email, user['name'])
        if not alert_result['success']:
            raise HTTPException(
                status_code=500,
                detail=alert_result['message'],
            )

        return DefautMessage(
            success=True, message='Senha alterada com sucesso'
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={'success': False, 'message': f'Exception {str(e)}'},
        )


@router.post('/auth/changeEmail', tags=['auth'])
async def change_email(
    request: RequestChangeEmail,
    db_users=Depends(get_users_collection),
    df_mail_confirmation=Depends(get_mail_confirmation_collection),
):  # noqa: PLR0911
    email = request.email
    password = request.password
    new_email = request.new_email
    # Verificar se os emails são iguais
    if email == new_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Este é o seu email atual',
        )

    try:
        # Verificar se o usuário existe
        user = db_users.find_one({'email': email})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Não há conta com esse email',
            )

        # Verificar senha
        if not verify_password(password, user['password']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='A senha não confere',
            )

        # Gerar código de confirmação
        confirmation_code = str(random.randint(1000, 9999))

        # Remover confirmações anteriores
        df_mail_confirmation.delete_many({
            'user_id': str(user['_id']),
            'request_type': 'change_email',
        })

        # Criar nova confirmação
        df_mail_confirmation.insert_one({
            'user_id': str(user['_id']),
            'request_type': 'change_email',
            'confirmation_code': confirmation_code,
            'new_email': new_email,
        })

        # Enviar código por email
        result = await _send_email(
            new_email,
            'Confirmação de alteração de e-mail',
            f'Olá, {user["name"]}! '
            f'Seu código de confirmação é: {confirmation_code}',
        )

        if not result['success']:
            raise HTTPException(
                status_code=500,
                detail='Erro ao enviar email',
            )

        request = {'success': True, 'message': 'Código enviado para o email'}

        return request
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f'Exception {str(e)}',
        )


async def _send_email(to_email: str, subject: str, body: str):
    smtp_server = 'smtp.gmail.com'
    port = 587
    sender_email = GMAIL_EMAIL
    password = GMAIL_PASSWORD

    message = MIMEMultipart()
    message['From'] = f'KliqueApp <{sender_email}>'
    message['To'] = to_email
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain', 'utf-8'))

    try:
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()
            server.login(sender_email, password)
            server.send_message(message)
        return {'success': True, 'message': 'email sent'}
    except Exception as e:
        logger.error(f'Failed to send email to {to_email}: {e}')
        return {'success': False, 'message': str(e)}


async def send_alert_to_old_mail(
    old_email: str, user_name: str, new_email: str
):
    subject = 'E-mail alterado | Klique'
    body = f"""Olá, {user_name}! Sua conta teve o endereço de e-mail
    alterado, para entrar você deve utilizar o novo endereço {new_email}.
    Caso você não tenha alterado o e-mail entre em contato conosco."""
    return await _send_email(old_email, subject, body)


async def send_alert_to_google(email: str, user_name: str):
    subject = 'Senha alterada | Klique'
    body = f"""Olá, {user_name}! Sua senha foi alterada com sucesso.
    Caso você não tenha alterado a senha, entre em contato conosco."""
    return await _send_email(email, subject, body)


@router.post('/auth/confirmChangeEmail', tags=['auth'])
async def confirm_change_email(
    request: RequestChangeEmail,
    db_users=Depends(get_users_collection),
    df_mail_confirmation=Depends(get_mail_confirmation_collection),
):
    email = request.email
    new_email = request.new_email
    confirmation_code = request.confirmation_code
    try:
        # Buscar usuário
        user = db_users.find_one({'email': email})
        if not user:
            raise HTTPException(
                status_code=404,
                detail='Usuário não encontrado',
            )

        # Buscar confirmação de email
        mail_confirm = df_mail_confirmation.find_one({
            'user_id': str(user['_id']),
            'request_type': 'change_email',
        })

        if (
            not mail_confirm
            or mail_confirm['confirmation_code'] != confirmation_code
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Código inválido',
            )

        # Enviar alerta para email antigo
        alert_result = await send_alert_to_old_mail(
            email, user['name'], new_email
        )
        if not alert_result['success']:
            raise HTTPException(
                status_code=500,
                detail=alert_result['message'],
            )

        # Atualizar email do usuário
        db_users.update_one(
            {'_id': user['_id']}, {'$set': {'email': new_email}}
        )

        # Remover confirmação
        df_mail_confirmation.delete_one({
            'user_id': str(user['_id']),
            'request_type': 'change_email',
        })

        return {'success': True, 'message': 'Email alterado com sucesso'}

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f'Exception: {str(e)}',
        )


@router.get('/users/me/', response_model=User, tags=['users'])
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


@router.post('/searchByEmail', tags=['auth'])
async def search_by_email(
    request: SearchByEmailRequest, db_users=Depends(get_users_collection)
):
    try:
        request = request.model_dump(by_alias=True, exclude_unset=True)
        email = request['email']
        # Procurar por email no banco de dados
        user = db_users.find_one({'email': email})

        if user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Já existe uma conta com esse email',
            )
        response = {'success': True, 'message': 'Não há conta com esse email'}
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.info(str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


async def update_google_password(email: str, new_password: str):
    # Implement the logic to update the password in the user's Google account
    # This is a placeholder function and should be replaced
    # with actual implementation
    return {'success': True, 'message': 'Password updated successfully'}
