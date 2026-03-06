"""
Rotas para gestão de perfil do utilizador, incluindo avatar com IA.
"""

import os
import shutil
from datetime import datetime, timezone

from bson import ObjectId
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
)

from ..database import get_profiles_collection, get_users_collection
from ..dependencies import get_current_active_user
from ..logger import logger
from ..services.image_generation import (
    MEDIA_DIR,
    build_avatar_image_prompt,
    generate_and_save_image,
    improve_image_with_ai,
)
from .schemas import DefautMessage, Profile, ProfileUpdate

router = APIRouter(prefix='/api/profile', tags=['profile'])


async def _get_or_create_profile(user_id: str, user_doc: dict):
    """Busca o perfil do utilizador, criando um vazio se não existir."""
    users_col = get_users_collection()
    profiles_col = get_profiles_collection()

    profile_id = user_doc.get('profile_id')
    if profile_id:
        try:
            profile_doc = await profiles_col.find_one({
                '_id': ObjectId(profile_id)
            })  # noqa: E501
            if profile_doc:
                return profile_doc
        except Exception:
            pass

    # Create an empty profile and link it
    now = datetime.now(timezone.utc)
    new_profile = {
        'name': user_doc.get('name', ''),
        'nickname': '',
        'country': '',
        'state': '',
        'city': '',
        'district': '',
        'deficiency': '',
        'avatar_url': None,
        'email': user_doc.get('email'),
        'phone_number': user_doc.get('phone_number'),
        'created_at': now,
        'updated_at': now,
    }
    result = await profiles_col.insert_one(new_profile)
    new_profile['_id'] = str(result.inserted_id)

    await users_col.update_one(
        {'_id': ObjectId(user_id)},
        {'$set': {'profile_id': str(result.inserted_id)}},
    )

    return new_profile


@router.get('/me', response_model=Profile)
async def get_my_profile(
    current_user=Depends(get_current_active_user),
):
    """Retorna o perfil completo do utilizador autenticado."""
    user_id = str(current_user['_id'])
    profile_doc = await _get_or_create_profile(user_id, current_user)
    profile_doc['_id'] = str(profile_doc['_id'])
    return Profile(**profile_doc)


@router.put('/me', response_model=Profile)
async def update_my_profile(
    data: ProfileUpdate,
    current_user=Depends(get_current_active_user),
    profiles_col=Depends(get_profiles_collection),
):
    """Atualiza os campos do perfil do utilizador."""
    user_id = str(current_user['_id'])
    profile_doc = await _get_or_create_profile(user_id, current_user)

    updates = {k: v for k, v in data.model_dump().items() if v is not None}
    updates['updated_at'] = datetime.now(timezone.utc)

    profile_id = str(profile_doc['_id'])
    await profiles_col.update_one(
        {'_id': ObjectId(profile_id)}, {'$set': updates}
    )
    profile_doc.update(updates)
    profile_doc['_id'] = profile_id
    return Profile(**profile_doc)


@router.post('/me/avatar/generate', response_model=DefautMessage)
async def generate_avatar(
    request: Request,
    background_tasks: BackgroundTasks,
    prompt: str = Form(...),
    current_user=Depends(get_current_active_user),
    profiles_col=Depends(get_profiles_collection),
):
    """Gera um avatar via IA com base num prompt descritivo."""
    user_id = str(current_user['_id'])
    profile_doc = await _get_or_create_profile(user_id, current_user)
    profile_id = str(profile_doc['_id'])

    gemini_client = getattr(request.app.state, 'gemini_webapi_client', None)
    if not gemini_client:
        raise HTTPException(
            status_code=503, detail='Motor de IA não está configurado.'
        )

    full_prompt = build_avatar_image_prompt(prompt)

    async def _generate_and_update():
        avatars_dir = os.path.join(MEDIA_DIR, 'avatars')
        os.makedirs(avatars_dir, exist_ok=True)
        path = await generate_and_save_image(
            prompt=full_prompt,
            output_dir='avatars',
            filename=user_id,
            gemini_client=gemini_client,
            force=True,
        )
        if path:
            abs_url = f'/media/{path}'
            try:
                col = get_profiles_collection()
                await col.update_one(
                    {'_id': ObjectId(profile_id)},
                    {'$set': {'avatar_url': abs_url}},
                )
            except Exception as e:
                logger.error(f'Erro ao atualizar avatar_url: {e}')

    background_tasks.add_task(_generate_and_update)

    return DefautMessage(
        success=True, message='Geração de avatar iniciada em background.'
    )  # noqa: E501


@router.post('/me/avatar/upload', response_model=DefautMessage)
async def upload_avatar(  # noqa: PLR0913, PLR0917
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    improve: bool = Form(False),
    style_prompt: str = Form(''),
    current_user=Depends(get_current_active_user),
    profiles_col=Depends(get_profiles_collection),
):
    """
    Faz upload de uma foto de perfil.
    Se improve=True, aplica uma melhoria de estilo via IA após o upload.
    """
    user_id = str(current_user['_id'])
    profile_doc = await _get_or_create_profile(user_id, current_user)
    profile_id = str(profile_doc['_id'])

    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400, detail='O ficheiro deve ser uma imagem.'
        )

    avatars_dir = os.path.join(MEDIA_DIR, 'avatars')
    os.makedirs(avatars_dir, exist_ok=True)
    dest_path = os.path.join(avatars_dir, f'{user_id}.png')

    with open(dest_path, 'wb') as out:
        shutil.copyfileobj(file.file, out)

    abs_url = f'/media/avatars/{user_id}.png'
    await profiles_col.update_one(
        {'_id': ObjectId(profile_id)},
        {'$set': {'avatar_url': abs_url}},
    )

    # If improvement requested and Gemini available, apply style improvement
    if improve and style_prompt:
        gemini_client = getattr(
            request.app.state, 'gemini_webapi_client', None
        )  # noqa: E501
        if gemini_client:
            base_prompt = (
                'Retrato premium cinematográfico com foco no rosto'  # noqa: E501
            )
            background_tasks.add_task(
                improve_image_with_ai,
                'avatars',
                user_id,
                style_prompt,
                base_prompt,
                gemini_client,
            )

    return DefautMessage(success=True, message='Avatar carregado com sucesso.')


@router.delete('/me/avatar', response_model=DefautMessage)
async def remove_avatar(
    current_user=Depends(get_current_active_user),
    profiles_col=Depends(get_profiles_collection),
):
    """Remove o avatar do utilizador."""
    user_id = str(current_user['_id'])
    profile_doc = await _get_or_create_profile(user_id, current_user)
    profile_id = str(profile_doc['_id'])

    img_path = os.path.join(MEDIA_DIR, 'avatars', f'{user_id}.png')
    if os.path.exists(img_path):
        os.remove(img_path)

    await profiles_col.update_one(
        {'_id': ObjectId(profile_id)},
        {'$set': {'avatar_url': None}},
    )

    return DefautMessage(success=True, message='Avatar removido.')
