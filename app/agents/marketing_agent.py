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

from app.config import OPENROUTER_API_KEY
from app.services.gemini_webapi_service import GeminiWebApiService
from app.services.whatsapp import WhatsAppService

# Constante para tamanho mínimo de número de telefone
MIN_PHONE_LENGTH = 10

llm_marketing = ChatOpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url='https://openrouter.ai/api/v1',
    model='openrouter/sonoma-sky-alpha',
)

whatsapp_service = WhatsAppService()
gemini_webapi_service = GeminiWebApiService()


@tool
async def gerar_ou_editar_imagem(
    user_number: str,
    prompt: str,
    image_bytes: Optional[bytes] = None,
    enhance_prompt: bool = True,
) -> str:
    """
    Gera ou edita uma imagem usando o Gemini Web API Service e envia automaticamente para o usuário.

    Args:
        user_number: O número de telefone do usuário para manter a sessão.
        prompt: A descrição da imagem a ser gerada ou da edição a ser feita.
        image_bytes: Os bytes da imagem a ser editada (opcional).
        enhance_prompt: Se o prompt deve ser melhorado antes da geração (padrão: True).

    Returns:
        String com o resultado da operação (geração + envio).
    """
    try:
        chat_session = await gemini_webapi_service.get_or_create_chat(
            user_number
        )
        final_prompt = prompt
        if enhance_prompt:
            # Esta é uma simplificação. A lógica real de enhancement pode ser mais complexa.
            final_prompt = f'Aprimore e gere uma imagem com base em: {prompt}'

        input_images = [image_bytes] if image_bytes else None
        generated_images = (
            await gemini_webapi_service.generate_content_from_chat(
                prompt=final_prompt,
                chat=chat_session,
                input_images=input_images,
            )
        )

        if not generated_images:
            return '❌ Não foi possível gerar a imagem.'

        # Envia a imagem gerada diretamente para o usuário
        generated_image_bytes = generated_images[0]
        image_message_id = await whatsapp_service.send_image_message(
            user_number, generated_image_bytes, f'Imagem gerada: {prompt}'
        )
        
        if not image_message_id:
            return f'✅ Imagem gerada mas houve problema no envio. Prompt: "{prompt}"'

        return f'✅ Imagem gerada e enviada com sucesso! ID da mensagem: {image_message_id}. Prompt: "{prompt}"'

    except Exception as e:
        return f'❌ Erro ao gerar ou editar imagem: {e}'


@tool
async def gerar_legenda_criativa(user_number: str, image_prompt: str) -> str:
    """
    Gera uma legenda criativa para uma imagem usando a sessão de chat do usuário.

    Args:
        user_number: O número de telefone do usuário para obter a sessão de chat correta.
        image_prompt: O prompt usado para gerar a imagem.

    Returns:
        String com a legenda gerada ou uma mensagem de erro.
    """
    try:
        chat_session = await gemini_webapi_service.get_or_create_chat(
            user_number
        )
        caption = await gemini_webapi_service.generate_status_caption(
            chat=chat_session, image_prompt=image_prompt
        )

        if caption:
            return f'✅ Legenda gerada: "{caption}"'
        return '❌ Não foi possível gerar a legenda.'

    except Exception as e:
        return f'❌ Erro ao gerar legenda: {e}'


@tool
async def enviar_imagem_e_postar_status(
    user_number: str,
    image_bytes: bytes,
    caption: str,
    prompt: str
) -> str:
    """
    Envia uma imagem para o usuário e posta a mesma imagem como status do WhatsApp.

    Args:
        user_number: O número de telefone do usuário.
        image_bytes: Os bytes da imagem a ser enviada.
        caption: Legenda para o status.
        prompt: O prompt original usado para gerar a imagem.

    Returns:
        String com o resultado das operações.
    """
    try:
        # Envia imagem para o usuário
        image_message_id = await whatsapp_service.send_image_message(
            user_number, image_bytes, f'Imagem gerada: {prompt}'
        )
        
        # Posta como status
        status_id = await whatsapp_service.post_status_update(
            image_bytes, caption
        )
        
        results = []
        if image_message_id:
            results.append(f'✅ Imagem enviada para o usuário (ID: {image_message_id})')
        else:
            results.append('❌ Falha ao enviar imagem para o usuário')
            
        if status_id:
            results.append(f'✅ Status postado com sucesso (ID: {status_id})')
        else:
            results.append('❌ Falha ao postar status')
            
        return ' | '.join(results)

    except Exception as e:
        return f'❌ Erro ao enviar imagem e postar status: {e}'


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


