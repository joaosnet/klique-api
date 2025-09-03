import json
import random
import smtplib
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from http import HTTPStatus
from typing import Annotated

from bson import ObjectId
from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.responses import PlainTextResponse
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from src.config import (
    ACCESS_TOKEN_EXPIRE_DAYS,
    GMAIL_EMAIL,
    GMAIL_PASSWORD,
    GOOGLE_CLIENT_ID,
)
from src.database import (
    get_mail_confirmation_collection,
    get_profiles_collection,
)
from src.dependencies import (
    authenticate_token,
    authenticate_user,
    create_access_token,
    get_current_active_user,
    get_password_hash,
    get_users_collection,
    invalidate_token,
    verify_password,
)

from ..logger import logger
from .schemas import (
    ChangePasswordRequest,
    DefautMessage,
    LoginForm,
    LoginRequest,
    Profile,
    RegisterRequest,
    RegisterResponse,
    RequestChangeEmail,
    SearchByEmailRequest,
    Token,
    User,
    UserResponse,
    UserSimplified,
    ValidToken,
    confirmCodeRequest,
    confirmCodeResponse,
    verifyEmailRequest,
    verifyEmailResponse,
)

router = APIRouter()


@router.post(
    '/auth/login',
    tags=['auth'],
    status_code=status.HTTP_200_OK,
    response_model=LoginForm,
    responses={
        401: {
            'description': 'Código de segurança não confirmado',
            'content': {
                'application/json': {
                    'example': {
                        'success': False,
                        'message': 'Código de segurança não confirmado',
                    }
                }
            },
        }
    },
)
async def login(form_data: LoginForm, db_users=Depends(get_users_collection)):
    try:
        # Verificar se o usuário está cadastrado
        # com o Google usando google-auth
        # Para isso, email é o email do Google e
        # password é o user idToken do Google
        user = await db_users.find_one({'email': form_data.email})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Email não cadastrado',
            )

        try:
            # Verificar o token do Google (recebido no campo password)
            id_info = id_token.verify_oauth2_token(
                form_data.password,
                google_requests.Request(),
                GOOGLE_CLIENT_ID,
            )

            # Verificar se o email do token corresponde ao email da conta
            if id_info.get('email') != user['email']:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail='Token inválido - email não corresponde',
                )

            # Se chegarmos aqui, o token Google é válido
            # Não é necessário verificar a senha neste caso
        except Exception as e:
            logger.error(
                'Erro ao verificar token do Google, verificando senha normal: '
                + str(e)
            )
            # Para contas não-Google, verificar senha normal
            if not verify_password(form_data.password, user['password']):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail='Senha incorreta',
                )

        user_data = User(
            id=user['_id'],
            profile_id=user.get('profile_id', '').encode('utf-8'),
            name=user['name'],
            email=user['email'],
            user_type=user['user_type'],
            confirmed_code=user['confirmed_code'],
            created_at=user.get('created_at', datetime.now(timezone.utc)),
            updated_at=user.get('updated_at', datetime.now(timezone.utc)),
            password=user.get('password', 'Não possui senha'),
        )

        user_data_dict = user_data.model_dump(
            by_alias=True, exclude_unset=True
        )
        user_data_dict['created_at'] = user_data_dict['created_at'].isoformat()
        user_data_dict['updated_at'] = user_data_dict['updated_at'].isoformat()

        access_token = create_access_token(
            data={'sub': user['email']},
            expires_delta=timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS),
        )

        request = LoginRequest(
            success=True,
            user=user_data_dict,
            token=access_token,
            access_token=access_token,
            token_type='bearer',
        ).model_dump(by_alias=True, exclude_unset=True)
        request = json.dumps(request, ensure_ascii=True)

        return PlainTextResponse(
            content=request,
            status_code=status.HTTP_200_OK,
            media_type='application/json',
        )

    except HTTPException:
        # logger.info(str(e),exc_info=True)cl
        raise

    except Exception as e:
        logger.info(str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post(
    '/auth/register',
    status_code=HTTPStatus.CREATED,
    response_model=RegisterResponse,
    tags=['auth'],
)
async def register(
    user: RegisterRequest,
    db_users=Depends(get_users_collection),
    db_profiles=Depends(get_profiles_collection),
):
    try:
        # Criar perfil
        profile = Profile(
            id=user.id,
            name=user.name,
            nickname=user.name,
            country=user.country,
            state=user.state,
            city=user.city,
            district=user.district,
            deficiency=user.deficiency,
            avatar_url=user.avatar_url,
            email=user.email,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        new_profile = await db_profiles.insert_one(
            profile.model_dump(exclude={'id'})
        )

        # Atualizar usuário
        hashed_password = get_password_hash(user.password)
        await db_users.update_one(
            {'_id': ObjectId(user.id)},
            {
                '$set': {
                    'password': hashed_password,
                    'profile_id': str(new_profile.inserted_id),
                }
            },
        )

        user = await db_users.find_one({'_id': ObjectId(user.id)})

        # Criar token JWT
        access_token = create_access_token(
            data={'sub': user['email']},
            expires_delta=timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS),
        )
        user_response = UserResponse(
            id=user['_id'],
            name=user['name'],
            email=user['email'],
            user_type=user['user_type'],
            confirmed_code=user['confirmed_code'],
            confirmation_code=user['confirmation_code'],
            created_at=user.get('created_at', datetime.now(timezone.utc)),
            updated_at=user.get('updated_at', datetime.now(timezone.utc)),
            profile_id=user['profile_id'],
        ).model_dump(by_alias=True, exclude_unset=True)

        user_response['created_at'] = user_response['created_at'].isoformat()
        user_response['updated_at'] = user_response['updated_at'].isoformat()

        request = RegisterResponse(
            success=True,
            user=user_response,
            message='Cadastro realizado com sucesso',
            token=access_token,
        ).model_dump(by_alias=True, exclude_unset=True)
        request = json.dumps(request, ensure_ascii=True)

        return PlainTextResponse(
            content=request,
            status_code=status.HTTP_200_OK,
            media_type='application/json',
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.info(str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/auth/valid_token', tags=['auth'], response_model=ValidToken)
async def valid_token(
    authorization: Annotated[str | None, Header()] = None,
    token_param: str = None,
    db_users=Depends(get_users_collection),
):
    try:
        token = None

        # Try to get token from authorization header
        if authorization:
            if authorization.startswith('Bearer '):
                token = authorization.split(' ')[1]
            else:
                # Use the header value directly if no Bearer prefix
                token = authorization

        # If no token from header, check for token parameter
        if not token and token_param:
            token = token_param

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
        request = json.dumps(request, ensure_ascii=True)

        return PlainTextResponse(
            content=request,
            status_code=status.HTTP_200_OK,
            media_type='application/json',
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f'Unknown error: {e}', exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post('/auth/logout', tags=['auth'], response_model=ValidToken)
async def logout(
    authorization: Annotated[str | None, Header()] = None,
):
    try:
        # Verificar se o token foi fornecido
        # Try to get token from authorization header
        if authorization:
            if authorization.startswith('Bearer '):
                token = authorization.split(' ')[1]
            else:
                # Use the header value directly if no Bearer prefix
                token = authorization

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
        user = await db_users.find_one({'email': email})

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
        await db_users.update_one(
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
        user = await db_users.find_one({'email': email})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Não há conta com esse email',
            )

        # Verificar se o novo email já está cadastrado
        if await check_account(new_email, db=db_users):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Este e-mail já está cadastrado',
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
        await df_mail_confirmation.delete_many({
            'user_id': str(user['_id']),
            'request_type': 'change_email',
        })

        # Criar nova confirmação
        await df_mail_confirmation.insert_one({
            'user_id': str(user['_id']),
            'request_type': 'change_email',
            'confirmation_code': confirmation_code,
            'new_email': new_email,
        })

        # Enviar código por email
        result = await send_confirmation_code(
            confirmation_code, new_email, user['name']
        )

        if not result['success']:
            raise HTTPException(
                status_code=500,
                detail='Erro ao enviar email',
            )

        request = {'success': True, 'message': 'Código enviado para o email'}

        request = json.dumps(request, ensure_ascii=True)
        return PlainTextResponse(
            content=request,
            status_code=status.HTTP_200_OK,
            media_type='application/json',
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f'Exception {str(e)}',
        )


async def send_alert_to_old_mail(
    old_email: str, user_name: str, new_email: str
):
    try:
        smtp_server = 'smtp.gmail.com'
        port = 587
        sender_email = GMAIL_EMAIL
        password = GMAIL_PASSWORD

        message = MIMEMultipart()
        message['From'] = f'KliqueApp <{sender_email}>'
        message['To'] = old_email
        message['Subject'] = 'E-mail alterado | Klique'

        body = f"""Olá, {user_name}! Sua conta teve o endereço de e-mail
        alterado, para entrar você deve utilizar o novo endereço {new_email}.
        Caso você não tenha alterado o e-mail entre em contato conosco."""
        message.attach(MIMEText(body, 'plain', 'utf-8'))

        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()
            server.login(sender_email, password)
            server.send_message(message)

        return {'success': True, 'message': 'email sent'}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


async def send_alert_to_google(email: str, user_name: str):
    try:
        smtp_server = 'smtp.gmail.com'
        port = 587
        sender_email = GMAIL_EMAIL
        password = GMAIL_PASSWORD
        message = MIMEMultipart()
        message['From'] = f'KliqueApp <{sender_email}>'
        message['To'] = email
        message['Subject'] = 'Senha alterada | Klique'
        body = f"""Olá, {user_name}! Sua senha foi alterada com sucesso.
        Caso você não tenha alterado a senha, entre em contato conosco."""
        message.attach(MIMEText(body, 'plain', 'utf-8'))
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()
            server.login(sender_email, password)
            server.send_message(message)
        return {'success': True, 'message': 'email sent'}
    except HTTPException:
        raise
    except Exception as e:
        return {'success': False, 'message': str(e)}


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
        user = await db_users.find_one({'email': email})
        if not user:
            raise HTTPException(
                status_code=404,
                detail='Usuário não encontrado',
            )

        # Buscar confirmação de email
        mail_confirm = await df_mail_confirmation.find_one({
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
        await db_users.update_one(
            {'_id': user['_id']}, {'$set': {'email': new_email}}
        )

        # Remover confirmação
        await df_mail_confirmation.delete_one({
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


@router.get('/auth/user', tags=['auth'], response_model=Token)
async def get_auth_user(
    token: Annotated[Token, Depends(get_current_active_user)],
):
    response = await authenticate_user(token)
    return response


@router.post('/searchByEmail', tags=['auth'])
async def search_by_email(
    request: SearchByEmailRequest, db_users=Depends(get_users_collection)
):
    try:
        request = request.model_dump(by_alias=True, exclude_unset=True)
        email = request['email']
        # Procurar por email no banco de dados
        user = await db_users.find_one({'email': email})

        if user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Já existe uma conta com esse email',
            )
        response = {'success': True, 'message': 'Não há conta com esse email'}
        request = json.dumps(response, ensure_ascii=True)

        return PlainTextResponse(
            content=request,
            status_code=status.HTTP_200_OK,
            media_type='application/json',
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.info(str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post('/checkAccount', tags=['auth'])
async def check_account(email: str, db=Depends(get_users_collection)):
    try:
        user = await db.find_one({'email': email})
        if user:
            if not user.get('password'):  # conta incompleta
                await db.delete_one({'email': email})
                return False
            return True
        return False
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                'success': False,
                'message': f'Erro ao verificar e-mail: {str(e)}',
            },
        )


@router.post(
    '/auth/verifyEmail', tags=['auth'], response_model=verifyEmailResponse
)
async def verify_email(
    request: verifyEmailRequest, db_users=Depends(get_users_collection)
):
    email = request.email
    name = request.name
    google = request.google
    # Verificar conta existente
    if await check_account(email, db=db_users):
        raise HTTPException(
            status_code=409,
            detail={
                'success': False,
                'message': 'E-mail já cadastrado',
            },
        )

    try:
        confirmation_code = str(random.randint(1000, 9999))

        # Criar usuário
        user = {
            'email': email,
            'name': name,
            'user_type': 'user',
            'confirmed_code': False,
            'confirmation_code': confirmation_code,
        }

        result = await db_users.insert_one(user)
        created_user = await db_users.find_one({'_id': result.inserted_id})

        # Preparar resposta sem confirmation_code
        user_response = UserSimplified(
            id=created_user['_id'],
            name=created_user['name'],
            email=created_user['email'],
            confirmed_code=created_user['confirmed_code'],
        )

        if google:
            return verifyEmailResponse(
                success=True,
                message='Código enviado ao e-mail',
                user=user_response,
            )

        result = await send_confirmation_code(confirmation_code, email, name)
        if result['success']:
            return verifyEmailResponse(
                success=True,
                message='Código enviado ao e-mail',
                user=user_response,
            )
        return result

    except Exception as e:
        raise HTTPException(
            status_code=500, detail={'success': False, 'message': str(e)}
        )


async def send_confirmation_code(
    confirmation_code: str, user_email: str, user_name: str
):
    try:
        smtp_server = 'smtp.gmail.com'
        port = 587
        sender_email = GMAIL_EMAIL
        password = GMAIL_PASSWORD

        message = MIMEMultipart()
        message['From'] = f'KliqueApp <{sender_email}>'
        message['To'] = user_email
        message['Subject'] = 'Código de confirmação de e-mail | Klique'

        body = f"""Olá, {user_name}! Seu código de
        confirmação é: {confirmation_code}"""
        message.attach(MIMEText(body, 'plain', 'utf-8'))

        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()
            server.login(sender_email, password)
            server.send_message(message)

        return {'success': True, 'message': 'email sent'}
    except Exception as e:
        return {'success': False, 'message': str(e)}


@router.post(
    '/auth/confirm_code', tags=['auth'], response_model=confirmCodeResponse
)
async def confirm_code(
    request: confirmCodeRequest, db_users=Depends(get_users_collection)
):
    try:
        user = await db_users.find_one({'_id': ObjectId(request.id)})

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Usuário não encontrado',
            )

        if user['confirmation_code'] != request.confirmation_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Código de confirmação inválido',
            )

        await db_users.update_one(
            {'_id': ObjectId(request.id)}, {'$set': {'confirmed_code': True}}
        )

        return confirmCodeResponse(
            success=True, message='Código confirmado com sucesso!'
        )
    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


async def update_google_password(email: str, new_password: str):
    # Implement the logic to update the password in the user's Google account
    # This is a placeholder function and should be replaced
    # with actual implementation
    return {'success': True, 'message': 'Password updated successfully'}
