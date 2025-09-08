import asyncio
import io
import time

import pytest
from PIL import Image

from app.services.whatsapp import WhatsAppService


@pytest.mark.asyncio
async def test_status_deletion_detailed():
    """Teste detalhado para investigar o problema de deleção de status."""
    print('\n=== Teste detalhado deleção de status ===')

    # Criar serviço WhatsApp
    service = WhatsAppService(base_url='http://localhost:3000')

    # Criar uma imagem de teste simples
    print('1. Criando imagem de teste...')
    image = Image.new('RGB', (100, 100), color='blue')
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    image_bytes = img_byte_arr.getvalue()
    print(f'   Imagem criada com {len(image_bytes)} bytes')

    # Obter ID do status mais recente antes de postar
    print('2. Verificando status mais recente antes...')
    initial_status_id = await service.get_latest_status_id()
    print(f'   Status ID inicial: {initial_status_id}')

    # Postar um novo status
    print('3. Postando novo status...')
    status_id = await service.post_status_update(
        image_bytes,
        'Teste de deleção de status - ' + time.strftime('%Y-%m-%d %H:%M:%S'),
    )
    print(f'   Status postado com ID: {status_id}')

    if not status_id:
        print('   ❌ Falha ao postar status')
        pytest.skip('Não foi possível postar o status para teste')
        return

    # Aguardar um momento para o status ser processado
    print('4. Aguardando processamento...')
    await asyncio.sleep(2)

    # Verificar se o status foi postado corretamente
    print('5. Verificando status postado...')
    latest_status_id = await service.get_latest_status_id()
    print(f'   Status mais recente após postagem: {latest_status_id}')

    if latest_status_id == status_id:
        print('   ✅ Status postado é o mais recente')
    else:
        print('   ⚠️  Status postado não é o mais recente')

    # Verificar se o status existe
    print('6. Verificando existência do status...')
    exists_before = await service.status_exists(status_id)
    print(f'   Status existe antes da deleção: {exists_before}')

    # Tentar deletar o status
    print('7. Tentando deletar status...')
    deletion_result = await service.delete_status(status_id)
    print(f'   Resultado da deleção: {deletion_result}')

    # Aguardar um momento após a deleção
    print('8. Aguardando após deleção...')
    await asyncio.sleep(2)

    # Verificar se o status ainda existe após deleção
    print('9. Verificando existência após deleção...')
    exists_after = await service.status_exists(status_id)
    print(f'   Status existe após deleção: {exists_after}')

    # Verificar o status mais recente após deleção
    print('10. Verificando status mais recente após deleção...')
    final_status_id = await service.get_latest_status_id()
    print(f'   Status mais recente final: {final_status_id}')

    # Resultados
    print('\n=== Resultados ===')
    print(f'Postado: {status_id}')
    print(f'Deletado: {deletion_result}')
    print(f'Existia antes: {exists_before}')
    print(f'Existe após: {exists_after}')
    print(f'Status final: {final_status_id}')

    # Assertions
    assert status_id is not None, 'Status ID não deve ser None'
    assert isinstance(status_id, str), 'Status ID deve ser string'
    assert len(status_id) > 0, 'Status ID não deve estar vazio'

    print('✅ Teste concluído com sucesso')


@pytest.mark.asyncio
async def test_delete_nonexistent_status():
    """Teste para deletar um status que não existe."""
    print('\n=== Teste deleção de status inexistente ===')

    service = WhatsAppService()

    # Tentar deletar um status com ID inválido
    print('Tentando deletar status com ID inválido...')
    result = await service.delete_status('invalid_status_id_12345')
    print(f'Resultado: {result}')

    # Deve retornar True (tratado como deletado)
    assert result is True, 'Deleção de status inválido deve retornar True'

    print('✅ Teste de status inexistente concluído')


@pytest.mark.asyncio
async def test_status_existence_check():
    """Teste para verificar a existência de status."""
    print('\n=== Teste de verificação de existência de status ===')

    service = WhatsAppService()

    # Verificar existência com ID válido
    latest_id = await service.get_latest_status_id()
    print(f'ID do status mais recente: {latest_id}')

    if latest_id:
        exists = await service.status_exists(latest_id)
        print(f'Status {latest_id} existe: {exists}')
        # Pode ser True ou False dependendo do estado real

    # Verificar existência com ID inválido
    exists_invalid = await service.status_exists('invalid_status_id_12345')
    print(f'Status inválido existe: {exists_invalid}')
    # Deve ser False na maioria dos casos

    print('✅ Teste de verificação de existência concluído')


if __name__ == '__main__':
    # Executar testes manualmente para debug
    asyncio.run(test_status_deletion_detailed())
