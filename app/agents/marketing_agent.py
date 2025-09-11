import io
from typing import Optional

import httpx
from langchain.agents import (
    AgentExecutor,
    create_openai_tools_agent,
    tool,
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from PIL import Image, ImageDraw, ImageFont
from pydantic import BaseModel

from app.config import OPENROUTER_API_KEY
from app.services.whatsapp import WhatsAppService

# Constante para tamanho mínimo de número de telefone
MIN_PHONE_LENGTH = 10

llm_marketing = ChatOpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url='https://openrouter.ai/api/v1',
    model='openrouter/sonoma-sky-alpha',
)

whatsapp_service = WhatsAppService()


class ImageGenerationRequest(BaseModel):
    """Modelo para requisição de geração de imagem."""

    prompt: str
    model: Optional[str] = None
    provider: Optional[str] = None
    response_format: Optional[str] = 'url'
    api_key: Optional[str] = None
    proxy: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    num_inference_steps: Optional[int] = None
    seed: Optional[int] = None
    guidance_scale: Optional[float] = None
    aspect_ratio: Optional[str] = None
    n: Optional[int] = 1
    negative_prompt: Optional[str] = None
    resolution: Optional[str] = None
    audio: Optional[dict] = None
    download_media: Optional[bool] = True


class ImageGenerationResponse(BaseModel):
    """Modelo para resposta de geração de imagem."""

    data: list[dict]
    model: str
    provider: str
    created: int


class ModelInfo(BaseModel):
    """Modelo para informações de um modelo de IA."""

    id: str
    object: str
    created: int
    owned_by: str


URL_G4F = 'http://g4f:8080'


@tool
async def listar_modelos_disponiveis() -> str:
    """Lista todos os modelos de IA disponíveis para geração de imagens.

    Returns:
        String com lista dos modelos disponíveis ou erro
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f'{URL_G4F}/v1/models',
                headers={'Content-Type': 'application/json'},
            )
            response.raise_for_status()

        models_data = response.json()

        if not models_data:
            return '❌ Nenhum modelo encontrado.'

        # Processar lista de modelos
        resultado = ['📋 Modelos de IA disponíveis:', '=' * 50]

        for i, model_data in enumerate(models_data, 1):
            model = ModelInfo(**model_data)
            resultado.extend([
                f'{i}. 🤖 Modelo: {model.id}',
                f'   📅 Criado: {model.created}',
                f'   👤 Proprietário: {model.owned_by}',
                f'   🔧 Tipo: {model.object}',
                '',
            ])

        return '\n'.join(resultado)

    except httpx.TimeoutException:
        return '❌ Erro: Timeout ao listar modelos (30s).'
    except httpx.HTTPStatusError as e:
        return f'❌ Erro HTTP {e.response.status_code}: {e.response.text}'
    except httpx.RequestError as e:
        return f'❌ Erro de conexão: {str(e)}'
    except Exception as e:
        return f'❌ Erro inesperado ao listar modelos: {str(e)}'


@tool
async def obter_detalhes_modelo(model_name: str) -> str:
    """Obtém detalhes específicos de um modelo de IA.

    Args:
        model_name: Nome do modelo para consultar detalhes

    Returns:
        String com detalhes do modelo ou erro
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f'{URL_G4F}/v1/models/{model_name}',
                headers={'Content-Type': 'application/json'},
            )
            response.raise_for_status()

        model_data = response.json()
        model = ModelInfo(**model_data)

        resultado = [
            f'🤖 Detalhes do Modelo: {model.id}',
            '=' * 50,
            f'📊 ID: {model.id}',
            f'🔧 Tipo: {model.object}',
            f'📅 Data de criação: {model.created}',
            f'👤 Proprietário: {model.owned_by}',
        ]

        return '\n'.join(resultado)

    except httpx.TimeoutException:
        return f"❌ Erro: Timeout ao consultar modelo '{model_name}' (30s)."
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return f"❌ Modelo '{model_name}' não encontrado."
        return f'❌ Erro HTTP {e.response.status_code}: {e.response.text}'
    except httpx.RequestError as e:
        return f'❌ Erro de conexão: {str(e)}'
    except Exception as e:
        return f'❌ Erro inesperado ao consultar modelo: {str(e)}'


