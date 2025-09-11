from typing import Any, List, Optional

import requests
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)
from langchain_core.outputs import ChatGeneration, ChatResult


class Gpt4FreeChatModel(BaseChatModel):
    """
    Um modelo de chat compatível com LangChain que utiliza um endpoint
    customizado (gpt4free-like).
    """

    def __init__(
        self,
        provider: str = 'LLmArena',
        model: str = 'gpt-5-high',
        api_key: Optional[str] = None,
        **kwargs,
    ):
        super().__init__()
        self.endpoint = (
            f'http://localhost:8080/api/{provider}/chat/completions'
        )
        self.model = model
        self.api_key = api_key
        self.kwargs = kwargs

    @staticmethod
    def _format_messages(messages: List[BaseMessage]) -> List[dict]:
        formatted = []
        for m in messages:
            if isinstance(m, HumanMessage):
                formatted.append({'role': 'user', 'content': m.content})
            elif isinstance(m, AIMessage):
                formatted.append({'role': 'assistant', 'content': m.content})
            elif isinstance(m, SystemMessage):
                formatted.append({'role': 'system', 'content': m.content})
            else:
                formatted.append({'role': 'user', 'content': m.content})
        return formatted

    def _call_api(self, messages: List[dict]) -> str:
        payload = {
            'model': self.model,
            'messages': messages,
        }
        headers = {'Content-Type': 'application/json'}
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        response = requests.post(
            self.endpoint, json=payload, headers=headers, timeout=60
        )
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content']

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> ChatResult:
        formatted = self._format_messages(messages)
        content = self._call_api(formatted)
        gen = ChatGeneration(message=AIMessage(content=content))
        return ChatResult(generations=[gen])

    @property
    def _llm_type(self) -> str:
        return 'gpt4free-chat'
