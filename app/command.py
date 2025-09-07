# -*- coding: utf-8 -*-
"""
Módulo de parsing e modelagem de comandos de chat (sem prefixo '/').

Comandos V1 (palavra inicial, case-insensitive):
  legenda <novo texto>        -> Atualiza legenda repostando mesma imagem
  refazer                     -> Regenera imagem usando o último prompt
  editar <instruções>         -> Edição (image-to-image) sobre a última imagem gerada
  imagem <novo prompt>        -> Nova geração (fluxo padrão)
  ajuda                       -> Exibe ajuda

Observações:
- Comandos não precisam de barra.
- 'refazer' e 'ajuda' podem vir sozinhos (sem argumento adicional).
- Para 'legenda', se não houver argumento retorna erro amigável.
- Para 'editar', se não houver instruções o handler pode retornar ajuda específica.
- Parser é tolerante a múltiplos espaços e capitalização.

Futuras extensões (V2):
- variantes, estilo, histórico, undo, alias curtos, etc.
"""  # noqa: E501

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class CommandOperation(Enum):
    LEGENDA = auto()
    REFAZER = auto()
    EDITAR = auto()
    IMAGEM = auto()
    AJUDA = auto()


@dataclass
class CommandContext:
    operation: CommandOperation
    argument: str  # Texto restante após a palavra-chave (pode ser vazio)
    raw_text: str

    @property
    def requires_argument(self) -> bool:
        return self.operation in {
            CommandOperation.LEGENDA,
            CommandOperation.EDITAR,
            CommandOperation.IMAGEM,
        }


HELP_MESSAGE = (
    '📘 *Ajuda - Comandos Klique*\n'
    '\n'
    '*imagem <prompt>*\n'
    '  Gera nova imagem e publica também no status.\n'
    '  Ex: imagem gato astronauta neon estilo vaporwave\n'
    '\n'
    '*refazer*\n'
    '  Regenera a última imagem usando o mesmo prompt (variação).\n'
    '\n'
    '*editar <instruções>*\n'
    '  Edita a última imagem gerada. Ex: editar adicionar brilhos roxos no fundo\n'  # noqa: E501
    '\n'
    '*legenda <texto>*\n'
    '  Atualiza a legenda/status da última imagem sem regenerar.\n'
    '\n'
    '*ajuda*\n'
    '  Mostra esta mensagem.\n'
    '\n'
    "Se aparecer: 'Nenhuma imagem anterior encontrada. Envie: imagem <prompt>' "  # noqa: E501
    'gere uma imagem primeiro.\n'
)


# Map de palavras-chave principais para operação
_KEYWORD_MAP = {
    'legenda': CommandOperation.LEGENDA,
    'refazer': CommandOperation.REFAZER,
    'editar': CommandOperation.EDITAR,
    'imagem': CommandOperation.IMAGEM,
    'ajuda': CommandOperation.AJUDA,
}


def parse_command(text: str | None) -> CommandContext | None:
    """
    Analisa o texto bruto e identifica se é um comando suportado.

    Regras:
    - Ignora espaços em branco no começo/fim.
    - Se primeira palavra está em _KEYWORD_MAP retornamos CommandContext.
    - Argumento é tudo que vem após a primeira palavra (strip()).
    - Retorna None se não identificar comando.
    """
    if not text:
        return None

    raw = text.strip()
    if not raw:
        return None

    parts = raw.split()
    keyword = parts[0].lower()

    operation = _KEYWORD_MAP.get(keyword)
    if not operation:
        return None

    argument = raw[len(parts[0]) :].strip()

    return CommandContext(operation=operation, argument=argument, raw_text=raw)


__all__ = [
    'CommandOperation',
    'CommandContext',
    'parse_command',
    'HELP_MESSAGE',
]
