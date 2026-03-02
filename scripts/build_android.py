"""Script para compilar o aplicativo Android via Capacitor.

Este script usa **rich** para saídas coloridas e painéis, tornando a
execução mais agradável no terminal.
"""

import re
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from collections import defaultdict
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
    'anim',
    'animator',
    'color',
    'drawable',
    'font',
    'layout',
    'menu',
    'mipmap',
    'raw',
    'transition',
    'values',
    'xml',
)


def remove_invalid_res_dirs(android_dir: Path) -> None:
    """Delete res/ subdirs whose names are not valid Android qualifiers.

    For example ``mipmap-512`` is rejected by aapt2 because '512' is not a
    known resource qualifier.  We detect dirs whose base name (the part
    before the first '-') is a known type but whose full name does not
    match the allowed pattern, and dirs that are entirely unknown, then
    remove them.
    """
    # Pattern: <type>[-<qual>]*  where qualifier doesn't start with a digit
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
                '[yellow]Removing invalid resource directory:'
                f' {entry}[/yellow]'
            )
            shutil.rmtree(entry)


def fix_duplicate_resources(android_dir: Path) -> None:  # noqa: PLR0912
    """Detect and fix duplicate resource declarations in values/*.xml.
    scripts\build_android.py
        Android's resource merger fails with 'Duplicate resources' when the
        same resource name is declared in multiple XML files inside a values/
        directory.  This function scans all values XML files, finds duplicates,
        and removes entries from non-canonical files, keeping the entry in the
        file that defines the most resources (e.g. colors.xml).
    """
    values_dir = android_dir / 'app' / 'src' / 'main' / 'res' / 'values'
    if not values_dir.exists():
        return

    xml_files = sorted(values_dir.glob('*.xml'))

    # Collect all (tag, name) -> list of files that declare it
    resource_owners: dict[tuple[str, str], list[Path]] = defaultdict(list)

    for xml_file in xml_files:
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
        except ET.ParseError as e:
            console.print(
                f'[yellow]Could not parse {xml_file.name}: {e}[/yellow]'
            )
            continue
        for child in root:
            name = child.get('name')
            if name:
                resource_owners[(child.tag, name)].append(xml_file)

    # For each duplicated resource, keep only the entry in the file with
    # the most resources (usually colors.xml / strings.xml / styles.xml),
    # and remove it from all other files.
    fixed_any = False
    for (tag, name), owners in resource_owners.items():
        if len(owners) <= 1:
            continue

        console.print(
            f'[yellow]Duplicate resource: <{tag} name="{name}"> '
            f'in {[f.name for f in owners]}[/yellow]'
        )

        def resource_count(p: Path) -> int:
            try:
                return len(ET.parse(p).getroot())
            except ET.ParseError:
                return 0

        canonical = max(owners, key=resource_count)
        to_fix = [f for f in owners if f != canonical]

        for xml_file in to_fix:
            try:
                tree = ET.parse(xml_file)
                root = tree.getroot()
                removed = []
                for child in list(root):
                    if child.tag == tag and child.get('name') == name:
                        root.remove(child)
                        removed.append(child)
                if removed:
                    if len(root) == 0:
                        xml_file.unlink()
                        console.print(
                            f'[green]Deleted now-empty: '
                            f'{xml_file.name}[/green]'
                        )
                    else:
                        ET.indent(tree, space='    ')
                        tree.write(
                            xml_file,
                            encoding='utf-8',
                            xml_declaration=True,
                        )
                        console.print(
                            f'[green]Removed duplicate '
                            f'<{tag} name="{name}"> from '
                            f'{xml_file.name} '
                            f'(kept in {canonical.name})[/green]'
                        )
                    fixed_any = True
            except Exception as e:  # noqa: BLE001
                console.print(f'[red]Failed to fix {xml_file.name}: {e}[/red]')

    if not fixed_any:
        console.print('[green]No duplicate resources found.[/green]')


def execute_gradle(android_dir: Path, gradlew: str) -> None:
    run(f'{gradlew} clean', cwd=android_dir, check=False)
    try:
        run(f'{gradlew} assembleDebug', cwd=android_dir)
    except subprocess.CalledProcessError as first_err:
        # Check if the error is a duplicate resource conflict (source issue,
        # not a cache issue) — if so, fix duplicates and retry immediately.
        console.print(
            '[yellow]\n⚠️  assembleDebug failed. '
            'Checking for duplicate resource conflicts...[/yellow]'
        )
        fix_duplicate_resources(android_dir)
        try:
            run(f'{gradlew} assembleDebug', cwd=android_dir)
            return  # recovery succeeded
        except subprocess.CalledProcessError:
            pass  # fall through to cache-clearing recovery below

        console.print(
            '[red]\n❌ Gradle failed to build the APK.\n'
            'This is often caused by a corrupted cache '
            '(a jar under "~/.gradle/caches").\n'
            'Attempting an automated recovery by clearing the build cache '
            'and retrying...'
        )
        try:
            run(f'{gradlew} clean', cwd=android_dir, check=False)
            run(
                f'{gradlew} assembleDebug --refresh-dependencies',
                cwd=android_dir,
            )
        except subprocess.CalledProcessError:
            console.print(
                '[red]Automated recovery failed.\n'
                'Please check the error output above and rerun `task android`.'
            )
            raise first_err


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
