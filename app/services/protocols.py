from typing import Any, Protocol


class ImageGenerationServiceProtocol(Protocol):
    """
    Protocolo que define a interface para serviços de geração de imagem.

    Qualquer serviço que implemente este protocolo deve fornecer um método
    `generate_content` com a assinatura especificada.
    """

    async def generate_content(
        self, prompt: str, input_image: bytes | None = None
    ) -> Any:
        """
        Gera conteúdo (imagem) com base em um prompt e uma imagem de entrada
        opcional.

        Args:
            prompt (str): O prompt de texto para guiar a geração.
            input_image (bytes | None): Bytes da imagem de entrada para
                edição ou variação.

        Returns:
            Any: O conteúdo gerado, idealmente os bytes da imagem.
        """
        ...
