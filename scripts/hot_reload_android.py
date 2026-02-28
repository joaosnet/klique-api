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


def main() -> None:
    console.print(
        Panel(
            'Android hot‑reload mode',
            style='bold white',
            border_style='magenta',
        )
    )

    # 1. install frontend dependencies (ensures capacitor packages exist)
    # avoid peer-dependency conflicts that show up on some machines by
    # using the legacy resolver (matches what we use in CI/production).
    run('npm install --legacy-peer-deps')

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
    run('npm install --legacy-peer-deps typescript', check=False)
    run('npx cap sync android')

    # 2. start the Vite dev server in the background
    dev_proc = subprocess.Popen(
        'npm run dev',
        cwd=FRONTEND_DIR,
        shell=True,
    )

    # give the server some time to be ready before launching the app
    time.sleep(5)

    try:
        # 3. run the Android app with Capacitor's live reload flags.  the
        # ``--external`` option tells Capacitor to use the machine's
        # network address rather than ``localhost`` so a real device can
        # reach it; ``-l`` is shorthand for ``--livereload``.
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
        cmd = f'npx cap run android -l --external --host={ip}'
        console.print(f'[cyan]Using host address {ip} for livereload[/cyan]')
        if target:
            console.print(
                f'[cyan]Using adb device {target} (auto-selected)[/cyan]'
            )
            cmd += f' --target={target}'
        run(cmd)
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