@tool
async def selecionar_melhor_modelo_imagem() -> str:
    """Seleciona automaticamente o melhor modelo disponível para geração de imagens.

    Returns:
        String com o modelo recomendado ou erro
    """
    try:
        # Primeiro, listar todos os modelos disponíveis
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f'{URL_G4F}/v1/models',
                headers={'Content-Type': 'application/json'},
            )
            response.raise_for_status()

        models_data = response.json()

        if not models_data:
            return '❌ Nenhum modelo disponível para seleção.'

        # Critérios de priorização para modelos de imagem (preferências)
        priority_keywords = [
            'flux',  # Modelos Flux são conhecidos por qualidade
            'sdxl',  # Stable Diffusion XL
            'dalle',  # DALL-E da OpenAI
            'midjourney',  # Midjourney
            'stable',  # Stable Diffusion
            'imagen',  # Google Imagen
            'firefly',  # Adobe Firefly
        ]

        models = [ModelInfo(**model_data) for model_data in models_data]

        # Encontrar modelo com maior prioridade
        best_model = None
        best_priority = -1

        for model in models:
            model_id_lower = model.id.lower()

            # Verificar prioridade baseada em palavras-chave
            for i, keyword in enumerate(priority_keywords):
                if keyword in model_id_lower:
                    priority = len(priority_keywords) - i  # Prioridade inversa
                    if priority > best_priority:
                        best_priority = priority
                        best_model = model
                    break

        # Se não encontrou por palavra-chave, usar o primeiro modelo
        if not best_model and models:
            best_model = models[0]

        if not best_model:
            return '❌ Não foi possível selecionar um modelo.'

        resultado = [
            '🎯 Melhor modelo selecionado:',
            '=' * 40,
            f'🤖 Modelo: {best_model.id}',
            f'📅 Criado: {best_model.created}',
            f'👤 Proprietário: {best_model.owned_by}',
            f'🔧 Tipo: {best_model.object}',
            '',
            f"💡 Recomendação: Use '{best_model.id}' para gerar imagens de alta qualidade.",
        ]

        return '\n'.join(resultado)

    except httpx.TimeoutException:
        return '❌ Erro: Timeout ao selecionar modelo (30s).'
    except httpx.HTTPStatusError as e:
        return f'❌ Erro HTTP {e.response.status_code}: {e.response.text}'
    except httpx.RequestError as e:
        return f'❌ Erro de conexão: {str(e)}'
    except Exception as e:
        return f'❌ Erro inesperado ao selecionar modelo: {str(e)}'


