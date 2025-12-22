#!/usr/bin/env python3
"""
Script para configurar cookies do Gemini automaticamente.

Este script tenta importar cookies do navegador usando browser-cookie3
e salva as credenciais necessárias no arquivo .env.

Uso:
    python setup_cookies.py [navegador]

Navegadores suportados:
    chrome, chromium, opera, opera_gx, brave, edge, vivaldi, firefox, librewolf, safari

Se nenhum navegador for especificado, tenta todos os navegadores disponíveis.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Adicionar o diretório atual ao path para importar gemini_webapi
sys.path.insert(0, str(Path(__file__).parent))

try:
    import browser_cookie3 as bc3
    from gemini_webapi import GeminiClient
except ImportError as e:
    print(f'Erro ao importar dependências: {e}')
    print(
        'Certifique-se de que browser-cookie3 e gemini_webapi estão instalados.'
    )
    sys.exit(1)


def setup_cookies(browser_name=None):
    """Configura cookies do Gemini automaticamente.

    Args:
        browser_name: Nome do navegador para extrair cookies.
                     Se None, tenta todos os navegadores disponíveis.
    """
    if browser_name:
        print(f'🔍 Procurando cookies do Gemini no navegador: {browser_name}')
    else:
        print(
            '🔍 Procurando cookies do Gemini em todos os navegadores disponíveis...'
        )

    try:
        # Mapeamento de nomes de navegadores para funções do browser_cookie3
        browser_functions = {
            'chrome': bc3.chrome,
            'chromium': bc3.chromium,
            'opera': bc3.opera,
            'opera_gx': bc3.opera_gx,
            'brave': bc3.brave,
            'edge': bc3.edge,
            'vivaldi': bc3.vivaldi,
            'firefox': bc3.firefox,
            'librewolf': bc3.librewolf,
            'safari': bc3.safari,
        }

        secure_1psid = None
        secure_1psidts = None
        browser_used = None

        if browser_name:
            # Usar navegador específico
            if browser_name not in browser_functions:
                print(f"❌ Navegador '{browser_name}' não suportado.")
                print(
                    f'Navegadores suportados: {", ".join(browser_functions.keys())}'
                )
                return False

            try:
                cj = browser_functions[browser_name](domain_name='google.com')
                cookies = {cookie.name: cookie.value for cookie in cj}

                if '__Secure-1PSID' in cookies:
                    secure_1psid = cookies['__Secure-1PSID']
                    secure_1psidts = cookies.get('__Secure-1PSIDTS', '')
                    browser_used = browser_name
                    print(
                        f'✅ Cookies encontrados no navegador: {browser_name}'
                    )
                else:
                    print(
                        f'❌ Cookie __Secure-1PSID não encontrado no navegador {browser_name}.'
                    )
                    return False

            except Exception as e:
                print(f'❌ Erro ao acessar navegador {browser_name}: {e}')
                print(
                    'Certifique-se de que o navegador está instalado e você tem permissões adequadas.'
                )
                return False
        else:
            # Tentar todos os navegadores disponíveis
            for name, func in browser_functions.items():
                try:
                    cj = func(domain_name='google.com')
                    cookies = {cookie.name: cookie.value for cookie in cj}

                    if '__Secure-1PSID' in cookies:
                        secure_1psid = cookies['__Secure-1PSID']
                        secure_1psidts = cookies.get('__Secure-1PSIDTS', '')
                        browser_used = name
                        print(f'✅ Cookies encontrados no navegador: {name}')
                        break

                except Exception as e:
                    # Ignorar erros de navegadores não disponíveis
                    if (
                        'not found' in str(e).lower()
                        or 'permission' in str(e).lower()
                    ):
                        continue
                    print(f'⚠️  Erro ao verificar navegador {name}: {e}')

        if not secure_1psid:
            print(
                '❌ Cookie __Secure-1PSID não encontrado em nenhum navegador.'
            )
            print(
                'Certifique-se de que você está logado no Gemini (gemini.google.com) no seu navegador.'
            )
            if not browser_name:
                print(
                    'Dica: Você pode especificar um navegador específico, ex: python setup_cookies.py chrome'
                )
            return False

        # Atualizar .env preservando o formato
        update_env_file(secure_1psid, secure_1psidts)

        print('✅ Cookies salvos com sucesso no .env!')
        print(f'   Navegador usado: {browser_used}')
        print(f'   SECURE_1PSID: {secure_1psid[:20]}...')
        return True

    except Exception as e:
        print(f'❌ Erro ao obter cookies: {e}')
        print('Tente fazer login no Gemini manualmente e executar novamente.')
        return False


def update_env_file(secure_1psid, secure_1psidts):
    """Atualiza o arquivo .env preservando comentários e outras configurações."""
    env_path = Path('.env')

    if not env_path.exists():
        # Criar arquivo com template completo
        template = f"""# Configurações para o Gemini Web API MCP Server

# Credenciais do Gemini (obrigatórias)
SECURE_1PSID='{secure_1psid}'
SECURE_1PSIDTS='{secure_1psidts}'

# Configurações do Google Drive (opcionais - para salvar arquivos gerados)
# Método: OAuth 2.0 + Pasta Pessoal

# IMPORTANTE: Para Docker, coloque os arquivos no diretório raiz do projeto
# Caminho para o arquivo client_secrets.json baixado do Google Cloud Console
DRIVE_CLIENT_SECRETS_PATH=config/client_secrets.json
# Caminho onde salvar o token de acesso (será criado automaticamente)
DRIVE_TOKEN_PATH=config/token.json
# ID da pasta pessoal onde salvar as imagens
DRIVE_FOLDER_ID=sua_pasta_pessoal_id_aqui

