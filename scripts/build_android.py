"""Script para compilar o aplicativo Android via Capacitor.

Este script usa **rich** para saídas coloridas e painéis, tornando a
execução mais agradável no terminal.
"""

import shutil
import subprocess
import sys
import time
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

console = Console()


def get_adb_device() -> str | None:
    """Return the id of the first attached adb device, or None if none."""
    try:
        out = subprocess.check_output('adb devices', shell=True, text=True)
        lines = out.strip().splitlines()[1:]
        devices = [
            line.split()[0]
            for line in lines
            if line.strip() and 'device' in line
        ]
        return devices[0] if devices else None
    except Exception:
        return None


FRONTEND_DIR = Path(__file__).parent.parent / 'frontend'


def run(
    cmd: str, cwd: Path | None = None, check: bool = True
) -> subprocess.CompletedProcess:
    """Executa um comando exibindo saída em tempo real."""
    console.print(f'[cyan]\n[+] {cmd}[/cyan]')
    return subprocess.run(
        cmd,
        cwd=cwd or FRONTEND_DIR,
        shell=True,
        check=check,
    )


def print_header() -> None:
    console.print(
        Panel(
            'Build Android - OmniFlash',
            style='bold white',
            border_style='blue',
        )
    )


def ensure_npm_dependencies() -> None:
    run('npm install --legacy-peer-deps')


def build_frontend() -> None:
    run('npm run build')


def add_android_platform_if_missing(android_dir: Path) -> None:
    if not android_dir.exists():
        console.print(
            '\n[cyan][+] Pasta android não encontrada.'
            ' Adicionando plataforma...[/cyan]'
        )
        run('npx cap add android')


def install_typescript_optional() -> None:
    run('npm install --legacy-peer-deps typescript', check=False)


def sync_android() -> None:
    run('npx cap sync android')


def clear_gradle_cache(android_dir: Path, gradlew: str) -> None:
    gradle_jars = Path.home() / '.gradle' / 'caches' / 'jars-9'
    if not gradle_jars.exists():
        return
    console.print(
        '[cyan]Stopping any Gradle daemons and removing jars cache '
        '(~/.gradle/caches/jars-9) to avoid corruption issues...[/cyan]'
    )
    run(f'{gradlew} --stop', cwd=android_dir, check=False)
    try:
        shutil.rmtree(gradle_jars)
        return
    except Exception as exc:  # pragma: no cover - best effort
        console.print(
            f'[yellow]Initial removal failed (lock in use): {exc}[/yellow]'
        )
    time.sleep(1)
    try:
        shutil.rmtree(gradle_jars)
        return
    except Exception as exc2:  # pragma: no cover
        console.print(
            f'[yellow]Second removal attempt also failed: {exc2}[/yellow]'
        )
    if sys.platform == 'win32':
        console.print(
            '[yellow]Attempting to kill java processes to release the '
            'file lock...[/yellow]'
        )
        try:
            subprocess.run(
                'taskkill /F /IM java.exe',
                shell=True,
                check=False,
            )
        except Exception:
            pass
        time.sleep(1)
        try:
            shutil.rmtree(gradle_jars)
            return
        except Exception as exc3:  # pragma: no cover
            console.print(
                f'[yellow]Third removal attempt also failed: {exc3}[/yellow]'
            )
            console.print(
                '[yellow]Please close any Gradle/IDE processes or '
                'reboot to release the lock, then rerun.[/yellow]'
            )
            if gradle_jars.exists():
                console.print(
                    '[red]Gradle cache directory still present; '
                    'unable to proceed.[/red]'
                )
                sys.exit(1)
    else:
        console.print(
            '[yellow]Make sure no Gradle/IDE processes are running or '
            'manually execute `gradlew --stop`, then retry.[/yellow]'
        )


_VALID_RES_PREFIXES = (
    'anim', 'animator', 'color', 'drawable', 'font', 'layout',
    'menu', 'mipmap', 'raw', 'transition', 'values', 'xml',
)