@tool
async def gerar_imagem_ai(
    prompt: str,
    model: Optional[str] = None,
    provider: Optional[str] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    aspect_ratio: Optional[str] = None,
    negative_prompt: Optional[str] = None,
    n: Optional[int] = 1,
) -> str:
    """Gera uma imagem usando IA através do endpoint de geração de imagens.

    Args:
        prompt: Descrição da imagem a ser gerada
        model: Modelo específico a ser usado (opcional - se não especificado, seleciona automaticamente o melhor)
        provider: Provedor de IA (opcional)
        width: Largura da imagem (opcional)
        height: Altura da imagem (opcional)
        aspect_ratio: Proporção da imagem (opcional)
        negative_prompt: O que não incluir na imagem (opcional)
        n: Número de imagens a gerar (padrão: 1)

    Returns:
        String com resultado da geração ou erro
    """
    try:
        # Verificar se o serviço está disponível primeiro
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                health_response = await client.get(f'{URL_G4F}/v1/models')
                health_response.raise_for_status()
        except Exception:
            return (
                '❌ Serviço de geração de imagens não está disponível.\n'
                '🔧 Verifique se o serviço está rodando na porta 8080.\n'
                '💡 Como alternativa, posso criar uma imagem placeholder com texto personalizado.'
            )

        # Se modelo não foi especificado, selecionar automaticamente o melhor
        selected_model = model
        if not selected_model:
            try:
                # Listar modelos disponíveis e selecionar o melhor
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(
                        f'{URL_G4F}/v1/models',
                        headers={'Content-Type': 'application/json'},
                    )
                    response.raise_for_status()

                models_data = response.json()

                if models_data:
                    # Critérios de priorização para modelos de imagem
                    priority_keywords = [
                        'flux',
                        'sdxl',
                        'dalle',
                        'midjourney',
                        'stable',
                        'imagen',
                        'firefly',
                    ]

                    models = [
                        ModelInfo(**model_data) for model_data in models_data
                    ]

                    # Encontrar modelo com maior prioridade
                    best_model = None
                    best_priority = -1

                    for model_info in models:
                        model_id_lower = model_info.id.lower()

                        for i, keyword in enumerate(priority_keywords):
                            if keyword in model_id_lower:
                                priority = len(priority_keywords) - i
                                if priority > best_priority:
                                    best_priority = priority
                                    best_model = model_info
                                break

                    # Se não encontrou por palavra-chave, usar o primeiro modelo
                    if not best_model and models:
                        best_model = models[0]

                    if best_model:
                        selected_model = best_model.id

            except Exception as e:
                # Se falhar na seleção automática, continuar sem modelo específico
                pass

        # Preparar payload para a API
        payload = ImageGenerationRequest(
            prompt=prompt,
            model=selected_model,
            provider=provider,
            width=width,
            height=height,
            aspect_ratio=aspect_ratio,
            negative_prompt=negative_prompt,
            n=n,
            response_format='url',
            download_media=True,
        )

        # Converter para dict e remover valores None
        payload_dict = {
            k: v for k, v in payload.model_dump().items() if v is not None
        }

        # Fazer requisição para o endpoint de geração
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f'{URL_G4F}/v1/images/generations',
                json=payload_dict,
                headers={'Content-Type': 'application/json'},
            )
            response.raise_for_status()

        # Processar resposta
        result_data = response.json()
        generation_response = ImageGenerationResponse(**result_data)

        # Extrair informações da resposta
        images_info = []
        for i, image_data in enumerate(generation_response.data):
            image_info = {
                'indice': i + 1,
                'url': image_data.get('url', ''),
                'prompt_revisado': image_data.get('revised_prompt', ''),
                'base64': 'disponível'
                if image_data.get('b64_json')
                else 'não disponível',
            }
            images_info.append(image_info)

        # Formattar resposta
        resultado = [
            f'✅ Geração de imagem concluída com sucesso!',
            f'📊 Modelo: {generation_response.model}'
            + (f' (selecionado automaticamente)' if not model else ''),
            f'🏢 Provedor: {generation_response.provider}',
            f'🕐 Timestamp: {generation_response.created}',
            f'🖼️ Imagens geradas: {len(generation_response.data)}',
            '',
            '📋 Detalhes das imagens:',
        ]

        for img_info in images_info:
            resultado.extend([
                f'  {img_info["indice"]}. URL: {img_info["url"]}',
                f'     Prompt revisado: {img_info["prompt_revisado"][:100]}...'
                if len(img_info['prompt_revisado']) > 100
                else f'     Prompt revisado: {img_info["prompt_revisado"]}',
                f'     Base64: {img_info["base64"]}',
                '',
            ])

        return '\n'.join(resultado)

    except httpx.TimeoutException:
        return '❌ Erro: Timeout na geração da imagem. O processo demorou mais de 60 segundos.'
    except httpx.HTTPStatusError as e:
        return f'❌ Erro HTTP {e.response.status_code}: {e.response.text}'
    except httpx.RequestError as e:
        return (
            f'❌ Erro de conexão: {str(e)}\n'
            '🔧 Verifique se o serviço de geração de imagens está rodando na porta 8080.\n'
            '💡 Como alternativa, posso criar uma imagem placeholder com texto personalizado.'
        )
    except Exception as e:
        return f'❌ Erro inesperado na geração de imagem: {str(e)}'


