"""
Script para converter docs/icone_aplicativo.svg em PNGs para ícone Android.
Usa a biblioteca Python cairosvg (instala automaticamente se necessário).
"""

import importlib.util
import sys
from pathlib import Path

SVG_PATH = Path(__file__).parent.parent / 'docs' / 'icone_aplicativo.svg'
RES_DIR = (
    Path(__file__).parent.parent
    / 'frontend'
    / 'android'
    / 'app'
    / 'src'
    / 'main'
    / 'res'
)

# Tamanhos padrão Android
SIZES = {
    'mdpi': 48,
    'hdpi': 72,
    'xhdpi': 96,
    'xxhdpi': 144,
    'xxxhdpi': 192,
    'anydpi-v26': 192,  # Usado para adaptive icon foreground
}

# Nome base do arquivo
PNG_NAME = 'ic_launcher.png'
PNG_FOREGROUND = 'ic_launcher_foreground.png'


def ensure_cairosvg():
    if importlib.util.find_spec('cairosvg') is None:
        import subprocess

        print('Instalando cairosvg...')
        subprocess.check_call([
            sys.executable,
            '-m',
            'pip',
            'install',
            'cairosvg',
        ])
    global cairosvg
    import cairosvg


def convert_svg_to_png(svg_path, out_path, size):
    cairosvg.svg2png(
        url=str(svg_path),
        write_to=str(out_path),
        output_width=size,
        output_height=size,
    )


def main():
    ensure_cairosvg()
    if not SVG_PATH.exists():
        print(f'SVG não encontrado: {SVG_PATH}')
        return
    for dpi, size in SIZES.items():
        dir_path = RES_DIR / f'mipmap-{dpi}'
        dir_path.mkdir(parents=True, exist_ok=True)
        out_path = dir_path / (
            PNG_NAME if dpi != 'anydpi-v26' else PNG_FOREGROUND
        )
        print(f'Gerando {out_path} ({size}x{size})...')
        convert_svg_to_png(SVG_PATH, out_path, size)
    print('Conversão concluída!')


if __name__ == '__main__':
    main()