# Como obter as credenciais:
# 1. Gemini: Faça login no gemini.google.com e extraia os cookies __Secure-1PSID e __Secure-1PSIDTS
#
# 2. Google Drive - OAuth 2.0 + Pasta Pessoal:
#   - Vá para Google Cloud Console > APIs & Services > Credentials
#   - Clique em "+ CREATE CREDENTIALS" > "OAuth 2.0 Client ID"
#   - Tipo: "Desktop application"
#   - Baixe o arquivo client_secrets.json
#   - Crie uma pasta no seu Google Drive pessoal
#   - Copie o ID da pasta da URL: https://drive.google.com/drive/folders/FOLDER_ID
"""
        env_path.write_text(template, encoding='utf-8')
        return

    # Ler conteúdo atual
    content = env_path.read_text(encoding='utf-8')
    lines = content.split('\n')

    # Verificar se as credenciais já existem
    has_psid = any(line.startswith('SECURE_1PSID=') for line in lines)
    _has_psidts = any(line.startswith('SECURE_1PSIDTS=') for line in lines)

    # Atualizar linhas existentes ou adicionar novas
    updated_lines = []
    credentials_added = False

    for line in lines:
        if line.startswith('SECURE_1PSID='):
            updated_lines.append(f"SECURE_1PSID='{secure_1psid}'")
        elif line.startswith('SECURE_1PSIDTS='):
            updated_lines.append(f"SECURE_1PSIDTS='{secure_1psidts}'")
        elif line.strip() == '' and not credentials_added and not has_psid:
            # Adicionar credenciais após comentários iniciais se não existirem
            updated_lines.append(f"SECURE_1PSID='{secure_1psid}'")
            updated_lines.append(f"SECURE_1PSIDTS='{secure_1psidts}'")
            updated_lines.append('')  # Linha em branco
            updated_lines.append(line)
            credentials_added = True
        else:
            updated_lines.append(line)

    # Se ainda não adicionou as credenciais, adicionar no final
    if not has_psid and not credentials_added:
        if (
            updated_lines and updated_lines[-1].strip()
        ):  # Se a última linha não for vazia
            updated_lines.append('')  # Adicionar linha em branco
        updated_lines.append(f"SECURE_1PSID='{secure_1psid}'")
        updated_lines.append(f"SECURE_1PSIDTS='{secure_1psidts}'")

    # Escrever de volta
    env_path.write_text('\n'.join(updated_lines), encoding='utf-8')


def test_cookies():
    """Testa se os cookies estão funcionando."""
    print('🧪 Testando cookies...')

    load_dotenv('.env')

    secure_1psid = os.getenv('SECURE_1PSID')
    secure_1psidts = os.getenv('SECURE_1PSIDTS', '')

    if not secure_1psid:
        print('❌ SECURE_1PSID não definido no .env')
        return False

    try:
        # Tentar inicializar cliente
        client = GeminiClient(secure_1psid, secure_1psidts)
        # Tentar init (que faz uma chamada de teste)
        import asyncio

        asyncio.run(client.init(timeout=10))
        print(
            '✅ Cookies funcionando! Cliente Gemini inicializado com sucesso.'
        )
        return True

    except Exception as e:
        print(f'❌ Erro ao testar cookies: {e}')
        return False


def main():
    """Função principal."""
    print('🚀 Configurador de Cookies do Gemini MCP\n')

    # Verificar argumentos da linha de comando
    if len(sys.argv) > 1 and sys.argv[1] in {'--help', '-h', 'help'}:
        print('Uso: python setup_cookies.py [navegador]')
        print('\nNavegadores suportados:')
        print(
            '  chrome, chromium, opera, opera_gx, brave, edge, vivaldi, firefox, librewolf, safari'
        )
        print(
            '\nSe nenhum navegador for especificado, tenta todos os navegadores disponíveis.'
        )
        print('\nExemplos:')
        print('  python setup_cookies.py          # Todos os navegadores')
        print('  python setup_cookies.py chrome   # Apenas Chrome')
        print('  python setup_cookies.py firefox  # Apenas Firefox')
        return

    browser_name = None
    if len(sys.argv) > 1:
        browser_name = sys.argv[1].lower()
        print(f'Navegador especificado: {browser_name}')

    # Verificar se .env existe
    env_path = Path('.env')
    if not env_path.exists():
        env_path.touch()
        print('📄 Arquivo .env criado.')

    # Tentar obter cookies automaticamente
    print('Tentando obter cookies automaticamente...')
    if not setup_cookies(browser_name):
        print('\nPara configurar manualmente:')
        print('1. Acesse https://gemini.google.com')
        print('2. Faça login na sua conta Google')
        print('3. Abra as ferramentas de desenvolvedor (F12)')
        print('4. Vá para Application > Cookies > https://gemini.google.com')
        print('5. Copie os valores de __Secure-1PSID e __Secure-1PSIDTS')
        print('6. Cole no arquivo .env:')
        print('   SECURE_1PSID=seu_valor_aqui')
        print('   SECURE_1PSIDTS=seu_valor_aqui')
        return

    # Testar cookies
    if test_cookies():
        print('\n🎉 Setup concluído! O servidor MCP pode usar o Gemini.')
    else:
        print(
            '\n❌ Cookies inválidos. Tente novamente ou configure manualmente.'
        )


if __name__ == '__main__':
    main()
