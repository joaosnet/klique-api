"""Utilitários compartilhados da aplicação."""


def extract_user_number(sender_id: str | None) -> str | None:
    """
    Extrai o número limpo (sem sufixos) de um sender_id.

    Args:
        sender_id: O ID do remetente no formato WhatsApp
    (ex: '5511999998888@s.whatsapp.net' ou '5511999998888:1@s.whatsapp.net')

    Returns:
        O número limpo (ex: '5511999998888') ou None se sender_id for None
    """
    if not sender_id:
        return None
    return sender_id.split('@')[0].split(':')[0]


def extract_primary_user_number(data: dict) -> str | None:
    """
    Extrai o número de telefone principal a partir de um payload de webhook.

    Ordem de prioridade:
    1. data['sender_id']
    2. data['from']
    3. data['payload']['sender_id']

    Args:
        data: Payload bruto do webhook.

    Returns:
        Número limpo (string) ou None se nada for encontrado.
    """
    candidate = (
        data.get('sender_id')
        or data.get('from')
        or data.get('payload', {}).get('sender_id')
    )
    return extract_user_number(candidate)
