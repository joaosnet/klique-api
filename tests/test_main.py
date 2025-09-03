import io
import sys
from pathlib import Path

from fastapi import status
from fastapi.testclient import TestClient
from PIL import Image

sys.path.append(str(Path(__file__).parent.parent))

from main import app


def test_image_modification_conversation():
    """
    Testa uma conversa de múltiplos turnos com a API
    para manipulação de imagens,
    interagindo através do endpoint /generate/image.
    """
    with TestClient(app) as client:
        # 1. Criar uma imagem de teste em memória (preta, 10x10)
        test_image = Image.new('RGB', (10, 10), color='black')
        img_byte_arr = io.BytesIO()
        test_image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        # 2. Passo 1: Enviar a imagem e o primeiro prompt para o endpoint
        prompt1 = 'adicione um círculo vermelho no centro'
        files = {'image_file': ('test_image.png', img_byte_arr, 'image/png')}
        data = {'prompt': prompt1}
        response1 = client.post('/generate/image', files=files, data=data)

        # 3. Verificar a primeira resposta
        assert response1.status_code == status.HTTP_200_OK, (
            'A primeira requisição falhou com o status '
            + f'{response1.status_code}: {response1.text}'
        )
        response_data1 = response1.json()
        assert 'session_id' in response_data1, (
            'A resposta deve conter um session_id.'
        )
        assert 'generated_image' in response_data1, (
            'A resposta deve conter uma imagem gerada.'
        )
        assert response_data1['generated_image'] is not None, (
            'A imagem gerada não pode ser nula.'
        )

        session_id = response_data1['session_id']

        # 4. Passo 2: Continuar a conversa com um segundo prompt,
        #  usando o session_id
        prompt2 = 'agora mude o círculo para azul'
        data2 = {'prompt': prompt2, 'session_id': session_id}
        response2 = client.post('/generate/image', data=data2)

        # 5. Verificar a segunda resposta
        assert response2.status_code == status.HTTP_200_OK, (
            'A segunda requisição falhou com o status '
            + f'{response2.status_code}: {response2.text}'
        )
        response_data2 = response2.json()
        assert response_data2['session_id'] == session_id, (
            'O session_id deve ser o mesmo na continuação da conversa.'
        )
        assert 'generated_image' in response_data2, (
            'A segunda resposta também deve conter uma imagem.'
        )
        assert response_data2['generated_image'] is not None, (
            'A segunda imagem gerada não pode ser nula.'
        )
