import random
import smtplib
import uuid
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Annotated

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from webauthn import (
    generate_authentication_options,
    generate_registration_options,
    options_to_json,
    verify_authentication_response,
    verify_registration_response,
)
from webauthn.helpers import base64url_to_bytes
from webauthn.helpers.structs import (
    AttestationConveyancePreference,
    AuthenticatorSelectionCriteria,
    PublicKeyCredentialDescriptor,
    UserVerificationRequirement,
)

from ..config import (
    ACCESS_TOKEN_EXPIRE_DAYS,
    GMAIL_EMAIL,
    GMAIL_PASSWORD,
    GOOGLE_CLIENT_ID,
)
from ..database import (
    get_magic_links_collection,
    get_mail_confirmation_collection,
    get_otp_collection,
    get_profiles_collection,
    get_webauthn_challenges_collection,
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
from ..services.whatsapp import WhatsAppService
from .schemas import (
    AppleLoginRequest,
    ChangePasswordRequest,
    DefautMessage,
    GoogleLoginRequest,
    LazyRegistrationResponse,
    MagicLinkRequest,
    MagicLinkVerifyRequest,
    OTPRequest,
    OTPVerifyRequest,
    PasskeyAuthenticationOptionsResponse,
    PasskeyAuthenticationVerificationRequest,
    PasskeyRegistrationOptionsResponse,
    PasskeyRegistrationVerificationRequest,
    RequestChangeEmail,
    SearchByEmailRequest,
    Token,
    User,
    ValidToken,
)

router = APIRouter()

RP_ID = 'klique.app'  # domain
RP_NAME = 'Klique'


@router.post('/auth/google', response_model=Token, tags=['auth'])
async def google_login(
    request: GoogleLoginRequest,
    db_users=Depends(get_users_collection),
    db_profiles=Depends(get_profiles_collection),
):
    try:
        id_info = id_token.verify_oauth2_token(
            request.token, google_requests.Request(), GOOGLE_CLIENT_ID
        )
        email = id_info.get('email')
        name = id_info.get('name', 'User')
        picture = id_info.get('picture')

        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Email not found in Google token',
            )

        user = await db_users.find_one({'email': email})

        if not user:
            # Auto-register
            profile_data = {
                'name': name,
                'nickname': name,
                'country': 'Brasil',
                'state': '',
                'city': '',
                'district': '',
                'deficiency': 'Nenhuma',
                'avatar_url': picture,
                'email': email,
                'created_at': datetime.now(timezone.utc),
                'updated_at': datetime.now(timezone.utc),
            }
            new_profile = await db_profiles.insert_one(profile_data)

            user_data = {
                'name': name,
                'email': email,
                'profile_id': str(new_profile.inserted_id),
                'user_type': 'user',
                'confirmed_code': True,
                'google_id': id_info.get('sub'),
                'created_at': datetime.now(timezone.utc),
                'updated_at': datetime.now(timezone.utc),
            }
            await db_users.insert_one(user_data)
            user = await db_users.find_one({'email': email})

        access_token_expires = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
        access_token = create_access_token(
            data={'sub': user['email']}, expires_delta=access_token_expires
        )
        return {'access_token': access_token, 'token_type': 'bearer'}

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid Google token',
        )


@router.post('/auth/apple', response_model=Token, tags=['auth'])
async def apple_login(
    request: AppleLoginRequest,
    db_users=Depends(get_users_collection),
    db_profiles=Depends(get_profiles_collection),
):
    # This is a skeleton for Apple Login
    # Mock implementation for demonstration
    email = 'apple-user@example.com'  # Should be extracted from verified token
    name = request.name or 'Apple User'

    user = await db_users.find_one({'email': email})
    if not user:
        profile_data = {
            'name': name,
            'nickname': name,
            'country': 'Brasil',
            'state': '',
            'city': '',
            'district': '',
            'deficiency': 'Nenhuma',
            'email': email,
            'created_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc),
        }
        new_profile = await db_profiles.insert_one(profile_data)

        user_data = {
            'name': name,
            'email': email,
            'profile_id': str(new_profile.inserted_id),
            'user_type': 'user',
            'confirmed_code': True,
            'apple_id': 'apple-sub',  # Should be extracted from verified token
            'created_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc),
        }
        await db_users.insert_one(user_data)
        user = await db_users.find_one({'email': email})

    access_token_expires = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    access_token = create_access_token(
        data={'sub': user['email']}, expires_delta=access_token_expires
    )
    return {'access_token': access_token, 'token_type': 'bearer'}


