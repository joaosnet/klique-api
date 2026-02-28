"""Start an ngrok tunnel for local testing.

Usage:
    task ngrok                # uses default port 8000
    task ngrok -- --port 8080 # pass extra args through task

Requirements:
    - Install the ngrok CLI or set NGROK_AUTH_TOKEN environment variable.
    - pyngrok is installed in dev dependencies (already added via `uv add --dev pyngrok`).

This script opens an ngrok HTTP tunnel and prints the public URL. Keep the process
running to keep the tunnel alive.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from dotenv import load_dotenv
from pyngrok import conf, ngrok
from rich.console import Console
from rich.panel import Panel

console = Console()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description='Start ngrok tunnel for local testing'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=int(os.getenv('PORT', '8000')),
        help='Local port to forward (default: 8000)',
    )
    parser.add_argument(
        '--token', type=str, help='Provide NGROK_AUTH_TOKEN inline (optional)'
    )
    args = parser.parse_args(argv)

    # Try to load token from .ngrok.env at project root if present
    project_root = Path(__file__).resolve().parents[1]
    ngrok_env = project_root / '.ngrok.env'
    if ngrok_env.exists():
        load_dotenv(dotenv_path=str(ngrok_env), override=False)

    # Allow --token to override environment
    token = args.token or os.getenv('NGROK_AUTH_TOKEN')

    # If token present, configure pyngrok
    if token:
        try:
            conf.get_default().auth_token = token
        except Exception:
            # setting auth_token may fail in some environments; continue and rely on ngrok binary
            pass
    else:
        # No token — show helpful instructions and exit
        console.print('[red]ngrok authtoken not found.[/red]')
        console.print(
            "Please create a '.ngrok.env' file at the project root with the line:"
        )
        console.print('    NGROK_AUTH_TOKEN=SEU_TOKEN_AQUI')
        console.print('')
        console.print('Example (PowerShell):')
        console.print('  $env:NGROK_AUTH_TOKEN = "SEU_TOKEN_AQUI"')
        console.print('  setx NGROK_AUTH_TOKEN "SEU_TOKEN_AQUI"')
        console.print('')
        console.print('Or install via the ngrok CLI:')
        console.print('  ngrok config add-authtoken SEU_TOKEN_AQUI')
        console.print('')
        console.print(
            'Get your token here: https://dashboard.ngrok.com/get-started/your-authtoken'
        )
        return 2

    console.print(Panel(f'Starting ngrok tunnel to localhost:{args.port}...', border_style='green'))
    try:
        tunnel = ngrok.connect(args.port, 'http')
        console.print(f'[green]ngrok public url:[/green] {tunnel.public_url}')
        console.print('Press Ctrl+C to stop the tunnel')

        # Block until interrupted
        ngrok.get_ngrok_process().proc.wait()
    except KeyboardInterrupt:
        console.print('Stopping ngrok tunnel...')
        try:
            ngrok.disconnect(tunnel.public_url)
            ngrok.kill()
        except Exception:
            pass
        return 0
    except Exception as exc:
        console.print('[red]Failed to start ngrok tunnel:[/red]', exc, style='red')
        return 2

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
