"""Helper script to start the frontend dev server and launch the
Capacitor Android project in live‑reload mode.

This makes it easy to work on the web code and see changes immediately
on a connected Android device (or emulator) without rebuilding the
APK every time.  The taskipy task defined in ``pyproject.toml`` will
invoke this script.

Usage from command line (taskipy will use this):

    python scripts/hot_reload_android.py

The script performs the following steps:

1. ensure npm dependencies are installed
2. start ``npm run dev`` in the frontend directory
3. wait a few seconds for the Vite dev server to come up
4. invoke Capacitor CLI with live‑reload flags
5. when the Capacitor process exits the helper stops the dev server

"""

import os
import socket
import subprocess
import time
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

console = Console()

FRONTEND_DIR = Path(__file__).parent.parent / 'frontend'


def get_local_ip() -> str:
    """Return a non‑loopback IPv4 address for the host.

    Uses a UDP socket hack that doesn't actually send packets; this works
    even without network connectivity (it falls back to 127.0.0.1).
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        addr = s.getsockname()[0]
    except Exception:
        addr = '127.0.0.1'
    finally:
        try:
            s.close()
        except Exception:
            pass
    return addr


def run(
    cmd: str, cwd: Path | None = None, check: bool = True
) -> subprocess.CompletedProcess:
    """Execute a command showing live output."""
    console.print(f'[cyan]\n[+] {cmd}[/cyan]')
    return subprocess.run(
        cmd,
        cwd=cwd or FRONTEND_DIR,
        shell=True,
        check=check,
    )


def remove_precompressed_dist_assets() -> None:
    """Remove .gz/.br files from dist before Android sync.

    These precompressed files are useful for web serving but can cause
    duplicate asset merge errors in Android builds.
    """
    dist_dir = FRONTEND_DIR / 'dist'
    if not dist_dir.exists():
        return
    removed = 0
    for pattern in ('**/*.gz', '**/*.br'):
        for file_path in dist_dir.glob(pattern):
            if file_path.is_file():
                file_path.unlink(missing_ok=True)
                removed += 1
    if removed:
        console.print(
            f'[cyan]Removed {removed} precompressed dist assets '
            '(.gz/.br) before Android sync.[/cyan]'
        )


def main() -> None:
    console.print(
        Panel(
            'Android hot‑reload mode',
            style='bold white',
            border_style='magenta',
        )
    )

    # 1. install frontend dependencies (ensures capacitor packages exist)
    run('npm install')
    remove_precompressed_dist_assets()

    # make sure the Android platform exists and is synced; mirrors
    # build_android.py so the dev loop doesn't fail on a fresh clone.
    android_dir = FRONTEND_DIR / 'android'
    if not android_dir.exists():
        console.print(
            '[cyan][+] Pasta android não encontrada.'
            ' Adicionando plataforma...[/cyan]'
        )
        run('npx cap add android')

    # Cap sync will load our TypeScript config file, so install TS just in
    # case the caller hasn't already run `npm install` post‑clone.  A
    # second install is harmless and avoids the same cryptic error we
    # saw during the scripted build.
    run('npm install typescript', check=False)
    run('npx cap sync android')

    # 2. Auto-detect backend URL: if Docker production stack is running,
    # route API calls through Traefik (https://localhost); otherwise the
    # Vite proxy will try http://localhost:8000 (local uvicorn).
    if not os.environ.get('VITE_BACKEND_URL'):
        try:
            out = subprocess.check_output(
                'docker inspect -f "{{.State.Running}}" fastapi-omniflash',
                shell=True,
                text=True,
                stderr=subprocess.DEVNULL,
            ).strip()
            if out == 'true':
                os.environ['VITE_BACKEND_URL'] = 'https://localhost'
                console.print(
                    '[cyan]Docker backend detected → '
                    'VITE_BACKEND_URL=https://localhost[/cyan]'
                )
        except Exception:
            pass  # Docker not available or container not running

    # Start the Vite dev server in the background
    dev_proc = subprocess.Popen(
        'npm run dev',
        cwd=FRONTEND_DIR,
        shell=True,
    )

    # give the server some time to be ready before launching the app
    time.sleep(5)

    try:
        # 3. run the Android app with Capacitor's live reload flags.
        # ``-l`` enables live reload; ``--host`` sets the network address
        # so a real device can reach the Vite dev server.
        # Note: ``--external`` was removed in Capacitor 6 – ``--host``
        # already covers that role.  ``--forwardPorts`` runs adb reverse
        # automatically for improved live-reload support.
        #
        # If adb can see a device/emulator we pass ``--target`` so the
        # CLI does not prompt interactively (the prompt doesn't accept
        # keystrokes when executed from Python/Taskipy).
        def find_adb_device() -> str | None:
            try:
                out = subprocess.check_output(
                    'adb devices', shell=True, text=True
                )
                lines = out.strip().splitlines()[1:]
                devices = [
                    line.split()[0]
                    for line in lines
                    if line.strip() and 'device' in line
                ]
                return devices[0] if devices else None
            except Exception:
                return None

        target = find_adb_device()
        ip = get_local_ip()
        cmd = (
            f'npx cap run android -l --host={ip}'
            ' --port=3000 --forwardPorts=3000:3000'
        )
        console.print(f'[cyan]Using host address {ip} for livereload[/cyan]')
        if target:
            console.print(
                f'[cyan]Using adb device {target} (auto-selected)[/cyan]'
            )
            cmd += f' --target={target}'
        try:
            run(cmd)
        except KeyboardInterrupt:
            console.print('[yellow]Hot-reload interrupted by user.[/yellow]')
    finally:
        # kill the dev process when the user quits the Android run
        console.print('\n[+] stopping dev server')
        dev_proc.terminate()
        try:
            dev_proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            dev_proc.kill()


if __name__ == '__main__':
    main()