@router.post('/auth/otp/request', tags=['auth'])
async def request_otp(request: OTPRequest, db_otp=Depends(get_otp_collection)):
    code = str(random.randint(100000, 999999))
    phone = request.phone_number.replace('+', '').replace(' ', '')

    # Save OTP to DB with expiration
    await db_otp.update_one(
        {'phone_number': phone},
        {
            '$set': {
                'code': code,
                'created_at': datetime.now(timezone.utc),
                'expires_at': datetime.now(timezone.utc)
                + timedelta(minutes=5),
            }
        },
        upsert=True,
    )

    if request.method == 'whatsapp':
        ws = WhatsAppService()
        await ws.send_message(
            f'{phone}@s.whatsapp.net',
            f'Seu código de acesso Klique é: {code}',
        )
        await ws.close()
    else:
        # SMS implementation (placeholder)
        logger.info(f'SMS OTP for {phone}: {code}')

    return {'success': True, 'message': 'Código enviado'}


@router.post('/auth/otp/verify', response_model=Token, tags=['auth'])
async def verify_otp(
    request: OTPVerifyRequest,
    db_otp=Depends(get_otp_collection),
    db_users=Depends(get_users_collection),
    db_profiles=Depends(get_profiles_collection),
):
    phone = request.phone_number.replace('+', '').replace(' ', '')
    otp_entry = await db_otp.find_one({
        'phone_number': phone,
        'code': request.code,
    })

    if not otp_entry or otp_entry['expires_at'].replace(
        tzinfo=timezone.utc
    ) < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=400, detail='Código inválido ou expirado'
        )

    # Check if user exists by phone
    user = await db_users.find_one({'phone_number': phone})

    if not user:
        profile_data = {
            'name': f'User {phone[-4:]}',
            'nickname': f'User {phone[-4:]}',
            'country': 'Brasil',
            'state': '',
            'city': '',
            'district': '',
            'deficiency': 'Nenhuma',
            'phone_number': phone,
            'created_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc),
        }
        new_profile = await db_profiles.insert_one(profile_data)

        user_data = {
            'name': profile_data['name'],
            'phone_number': phone,
            'profile_id': str(new_profile.inserted_id),
            'user_type': 'user',
            'confirmed_code': True,
            'created_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc),
        }
        await db_users.insert_one(user_data)
        user = await db_users.find_one({'phone_number': phone})

    await db_otp.delete_one({'phone_number': phone})

    # Use phone as 'sub' if email is missing
    sub = user.get('email') or user.get('phone_number')
    access_token_expires = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    access_token = create_access_token(
        data={'sub': sub}, expires_delta=access_token_expires
    )
    return {'access_token': access_token, 'token_type': 'bearer'}


@router.post('/auth/magic-link/request', tags=['auth'])
async def request_magic_link(
    request: MagicLinkRequest,
    db_magic=Depends(get_magic_links_collection),
):
    token = str(uuid.uuid4())
    email = request.email.lower().strip()

    await db_magic.update_one(
        {'email': email},
        {
            '$set': {
                'token': token,
                'created_at': datetime.now(timezone.utc),
                'expires_at': datetime.now(timezone.utc) + timedelta(hours=1),
            }
        },
        upsert=True,
    )

    magic_url = f'https://klique.app/auth/verify?token={token}'

    await _send_email(
        email,
        'Seu link de acesso Klique',
        f'Clique aqui para entrar: {magic_url}',
    )

    return {'success': True, 'message': 'Link enviado para seu e-mail'}