@tool
async def enviar_mensagem_whatsapp(phone_number: str, message: str) -> str:
    """Envia uma mensagem de texto para um número de telefone específico no
    WhatsApp."""
    try:
        message_id = await whatsapp_service.send_message(phone_number, message)
        if message_id:
            return (
                f'Mensagem enviada com sucesso para {phone_number}. '
                f'ID da mensagem: {message_id}'
            )

        # Verifica se o usuário existe no WhatsApp antes de declarar falha
        user_check = await whatsapp_service.check_user(phone_number)
        if user_check and not user_check.get('on_whatsapp'):
            return f'O número {phone_number} não está ativo no WhatsApp.'

        return (
            f'Falha ao enviar mensagem para {phone_number}. O número pode '
            'estar temporariamente indisponível ou há um problema na conexão.'
        )
    except Exception as e:
        return f'Ocorreu um erro ao enviar mensagem: {e}'


@tool
async def postar_status_whatsapp(
    caption: str, image_url: str | None = None
) -> str:
    """Posta uma imagem como uma atualização de status no WhatsApp. A imagem
    pode ser gerada ou vir de uma URL."""
    try:
        image_bytes = b''
        if image_url:
            # Lógica para baixar a imagem da URL
            try:
                response = httpx.get(image_url, follow_redirects=True)
                response.raise_for_status()
                image_bytes = response.content
            except httpx.RequestError as e:
                return f'Erro ao baixar a imagem da URL: {e}'

        if not image_bytes:
            # Cria uma imagem de placeholder com o texto da legenda
            img = Image.new('RGB', (1080, 1920), color='black')
            draw = ImageDraw.Draw(img)
            try:
                font = ImageFont.truetype('arial.ttf', size=80)
            except IOError:
                font = ImageFont.load_default(size=80)

            # Centraliza o texto
            text_bbox = draw.textbbox((0, 0), caption, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            position = (
                (img.width - text_width) / 2,
                (img.height - text_height) / 2,
            )
            draw.text(position, caption, fill='white', font=font)

            byte_arr = io.BytesIO()
            img.save(byte_arr, format='PNG')
            image_bytes = byte_arr.getvalue()

        status_id = await whatsapp_service.post_status_update(
            image_bytes, caption
        )
        if status_id:
            return f'Status postado com sucesso. ID do status: {status_id}'
        return 'Falha ao postar status.'
    except Exception as e:
        return f'Ocorreu um erro ao postar o status: {e}'


@tool
async def enviar_link_whatsapp(
    phone_number: str, url: str, caption: str = ''
) -> str:
    """Envia um link com preview para um número de telefone específico no
    WhatsApp."""
    try:
        message_id = await whatsapp_service.send_link(
            phone_number, url, caption
        )
        if message_id:
            return (
                f'Link enviado com sucesso para {phone_number}. '
                f'ID da mensagem: {message_id}'
            )
        return f'Falha ao enviar link para {phone_number}.'
    except Exception as e:
        return f'Ocorreu um erro ao enviar link: {e}'


@tool
async def criar_grupo_whatsapp(name: str, participants: list[str]) -> str:
    """Cria um novo grupo no WhatsApp com um nome e uma lista de
    participantes."""
    try:
        result = await whatsapp_service.create_group(name, participants)
        if result and result.get('id'):
            return (
                f"Grupo '{name}' criado com sucesso. "
                f'ID do grupo: {result.get("id")}'
            )
        return f"Falha ao criar o grupo '{name}'. Resposta: {result}"
    except Exception as e:
        return f'Ocorreu um erro ao criar o grupo: {e}'


@tool
async def reagir_a_mensagem(message_id: str, reaction: str) -> str:
    """Reage a uma mensagem específica com um emoji."""
    try:
        success = await whatsapp_service.react_message(message_id, reaction)
        if success:
            return f'Reação "{reaction}" enviada para a mensagem {message_id}.'
        return f'Falha ao reagir à mensagem {message_id}.'
    except Exception as e:
        return f'Ocorreu um erro ao reagir à mensagem: {e}'


@tool
async def verificar_usuario_whatsapp(phone_number: str) -> str:
    """Verifica se um número de telefone pertence a um usuário válido no
    WhatsApp."""
    try:
        # Limpar o número removendo caracteres não numéricos exceto +
        numero_limpo = ''.join(
            c for c in phone_number if c.isdigit() or c == '+'
        )

        # Se começar com +, manter, senão tentar com código do país
        if not numero_limpo.startswith('+'):
            if numero_limpo.startswith('55'):
                numero_limpo = '+' + numero_limpo
            elif len(numero_limpo) >= MIN_PHONE_LENGTH:
                numero_limpo = '+55' + numero_limpo

        result = await whatsapp_service.check_user(numero_limpo)
        if result and result.get('on_whatsapp'):
            return f'O número {numero_limpo} está no WhatsApp.'

        # Tentar também sem o código do país se falhou
        if numero_limpo.startswith('+55'):
            numero_sem_codigo = numero_limpo[3:]
            result2 = await whatsapp_service.check_user(numero_sem_codigo)
            if result2 and result2.get('on_whatsapp'):
                return f'O número {numero_sem_codigo} está no WhatsApp.'

        return f'O número {phone_number} não foi encontrado no WhatsApp.'
    except Exception as e:
        return f'Ocorreu um erro ao verificar o usuário: {e}'


@tool
async def obter_info_grupo(group_id: str) -> str:
    """Obtém informações detalhadas de um grupo do WhatsApp."""
    try:
        info = await whatsapp_service.get_group_info(group_id)
        if info:
            return f'Informações do grupo {group_id}: {info}'
        return f'Falha ao obter informações do grupo {group_id}.'
    except Exception as e:
        return f'Ocorreu um erro ao obter informações do grupo: {e}'


@tool
async def sair_do_grupo(group_id: str) -> str:
    """Sai de um grupo do WhatsApp."""
    try:
        success = await whatsapp_service.leave_group(group_id)
        if success:
            return f'Você saiu do grupo {group_id}.'
        return f'Falha ao sair do grupo {group_id}.'
    except Exception as e:
        return f'Ocorreu um erro ao sair do grupo: {e}'


@tool
async def adicionar_participantes_grupo(
    group_id: str, participants: list[str]
) -> str:
    """Adiciona participantes a um grupo do WhatsApp."""
    try:
        success = await whatsapp_service.add_group_participants(
            group_id, participants
        )
        if success:
            return f'Participantes adicionados ao grupo {group_id}.'
        return f'Falha ao adicionar participantes ao grupo {group_id}.'
    except Exception as e:
        return f'Ocorreu um erro ao adicionar participantes: {e}'


@tool
async def remover_participantes_grupo(
    group_id: str, participants: list[str]
) -> str:
    """Remove participantes de um grupo do WhatsApp."""
    try:
        success = await whatsapp_service.remove_group_participants(
            group_id, participants
        )
        if success:
            return f'Participantes removidos do grupo {group_id}.'
        return f'Falha ao remover participantes do grupo {group_id}.'
    except Exception as e:
        return f'Ocorreu um erro ao remover participantes: {e}'


@tool
async def promover_participante_grupo(group_id: str, participant: str) -> str:
    """Promove um participante a administrador do grupo."""
    try:
        success = await whatsapp_service.promote_group_participant(
            group_id, participant
        )
        if success:
            return f'{participant} promovido a admin no grupo {group_id}.'
        return f'Falha ao promover {participant} no grupo {group_id}.'
    except Exception as e:
        return f'Ocorreu um erro ao promover participante: {e}'


@tool
async def rebaixar_participante_grupo(group_id: str, participant: str) -> str:
    """Rebaixa um administrador a participante comum."""
    try:
        success = await whatsapp_service.demote_group_participant(
            group_id, participant
        )
        if success:
            return (
                f'{participant} rebaixado a membro comum no grupo {group_id}.'
            )
        return f'Falha ao rebaixar {participant} no grupo {group_id}.'
    except Exception as e:
        return f'Ocorreu um erro ao rebaixar participante: {e}'


@tool
async def revogar_mensagem(message_id: str) -> str:
    """Revoga (apaga para todos) uma mensagem enviada."""
    try:
        success = await whatsapp_service.revoke_message(message_id)
        if success:
            return f'Mensagem {message_id} revogada com sucesso.'
        return f'Falha ao revogar a mensagem {message_id}.'
    except Exception as e:
        return f'Ocorreu um erro ao revogar a mensagem: {e}'


@tool
async def marcar_como_lida(message_id: str) -> str:
    """Marca uma mensagem como lida."""
    try:
        success = await whatsapp_service.read_message(message_id)
        if success:
            return f'Mensagem {message_id} marcada como lida.'
        return f'Falha ao marcar a mensagem {message_id} como lida.'
    except Exception as e:
        return f'Ocorreu um erro ao marcar a mensagem como lida: {e}'


@tool
async def listar_chats() -> str:
    """Retorna a lista de todos os chats abertos."""
    try:
        chats = await whatsapp_service.get_chats()
        if chats:
            return f'Chats encontrados: {chats}'
        return 'Nenhum chat encontrado.'
    except Exception as e:
        return f'Ocorreu um erro ao listar os chats: {e}'


@tool
async def obter_mensagens_chat(chat_jid: str) -> str:
    """Obtém as mensagens de um chat específico pelo seu JID."""
    try:
        messages = await whatsapp_service.get_chat_messages(chat_jid)
        if messages:
            return f'Mensagens do chat {chat_jid}: {messages}'
        return f'Nenhuma mensagem encontrada para o chat {chat_jid}.'
    except Exception as e:
        return f'Ocorreu um erro ao obter as mensagens do chat: {e}'


@tool
async def listar_contatos_whatsapp() -> str:
    """Retorna a lista de todos os contatos do usuário no WhatsApp."""
    try:
        contacts = await whatsapp_service.get_my_contacts()
        if contacts:
            return f'Contatos encontrados: {contacts}'
        return 'Nenhum contato encontrado.'
    except Exception as e:
        return f'Ocorreu um erro ao listar os contatos: {e}'


@tool
async def buscar_contato_por_nome(nome: str) -> str:
    """Busca um contato específico pelo nome (busca parcial,
    case-insensitive)."""
    try:
        contacts = await whatsapp_service.get_my_contacts()
        if not contacts:
            return 'Nenhum contato encontrado.'

        nome_lower = nome.lower()
        contatos_encontrados = []

        for contact in contacts:
            contact_name = contact.get('name', '').lower()
            if nome_lower in contact_name:
                # Extrair número do JID (ex: '5511999998888' de
                # '5511999998888@s.whatsapp.net')
                jid = contact.get('jid', '')
                numero = jid.split('@')[0].split(':')[0]
                contatos_encontrados.append({
                    'nome': contact.get('name', ''),
                    'numero': numero,
                    'jid': jid,
                })

        if contatos_encontrados:
            return (
                f'Contatos encontrados para "{nome}": {contatos_encontrados}'
            )
        return f'Nenhum contato encontrado com o nome "{nome}".'

    except Exception as e:
        return f'Ocorreu um erro ao buscar o contato: {e}'


@tool
async def obter_info_usuario() -> str:
    """Obtém as informações do perfil do usuário logado no WhatsApp."""
    try:
        info = await whatsapp_service.get_user_info()
        if info:
            return f'Informações do usuário: {info}'
        return 'Falha ao obter informações do usuário.'
    except Exception as e:
        return f'Ocorreu um erro ao obter as informações do usuário: {e}'


@tool
async def alterar_nome_exibicao(novo_nome: str) -> str:
    """Altera o nome de exibição (PushName) do usuário no WhatsApp."""
    try:
        success = await whatsapp_service.change_pushname(novo_nome)
        if success:
            return f'Nome de exibição alterado para "{novo_nome}".'
        return 'Falha ao alterar o nome de exibição.'
    except Exception as e:
        return f'Ocorreu um erro ao alterar o nome de exibição: {e}'


@tool
async def alterar_avatar(image_url: str) -> str:
    """Altera a foto de perfil (avatar) do usuário a partir de uma URL de
    imagem."""
    try:
        response = httpx.get(image_url, follow_redirects=True)
        response.raise_for_status()
        image_bytes = response.content
        success = await whatsapp_service.change_avatar(image_bytes)
        if success:
            return 'Foto de perfil alterada com sucesso.'
        return 'Falha ao alterar a foto de perfil.'
    except Exception as e:
        return f'Ocorreu um erro ao alterar a foto de perfil: {e}'


def create_marketing_agent():
    tools = [
        enviar_mensagem_whatsapp,
        postar_status_whatsapp,
        enviar_link_whatsapp,
        criar_grupo_whatsapp,
        reagir_a_mensagem,
        verificar_usuario_whatsapp,
        obter_info_grupo,
        sair_do_grupo,
        adicionar_participantes_grupo,
        remover_participantes_grupo,
        promover_participante_grupo,
        rebaixar_participante_grupo,
        revogar_mensagem,
        marcar_como_lida,
        listar_chats,
        obter_mensagens_chat,
        listar_contatos_whatsapp,
        buscar_contato_por_nome,
        obter_info_usuario,
        alterar_nome_exibicao,
        listar_modelos_disponiveis,
        obter_detalhes_modelo,
        selecionar_melhor_modelo_imagem,
        alterar_avatar,
    ]
    prompt = ChatPromptTemplate.from_messages([
        (
            'system',
            'Você é um agente de marketing e gerenciador de comunidades no '
            'WhatsApp. Você pode enviar mensagens, links, status, gerenciar '
            'grupos (criar, sair, adicionar/remover/promover/rebaixar '
            'participantes), gerenciar mensagens (revogar, marcar como lida, '
            'listar chats e obter mensagens), listar e buscar contatos, '
            'gerenciar perfil (obter informações do usuário, alterar nome de '
            'exibição e foto de perfil) e GERAR IMAGENS usando IA. '
            'FUNCIONALIDADES DE IA: '
            '1. "listar_modelos_disponiveis" - lista todos os modelos de IA disponíveis '
            '2. "obter_detalhes_modelo" - obtém detalhes de um modelo específico '
            '3. "selecionar_melhor_modelo_imagem" - seleciona automaticamente o melhor modelo '
            '4. "gerar_imagem_ai" - gera imagens (seleciona automaticamente o melhor modelo se não especificado) '
            'IMPORTANTE: Se o serviço de IA não estiver disponível (erro de conexão), '
            'NÃO tente múltiplas vezes as funções de IA. Em vez disso, informe que o serviço '
            'não está disponível e ofereça alternativas como criar imagens placeholder com texto. '
            'Para gerar imagens quando o serviço estiver disponível, use "gerar_imagem_ai" com um prompt descritivo. '
            'Quando precisar buscar um contato por nome, use "buscar_contato_por_nome" '
            'em vez de listar todos os contatos. Para verificar se um número existe no WhatsApp, '
            'use "verificar_usuario_whatsapp". Seja eficiente e não repita ferramentas que falharam.',
        ),
        MessagesPlaceholder(variable_name='chat_history'),
        ('user', '{input}'),
        MessagesPlaceholder(variable_name='agent_scratchpad'),
    ])
    agent = create_openai_tools_agent(llm_marketing, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    return executor
