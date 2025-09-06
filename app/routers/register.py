import random
import smtplib
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from http import HTTPStatus

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status

from ..config import ACCESS_TOKEN_EXPIRE_DAYS, GMAIL_EMAIL, GMAIL_PASSWORD
from ..database import get_profiles_collection, get_users_collection
from ..dependencies import (
    create_access_token,
    get_password_hash,
)
from ..logger import logger
from .schemas import (
    Profile,
    RegisterResponse,
    UserCreate,
    UserResponse,
    UserSimplified,
    confirmCodeRequest,
    confirmCodeResponse,
    verifyEmailRequest,
    verifyEmailResponse,
)

router = APIRouter()


@router.post(
    '/auth/register',
    status_code=HTTPStatus.CREATED,
    response_model=RegisterResponse,
    tags=['auth'],
)
async def register(
    user_data: UserCreate,
    db_users=Depends(get_users_collection),
    db_profiles=Depends(get_profiles_collection),
):
    # Verificar se o e-mail já existe
    existing_user = db_users.find_one({'email': user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='E-mail já cadastrado.',
        )

    # Criar perfil
    profile = Profile(
        name=user_data.name,
        nickname=user_data.name,
        country=user_data.country,
        state=user_data.state,
        city=user_data.city,
        district=user_data.district,
        deficiency=user_data.deficiency,
        avatar_url=user_data.avatar_url,
        email=user_data.email,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    new_profile = db_profiles.insert_one(profile.model_dump(exclude={'id'}))

    # Criar usuário
    hashed_password = get_password_hash(user_data.password)
    confirmation_code = str(random.randint(1000, 9999))

    new_user_data = {
        'name': user_data.name,
        'email': user_data.email,
        'password': hashed_password,
        'profile_id': str(new_profile.inserted_id),
        'user_type': 'user',
        'confirmed_code': False,
        'confirmation_code': confirmation_code,
        'created_at': datetime.now(timezone.utc),
        'updated_at': datetime.now(timezone.utc),
    }

    result = db_users.insert_one(new_user_data)
    created_user = db_users.find_one({'_id': result.inserted_id})

    # Enviar e-mail de confirmação (opcional, mas recomendado)
    await send_confirmation_code(
        confirmation_code, created_user['email'], created_user['name']
    )

    # Criar token JWT
    access_token = create_access_token(
        data={'sub': created_user['email']},
        expires_delta=timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS),
    )
    # Instanciação robusta usando model_validate para garantir suporte ao alias
    user_response = UserResponse.model_validate(created_user).model_dump(
        by_alias=True
    )

    user_response['created_at'] = user_response['created_at'].isoformat()
    user_response['updated_at'] = user_response['updated_at'].isoformat()

    return RegisterResponse(
        success=True,
        user=user_response,
        message='Cadastro realizado com sucesso. '
        'Verifique seu e-mail para o código de confirmação.',
        token=access_token,
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

    confirmation_code = str(random.randint(1000, 9999))

    # Criar usuário
    user = {
        'email': email,
        'name': name,
        'user_type': 'user',
        'confirmed_code': False,
        'confirmation_code': confirmation_code,
    }

    result = db_users.insert_one(user)
    created_user = db_users.find_one({'_id': result.inserted_id})

    # Preparar resposta sem confirmation_code
    if not created_user or '_id' not in created_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Erro interno: usuário não encontrado após criação.',
        )

    user_response = UserSimplified(
        _id=str(created_user['_id']),
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

    result = send_confirmation_code(confirmation_code, email, name)
    if result['success']:
        return verifyEmailResponse(
            success=True,
            message='Código enviado ao e-mail',
            user=user_response,
        )
    return result


@router.post(
    '/auth/confirm_code', tags=['auth'], response_model=confirmCodeResponse
)
async def confirm_code(
    request: confirmCodeRequest, db_users=Depends(get_users_collection)
):
    user = db_users.find_one({'_id': ObjectId(request.id)})

    if not user:
        raise HTTPException(
            status_code=404,
            detail='Usuário não encontrado',
        )

    if user['confirmation_code'] != request.confirmation_code:
        raise HTTPException(
            status_code=400,
            detail='Código de confirmação inválido',
        )

    db_users.update_one(
        {'_id': ObjectId(request.id)}, {'$set': {'confirmed_code': True}}
    )

    return confirmCodeResponse(
        success=True, message='Código confirmado com sucesso!'
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
    message.attach(MIMEText(body, 'html', 'utf-8'))

    try:
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()
            server.login(sender_email, password)
            server.send_message(message)
        return {'success': True, 'message': 'email sent'}
    except Exception as e:
        logger.error(f'Failed to send email to {to_email}: {e}')
        return {'success': False, 'message': str(e)}


async def send_confirmation_code(
    confirmation_code: str, user_email: str, user_name: str
):
    subject = 'Código de confirmação de e-mail | Klique'
    body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
            h1 {{ color: #333; }}
            p {{ color: #666; }}
            .code {{ background-color: #e7f3ff; border: 1px solid #007bff; padding: 10px; font-size: 24px; font-weight: bold; text-align: center; border-radius: 4px; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Confirmação de E-mail - Klique</h1>
            <p>Olá, {user_name}!</p>
            <p>Obrigado por se registrar no Klique. Para confirmar seu e-mail, use o código abaixo:</p>
            <div class="code">{confirmation_code}</div>
            <p>Se você não solicitou este código, ignore este e-mail.</p>
            <p>Atenciosamente,<br>Equipe Klique</p>
        </div>
    </body>
    </html>
    """  # noqa: E501
    return await _send_email(user_email, subject, body)


@router.post('/checkAccount', tags=['auth'])
async def check_account(email: str, db=Depends(get_users_collection)):
    user = db.find_one({'email': email})
    if user:
        if not user.get('password'):  # conta incompleta
            db.delete_one({'email': email})
            return False
        return True
    return False