def remove_invalid_res_dirs(android_dir: Path) -> None:
    """Delete any res/ subdirectories whose names are not valid Android qualifiers.

    For example ``mipmap-512`` is rejected by aapt2 because '512' is not a
    known resource qualifier.  We detect dirs whose base name (the part before
    the first '-') is a known type but whose full name does not match the
    allowed pattern, and dirs that are entirely unknown, then remove them.
    """
    import re

    # Pattern: <type>[-<qualifier>]*  where qualifier does not start with a digit
    valid_pattern = re.compile(
        r'^(' + '|'.join(_VALID_RES_PREFIXES) + r')(-[a-zA-Z][a-zA-Z0-9]*)*$'
    )

    res_dir = android_dir / 'app' / 'src' / 'main' / 'res'
    if not res_dir.exists():
        return
    for entry in res_dir.iterdir():
        if not entry.is_dir():
            continue
        if not valid_pattern.match(entry.name):
            console.print(
                f'[yellow]Removing invalid resource directory: {entry}[/yellow]'
            )
            shutil.rmtree(entry)


def execute_gradle(android_dir: Path, gradlew: str) -> None:
    run(f'{gradlew} clean', cwd=android_dir, check=False)
    try:
        run(f'{gradlew} assembleDebug', cwd=android_dir)
    except subprocess.CalledProcessError:
        console.print(
            '[red]\n❌ Gradle failed to build the APK.\n'
            'This is often caused by a corrupted cache '
            '(a jar under "~/.gradle/caches").\n'
            'Attempting an automated recovery by clearing the build cache '
            'and retrying...'
        )
        try:
            run(f'{gradlew} cleanBuildCache', cwd=android_dir, check=False)
            run(
                f'{gradlew} assembleDebug --refresh-dependencies',
                cwd=android_dir,
            )
        except subprocess.CalledProcessError:
            console.print(
                '[red]Automated recovery failed.\n'
                'Please run the following commands manually or delete '
                'the problematic files in ~/.gradle/caches and rerun '
                '`task android`:\n'
                '  gradlew.bat cleanBuildCache\n'
                '  gradlew.bat assembleDebug --refresh-dependencies'
            )
            raise


def display_and_optionally_install_apk(android_dir: Path) -> None:
    apk_dir = android_dir / 'app' / 'build' / 'outputs' / 'apk' / 'debug'
    apks = list(apk_dir.glob('*.apk'))
    if not apks:
        console.print(
            '\n[red]❌ APK não encontrado no caminho esperado.[/red]'
        )
        sys.exit(1)
    apk_path = apks[0]
    console.print(f'\n[green]✅ APK gerado em:[/green] {apk_path}')
    device = get_adb_device()
    if device:
        console.print(
            f'[cyan]Instalando APK no dispositivo {device} via adb...[/cyan]'
        )
        try:
            subprocess.run(
                f'adb install -r {apk_path}', shell=True, check=True
            )
            console.print('[green]✅ APK instalado no dispositivo.[/green]')
        except subprocess.CalledProcessError as e:
            console.print(f'[red]Falha ao instalar via adb:[/red] {e}')
    else:
        console.print(
            '[yellow]Nenhum dispositivo adb conectado; pule a instalação\
 automática.[/yellow]'
        )


def main() -> None:
    print_header()
    android_dir = FRONTEND_DIR / 'android'

    ensure_npm_dependencies()
    build_frontend()
    add_android_platform_if_missing(android_dir)
    install_typescript_optional()
    sync_android()

    gradlew = 'gradlew.bat' if sys.platform == 'win32' else './gradlew'
    clear_gradle_cache(android_dir, gradlew)
    remove_invalid_res_dirs(android_dir)
    execute_gradle(android_dir, gradlew)
    display_and_optionally_install_apk(android_dir)


if __name__ == '__main__':
    main()