def create_marketing_agent(user_context: dict = None):
    if user_context is None:
        user_context = {}
    
    user_number = user_context.get('user_number', '559184497318')
    
    # Cria versões contextualizadas das tools de geração de imagem
    @tool
    async def gerar_ou_editar_imagem_contextualizada(
        prompt: str,
        image_bytes: Optional[bytes] = None,
        enhance_prompt: bool = True,
    ) -> str:
        """
        Gera ou edita uma imagem usando o Gemini Web API Service e envia automaticamente para o usuário.
        O número do usuário é obtido automaticamente do contexto.
        """
        return await gerar_ou_editar_imagem(user_number, prompt, image_bytes, enhance_prompt)
    
    @tool
    async def gerar_legenda_criativa_contextualizada(image_prompt: str) -> str:
        """
        Gera uma legenda criativa para uma imagem usando a sessão de chat do usuário.
        O número do usuário é obtido automaticamente do contexto.
        """
        return await gerar_legenda_criativa(user_number, image_prompt)
    
    @tool
    async def enviar_imagem_e_postar_status_contextualizada(
        image_bytes: bytes,
        caption: str,
        prompt: str
    ) -> str:
        """
        Envia uma imagem para o usuário e posta a mesma imagem como status do WhatsApp.
        O número do usuário é obtido automaticamente do contexto.
        """
        return await enviar_imagem_e_postar_status(user_number, image_bytes, caption, prompt)
    
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
        alterar_avatar,
        gerar_ou_editar_imagem_contextualizada,
        gerar_legenda_criativa_contextualizada,
        enviar_imagem_e_postar_status_contextualizada,
    ]
    
    prompt = ChatPromptTemplate.from_messages([
        (
            'system',
            f'Você é um agente de marketing e gerenciador de comunidades no '
            'WhatsApp. Você pode enviar mensagens, links, status, gerenciar '
            'grupos, mensagens, contatos e perfil. '
            f'CONTEXTO DO USUÁRIO ATUAL: {user_number} '
            'FUNCIONALIDADES DE IA: '
            '1. "gerar_ou_editar_imagem_contextualizada": Gera uma nova imagem a partir de um prompt e envia automaticamente para o usuário atual. '
            '   - `prompt` é a descrição do que fazer. '
            '   - `image_bytes` é usado para edição (opcional). '
            '   - `enhance_prompt` pode ser usado para melhorar a descrição (opcional). '
            '2. "gerar_legenda_criativa_contextualizada": Cria uma legenda para uma imagem recém-gerada. '
            '   - `image_prompt` é o prompt original da imagem. '
            '3. "enviar_imagem_e_postar_status_contextualizada": Envia uma imagem para o usuário E posta como status simultaneamente. '
            '   - `image_bytes`, `caption` e `prompt` são obrigatórios. '
            'FLUXO RECOMENDADO PARA GERAÇÃO DE IMAGENS: '
            '1. Use "gerar_ou_editar_imagem_contextualizada" para gerar e enviar a imagem para o usuário '
            '2. Use "gerar_legenda_criativa_contextualizada" para criar uma legenda '
            '3. Use "enviar_imagem_e_postar_status_contextualizada" para postar a mesma imagem como status '
            'IMPORTANTE: O número do usuário está automaticamente configurado no contexto. '
            'Seja eficiente e não repita ferramentas que falharam.',
        ),
        MessagesPlaceholder(variable_name='chat_history'),
        ('user', '{input}'),
        MessagesPlaceholder(variable_name='agent_scratchpad'),
    ])
    agent = create_openai_tools_agent(llm_marketing, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    return executor