@router.post('/auth/magic-link/verify', response_model=Token, tags=['auth'])
async def verify_magic_link(
    request: MagicLinkVerifyRequest,
    db_magic=Depends(get_magic_links_collection),
    db_users=Depends(get_users_collection),
    db_profiles=Depends(get_profiles_collection),
):
    magic_entry = await db_magic.find_one({'token': request.token})

    if not magic_entry or magic_entry['expires_at'].replace(
        tzinfo=timezone.utc
    ) < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=400, detail='Link inválido ou expirado'
        )

    email = magic_entry['email']
    user = await db_users.find_one({'email': email})

    if not user:
        profile_data = {
            'name': email.split('@')[0],
            'nickname': email.split('@')[0],
            'country': 'Brasil',
            'state': '',
            'city': '',
            'district': '',
            'deficiency': 'Nenhuma',
            'email': email,
            'created_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc),
        }
        new_profile = await db_profiles.insert_one(profile_data)

        user_data = {
            'name': profile_data['name'],
            'email': email,
            'profile_id': str(new_profile.inserted_id),
            'user_type': 'user',
            'confirmed_code': True,
            'created_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc),
        }
        await db_users.insert_one(user_data)
        user = await db_users.find_one({'email': email})

    await db_magic.delete_one({'token': request.token})

    access_token_expires = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    access_token = create_access_token(
        data={'sub': user['email']}, expires_delta=access_token_expires
    )
    return {'access_token': access_token, 'token_type': 'bearer'}


@router.post(
    '/auth/passkey/register/options',
    response_model=PasskeyRegistrationOptionsResponse,
    tags=['auth'],
)
async def passkey_register_options(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db_challenges=Depends(get_webauthn_challenges_collection),
):
    options = generate_registration_options(
        rp_id=RP_ID,
        rp_name=RP_NAME,
        user_id=str(current_user['_id']).encode(),
        user_name=current_user['email']
        or current_user.get('phone_number', 'User'),
        attestation=AttestationConveyancePreference.DIRECT,
        authenticator_selection=AuthenticatorSelectionCriteria(
            user_verification=UserVerificationRequirement.PREFERRED,
        ),
    )

    registration_id = str(uuid.uuid4())
    await db_challenges.insert_one({
        'registration_id': registration_id,
        'challenge': options.challenge,
        'user_id': str(current_user['_id']),
        'created_at': datetime.now(timezone.utc),
    })

    return {
        'options': options_to_json(options),
        'registration_id': registration_id,
    }


@router.post('/auth/passkey/register/verify', tags=['auth'])
async def passkey_register_verify(
    request: PasskeyRegistrationVerificationRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db_challenges=Depends(get_webauthn_challenges_collection),
    db_users=Depends(get_users_collection),
):
    challenge_entry = await db_challenges.find_one({
        'registration_id': request.registration_id
    })
    if not challenge_entry:
        raise HTTPException(status_code=400, detail='Desafio não encontrado')

    try:
        verification = verify_registration_response(
            credential=request.credential,
            expected_challenge=challenge_entry['challenge'],
            expected_origin=f'https://{RP_ID}',
            expected_rp_id=RP_ID,
        )

        # Save credential to user
        new_credential = {
            'id': verification.credential_id,
            'public_key': verification.credential_public_key,
            'sign_count': verification.sign_count,
            'created_at': datetime.now(timezone.utc),
        }

        await db_users.update_one(
            {'_id': current_user['_id']},
            {'$push': {'webauthn_credentials': new_credential}},
        )

        await db_challenges.delete_one({
            'registration_id': request.registration_id
        })
        return {'success': True}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    '/auth/passkey/authenticate/options',
    response_model=PasskeyAuthenticationOptionsResponse,
    tags=['auth'],
)
async def passkey_authenticate_options(
    email: str,
    db_users=Depends(get_users_collection),
    db_challenges=Depends(get_webauthn_challenges_collection),
):
    user = await db_users.find_one({'email': email})
    if not user:
        raise HTTPException(status_code=404, detail='Usuário não encontrado')

    allow_credentials = []
    for cred in user.get('webauthn_credentials', []):
        allow_credentials.append(PublicKeyCredentialDescriptor(id=cred['id']))

    options = generate_authentication_options(
        rp_id=RP_ID,
        allow_credentials=allow_credentials,
        user_verification=UserVerificationRequirement.PREFERRED,
    )

    authentication_id = str(uuid.uuid4())
    await db_challenges.insert_one({
        'authentication_id': authentication_id,
        'challenge': options.challenge,
        'user_id': str(user['_id']),
        'created_at': datetime.now(timezone.utc),
    })

    return {
        'options': options_to_json(options),
        'authentication_id': authentication_id,
    }


