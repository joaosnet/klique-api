import io

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
from app.services.whatsapp import WhatsAppService

# Constante para tamanho mínimo de número de telefone
MIN_PHONE_LENGTH = 10

llm_marketing = ChatOpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url='https://openrouter.ai/api/v1',
    model='openrouter/sonoma-sky-alpha',
)

whatsapp_service = WhatsAppService()


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
                f"ID do grupo: {result.get('id')}"
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
        alterar_avatar,
    ]
    prompt = ChatPromptTemplate.from_messages([
        (
            'system',
            'Você é um agente de marketing e gerenciador de comunidades no '
            'WhatsApp. Você pode enviar mensagens, links, status, gerenciar '
            'grupos (criar, sair, adicionar/remover/promover/rebaixar '
            'participantes), gerenciar mensagens (revogar, marcar como lida, '
            'listar chats e obter mensagens), listar e buscar contatos e '
            'gerenciar perfil (obter informações do usuário, alterar nome de '
            'exibição e foto de perfil). IMPORTANTE: Quando precisar buscar '
            'um contato por nome, use a ferramenta "buscar_contato_por_nome" '
            'em vez de listar todos os contatos. Para verificar se um número '
            'existe no WhatsApp, use "verificar_usuario_whatsapp". Use as '
            'ferramentas disponíveis para executar essas ações de forma '
            'eficiente.',
        ),
        MessagesPlaceholder(variable_name='chat_history'),
        ('user', '{input}'),
        MessagesPlaceholder(variable_name='agent_scratchpad'),
    ])
    agent = create_openai_tools_agent(llm_marketing, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    return executor
