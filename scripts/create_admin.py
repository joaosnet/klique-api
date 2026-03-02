import asyncio
import sys
from datetime import datetime, timezone
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.text import Text

# Adiciona o diretório raiz ao path para importar os módulos do app
sys.path.append(str(Path(__file__).parent.parent))

from app.database import (
    close_db_connection,
    get_profiles_collection,
    get_users_collection,
)
from app.dependencies import get_password_hash

console = Console()


async def create_admin_interactive():
    console.clear()
    console.print(
        Panel(
            Text('Gerador de Administrador OmniFlash', style='bold white'),
            subtitle='✨ Configuração Inicial ✨',
            border_style='bright_blue',
        )
    )

    # Coleta de dados
    name = Prompt.ask('[bold cyan]Nome Completo[/bold cyan]', default='Admin')
    email = Prompt.ask('[bold cyan]E-mail[/bold cyan]')
    password = Prompt.ask('[bold cyan]Senha[/bold cyan]', password=True)

    confirm = Confirm.ask(
        f'Deseja criar o admin [bold yellow]{name}[/bold yellow] ({email})?',
        default=True,
    )

    if not confirm:
        console.print('[yellow]Operação cancelada.[/yellow]')
        return

    with console.status('[bold green]Acessando banco de dados...'):
        db_users = get_users_collection()
        db_profiles = get_profiles_collection()

        # Verifica se já existe
        existing = await db_users.find_one({'email': email})
        if existing:
            console.print(
                f'\n[bold red]❌ Erro:[/bold red] O usuário com e-mail '
                f'[underline]{email}[/underline] já existe.'
            )
            return

        # 1. Criar Perfil
        profile_data = {
            'name': name,
            'nickname': name,
            'country': 'Brasil',
            'state': 'SP',
            'city': 'São Paulo',
            'district': 'Centro',
            'deficiency': 'Nenhuma',
            'avatar_url': None,
            'email': email,
            'created_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc),
        }

        profile_result = await db_profiles.insert_one(profile_data)
        profile_id = str(profile_result.inserted_id)

        # 2. Criar Usuário Admin
        hashed_password = get_password_hash(password)
        user_data = {
            'name': name,
            'email': email,
            'password': hashed_password,
            'profile_id': profile_id,
            'user_type': 'admin',
            'confirmed_code': True,  # Admin já vem confirmado
            'created_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc),
        }

        user_result = await db_users.insert_one(user_data)

    console.print('\n[bold green]✅ Sucesso![/bold green]')
    console.print(
        f'Usuário Admin criado com ID: '
        f'[white]{user_result.inserted_id}[/white]'
    )
    console.print(f'Perfil criado com ID: [white]{profile_id}[/white]\n')
    console.print(
        Panel(
            'Você já pode fazer login no sistema com suas credenciais.',
            border_style='green',
        )
    )


async def main():
    try:
        await create_admin_interactive()
    except KeyboardInterrupt:
        console.print('\n[red]Operação interrompida pelo usuário.[/red]')
    finally:
        await close_db_connection()


if __name__ == '__main__':
    asyncio.run(main())