@router.post(
    '/auth/passkey/authenticate/verify', response_model=Token, tags=['auth']
)
async def passkey_authenticate_verify(
    request: PasskeyAuthenticationVerificationRequest,
    db_challenges=Depends(get_webauthn_challenges_collection),
    db_users=Depends(get_users_collection),
):
    challenge_entry = await db_challenges.find_one({
        'authentication_id': request.authentication_id
    })
    if not challenge_entry:
        raise HTTPException(
            status_code=400, detail='Desafio não encontrado/expirado'
        )

    user = await db_users.find_one({
        '_id': ObjectId(challenge_entry['user_id'])
    })
    if not user:
        raise HTTPException(status_code=404, detail='Usuário não encontrado')

    credential_id_bytes = base64url_to_bytes(request.credential.get('id', ''))
    stored_credential = next(
        (
            c
            for c in user.get('webauthn_credentials', [])
            if c['id'] == credential_id_bytes
        ),
        None,
    )

    if not stored_credential:
        raise HTTPException(
            status_code=400, detail='Credencial não encontrada'
        )

    try:
        verification = verify_authentication_response(
            credential=request.credential,
            expected_challenge=challenge_entry['challenge'],
            expected_rp_id=RP_ID,
            expected_origin=f'https://{RP_ID}',
            credential_public_key=stored_credential['public_key'],
            credential_current_sign_count=stored_credential['sign_count'],
        )

        # Update sign count
        await db_users.update_one(
            {
                '_id': user['_id'],
                'webauthn_credentials.id': stored_credential['id'],
            },
            {
                '$set': {
                    'webauthn_credentials.$.sign_count': verification.new_sign_count
                }
            },
        )

        await db_challenges.delete_one({
            'authentication_id': request.authentication_id
        })

        access_token_expires = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
        sub = user.get('email') or user.get('phone_number')
        access_token = create_access_token(
            data={'sub': sub}, expires_delta=access_token_expires
        )
        return {'access_token': access_token, 'token_type': 'bearer'}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    '/auth/lazy', response_model=LazyRegistrationResponse, tags=['auth']
)
async def lazy_registration(
    db_users=Depends(get_users_collection),
    db_profiles=Depends(get_profiles_collection),
):
    # Create an anonymous/temporary user
    temp_id = str(uuid.uuid4())
    name = f'Guest_{temp_id[:8]}'

    profile_data = {
        'name': name,
        'nickname': name,
        'country': 'Brasil',
        'state': '',
        'city': '',
        'district': '',
        'deficiency': 'Nenhuma',
        'created_at': datetime.now(timezone.utc),
        'updated_at': datetime.now(timezone.utc),
    }
    new_profile = await db_profiles.insert_one(profile_data)

    user_data = {
        'name': name,
        'profile_id': str(new_profile.inserted_id),
        'user_type': 'user',
        'is_temporary': True,
        'created_at': datetime.now(timezone.utc),
        'updated_at': datetime.now(timezone.utc),
    }
    result = await db_users.insert_one(user_data)
    user_id = str(result.inserted_id)

    access_token = create_access_token(data={'sub': f'anon_{user_id}'})

    return {
        'access_token': access_token,
        'token_type': 'bearer',
        'user_id': user_id,
    }


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
    access_token_expires = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
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
        user = await db_users.find_one({'email': email})

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
