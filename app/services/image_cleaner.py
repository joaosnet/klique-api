import os
import queue
import sys
import threading
from typing import Any, Callable, Optional, Tuple

import cv2
import numpy as np
from loguru import logger

# --- Configuração do Logger ---
logger.remove()
logger.add(
    sys.stderr,
    format='<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>',
)
logger.add(
    'execution_logs.log', rotation='1 MB', retention='10 days', level='DEBUG'
)

# --- Constantes para Upscale ---
RESOLUTION_4K = (3840, 2160)  # 4K UHD
RESOLUTION_2K = (2560, 1440)  # 2K QHD
RESOLUTION_FHD = (1920, 1080)  # Full HD


# --- Classe para processamento em background ---
class BackgroundTask:
    """Executa tarefas pesadas em thread separada para não travar a GUI."""

    def __init__(self):
        self.result_queue = queue.Queue()
        self.is_running = False

    def run(self, func: Callable, *args, **kwargs) -> None:
        """Inicia a tarefa em background."""
        self.is_running = True
        thread = threading.Thread(
            target=self._worker, args=(func, args, kwargs), daemon=True
        )
        thread.start()

    def _worker(self, func: Callable, args: tuple, kwargs: dict) -> None:
        """Worker que executa a função e coloca o resultado na fila."""
        try:
            result = func(*args, **kwargs)
            self.result_queue.put(('success', result))
        except Exception as e:
            self.result_queue.put(('error', str(e)))
        finally:
            self.is_running = False

    def get_result(self) -> Optional[Tuple[str, Any]]:
        """Retorna o resultado se disponível, None caso contrário."""
        try:
            return self.result_queue.get_nowait()
        except queue.Empty:
            return None


# --- CLASSE: Seletor com Mouse ---
class ROISelector:
    def __init__(self, image_path):
        self.original_img = cv2.imread(image_path)
        if self.original_img is None:
            raise ValueError('Não consegui ler a imagem.')

        self.h_orig, self.w_orig = self.original_img.shape[:2]
        self.scale = 1.0
        self.start_point = None
        self.end_point = None
        self.drawing = False
        self.rect_coords = None

        max_h = 900
        if self.h_orig > max_h:
            self.scale = max_h / self.h_orig
            new_w = int(self.w_orig * self.scale)
            new_h = int(self.h_orig * self.scale)
            self.display_img = cv2.resize(self.original_img, (new_w, new_h))
        else:
            self.display_img = self.original_img.copy()

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.start_point = (x, y)
            self.end_point = (x, y)
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing:
                self.end_point = (x, y)
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            self.end_point = (x, y)
            x1 = min(self.start_point[0], self.end_point[0])
            y1 = min(self.start_point[1], self.end_point[1])
            x2 = max(self.start_point[0], self.end_point[0])
            y2 = max(self.start_point[1], self.end_point[1])

            real_x = int(x1 / self.scale)
            real_y = int(y1 / self.scale)
            real_w = int((x2 - x1) / self.scale)
            real_h = int((y2 - y1) / self.scale)

            self.rect_coords = (real_x, real_y, real_w, real_h)
            logger.debug(f'Seleção Mouse: {self.rect_coords}')

    def select(self):
        window_name = 'SELECIONE A MARCA (Arraste e aperte ENTER)'
        cv2.namedWindow(window_name)
        cv2.setMouseCallback(window_name, self.mouse_callback)

        while True:
            img_copy = self.display_img.copy()
            if self.start_point and self.end_point:
                cv2.rectangle(
                    img_copy, self.start_point, self.end_point, (0, 0, 255), 2
                )
            cv2.imshow(window_name, img_copy)
            key = cv2.waitKey(1) & 0xFF
            if key in {13, 32}:  # Enter/Space
                if self.rect_coords:
                    break
            if key == 27:  # Esc
                self.rect_coords = None
                break
        cv2.destroyAllWindows()
        return self.rect_coords


# --- NOVA FUNÇÃO: Auto Detecção (Template Matching) ---
def auto_detect_watermark(image_path, template_path=None, threshold=0.7):
    """
    Tenta encontrar o template dentro da imagem alvo.
    Retorna (w, h, off_x, off_y) se encontrar, ou None se falhar.
    """
    if template_path is None:
        template_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'template.png'
        )

    logger.debug(f'Procurando template em: {template_path}')

    if not os.path.exists(template_path):
        logger.warning(
            f"Template '{template_path}' não encontrado. Automação pulada."
        )
        return None

    img_rgb = cv2.imread(image_path)
    if img_rgb is None:
        logger.error(f'Não foi possível ler a imagem alvo: {image_path}')
        return None

    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)

    template = cv2.imread(template_path, 0)  # Lê em grayscale
    if template is None:
        logger.error(f'Falha ao ler o arquivo de template: {template_path}')
        return None

    w_temp, h_temp = template.shape[::-1]
    h_img, w_img = img_gray.shape[:2]

    # A mágica do OpenCV procurando padrões
    res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    logger.debug(
        f'Confiança da detecção: {max_val:.4f} (Threshold: {threshold})'
    )

    if max_val >= threshold:
        # max_loc é o canto superior esquerdo da correspondência
        top_left = max_loc

        # Calculamos os offsets baseados no canto inferior direito da imagem
        # X final da marca = top_left[0] + w_temp
        # Off X = Largura total - X final
        off_x = w_img - (top_left[0] + w_temp)

        # Y final da marca = top_left[1] + h_temp
        # Off Y = Altura total - Y final
        off_y = h_img - (top_left[1] + h_temp)

        # Ajuste fino: Se o offset der negativo (borda), zera.
        off_x = max(0, off_x)
        off_y = max(0, off_y)

        return (w_temp, h_temp, off_x, off_y)

    return None


# --- FUNÇÃO: Remoção de Fundo (rembg - opcional) ---
def remove_background(
    input_path: str,
    output_path: Optional[str] = None,
    alpha_matting: bool = False,
    alpha_matting_foreground_threshold: int = 240,
    alpha_matting_background_threshold: int = 10,
) -> Tuple[Optional[str], str]:
    """
    Remove o fundo de uma imagem usando a biblioteca rembg.

    Args:
        input_path: Caminho da imagem de entrada
        output_path: Caminho de saída (opcional, gera automaticamente se não fornecido)
        alpha_matting: Usar alpha matting para bordas mais suaves
        alpha_matting_foreground_threshold: Threshold para foreground (0-255)
        alpha_matting_background_threshold: Threshold para background (0-255)

    Returns:
        Tuple com (caminho_saída, mensagem_status)
    """
    logger.info(f'Removendo fundo: {input_path}')

    if not os.path.exists(input_path):
        return None, 'Arquivo não encontrado.'

    try:
        from PIL import Image
        from rembg import remove
    except ImportError as e:
        logger.error(f'Biblioteca não instalada: {e}')
        return None, 'Instale rembg: pip install rembg'

    try:
        # Carregar imagem
        with Image.open(input_path) as img:
            # Converter para RGBA se necessário
            if img.mode != 'RGBA':
                img = img.convert('RGBA')

            # Remover fundo
            logger.debug('Processando remoção de fundo...')
            output_img = remove(
                img,
                alpha_matting=alpha_matting,
                alpha_matting_foreground_threshold=alpha_matting_foreground_threshold,
                alpha_matting_background_threshold=alpha_matting_background_threshold,
            )

            # Gerar caminho de saída
            if not output_path:
                base, ext = os.path.splitext(input_path)
                output_path = (
                    f'{base}_nobg.png'  # PNG para preservar transparência
                )

            # Garantir extensão PNG para transparência
            if not output_path.lower().endswith('.png'):
                output_path = os.path.splitext(output_path)[0] + '.png'

            output_img.save(output_path, 'PNG')
            logger.success(f'Fundo removido: {output_path}')
            return output_path, 'Sucesso'

    except Exception as e:
        logger.exception('Erro ao remover fundo')
        return None, str(e)


# --- FUNÇÃO: Remoção de Fundo Branco (sem dependências extras) ---
def remove_white_background(
    input_path: str,
    output_path: Optional[str] = None,
    threshold: int = 240,
    feather: int = 2,
) -> Tuple[Optional[str], str]:
    """
    Remove fundo branco/claro de uma imagem usando PIL.

    Funciona melhor quando a imagem tem fundo branco sólido (gerado via prompt).
    Não precisa de bibliotecas externas como rembg.

    Args:
        input_path: Caminho da imagem de entrada
        output_path: Caminho de saída (opcional)
        threshold: Valor RGB acima do qual é considerado "branco" (0-255)
        feather: Pixels de suavização nas bordas

    Returns:
        Tuple com (caminho_saída, mensagem_status)
    """
    logger.info(f'Removendo fundo branco: {input_path}')

    if not os.path.exists(input_path):
        return None, 'Arquivo não encontrado.'

    try:
        from PIL import Image

        # Carregar imagem
        img = Image.open(input_path)

        # Converter para RGBA
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        # Obter dados da imagem
        data = img.getdata()
        new_data = []

        for item in data:
            # Se o pixel é branco/quase branco (R, G, B todos acima do threshold)
            if (
                item[0] > threshold
                and item[1] > threshold
                and item[2] > threshold
            ):
                # Tornar transparente
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append(item)

        # Aplicar novos dados
        img.putdata(new_data)

        # Gerar caminho de saída
        if not output_path:
            base, ext = os.path.splitext(input_path)
            output_path = f'{base}_nobg.png'

        # Garantir extensão PNG
        if not output_path.lower().endswith('.png'):
            output_path = os.path.splitext(output_path)[0] + '.png'

        img.save(output_path, 'PNG')
        logger.success(f'Fundo branco removido: {output_path}')
        return output_path, 'Sucesso'

    except Exception as e:
        logger.exception('Erro ao remover fundo branco')
        return None, str(e)


# --- Singleton para Real-ESRGAN (evita recarregar modelo) ---
_realesrgan_upsampler = None


def get_realesrgan_upsampler(
    scale: int = 4, model_name: str = 'RealESRGAN_x4plus'
):
    """
    Retorna instância singleton do Real-ESRGAN upsampler.
    Baixa o modelo automaticamente na primeira execução.

    Args:
        scale: Fator de upscale (2 ou 4)
        model_name: Nome do modelo a usar

    Returns:
        RealESRGANer instance
    """
    global _realesrgan_upsampler

    if _realesrgan_upsampler is not None:
        return _realesrgan_upsampler

    try:
        # Patch para compatibilidade torchvision > 0.18
        # O basicsr usa uma API removida do torchvision
        import sys

        import torch

        try:
            from torchvision.transforms import functional as F

            # Criar módulo fake para compatibilidade
            if 'torchvision.transforms.functional_tensor' not in sys.modules:
                sys.modules['torchvision.transforms.functional_tensor'] = F
        except ImportError:
            pass

        from basicsr.archs.rrdbnet_arch import RRDBNet
        from realesrgan import RealESRGANer

        logger.info(f'Inicializando Real-ESRGAN ({model_name})...')

        # Detectar dispositivo (GPU se disponível)
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f'Usando dispositivo: {device}')

        # Configurar modelo baseado no nome
        if model_name == 'RealESRGAN_x4plus':
            model = RRDBNet(
                num_in_ch=3,
                num_out_ch=3,
                num_feat=64,
                num_block=23,
                num_grow_ch=32,
                scale=4,
            )
            netscale = 4
            model_url = 'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth'
        elif model_name == 'RealESRGAN_x2plus':
            model = RRDBNet(
                num_in_ch=3,
                num_out_ch=3,
                num_feat=64,
                num_block=23,
                num_grow_ch=32,
                scale=2,
            )
            netscale = 2
            model_url = 'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.1/RealESRGAN_x2plus.pth'
        elif model_name == 'RealESRNet_x4plus':
            # Modelo mais rápido, menos qualidade
            model = RRDBNet(
                num_in_ch=3,
                num_out_ch=3,
                num_feat=64,
                num_block=23,
                num_grow_ch=32,
                scale=4,
            )
            netscale = 4
            model_url = 'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.1/RealESRNet_x4plus.pth'
        else:
            # Padrão x4plus
            model = RRDBNet(
                num_in_ch=3,
                num_out_ch=3,
                num_feat=64,
                num_block=23,
                num_grow_ch=32,
                scale=4,
            )
            netscale = 4
            model_url = 'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth'

        # Diretório para modelos
        model_dir = os.path.join(os.path.dirname(__file__), 'models')
        os.makedirs(model_dir, exist_ok=True)
        model_path = os.path.join(model_dir, f'{model_name}.pth')

        # Baixar modelo se não existir
        if not os.path.exists(model_path):
            logger.info(
                f"Modelo '{model_name}' não encontrado localmente. Baixando de {model_url} ..."
            )
            try:
                from urllib import request

                tmp_path = model_path + '.download'
                request.urlretrieve(model_url, tmp_path)
                os.replace(tmp_path, model_path)
                logger.success(f"Modelo '{model_name}' baixado com sucesso.")
            except Exception as e:
                logger.error(f'Falha ao baixar modelo: {e}')
                raise FileNotFoundError(
                    f"Modelo '{model_name}' não encontrado e falha ao baixar: {e}"
                )

        # Criar upsampler
        _realesrgan_upsampler = RealESRGANer(
            scale=netscale,
            model_path=model_path,
            dni_weight=None,
            model=model,
            tile=0,  # 0 = sem tiles (mais qualidade), use 400 para menos VRAM
            tile_pad=10,
            pre_pad=0,
            half=False,  # True para GPU com FP16
            device=device,
        )

        logger.success('Real-ESRGAN inicializado com sucesso!')
        return _realesrgan_upsampler

    except Exception as e:
        logger.error(f'Erro ao inicializar Real-ESRGAN: {e}')
        raise


# --- FUNÇÃO: Upscale com Real-ESRGAN (Profissional) ---
def upscale_realesrgan(
    input_path: str,
    output_path: Optional[str] = None,
    scale: int = 4,
    model_name: str = 'RealESRGAN_x4plus',
    face_enhance: bool = False,
) -> Tuple[Optional[str], str]:
    """
    Upscale profissional usando Real-ESRGAN (GAN super-resolution).

    Args:
        input_path: Caminho da imagem de entrada
        output_path: Caminho de saída (opcional)
        scale: Fator de upscale (2 ou 4)
        model_name: Modelo a usar (RealESRGAN_x4plus, RealESRGAN_x2plus, RealESRNet_x4plus)
        face_enhance: Usar GFPGAN para melhorar rostos

    Returns:
        Tuple com (caminho_saída, mensagem_status)
    """
    logger.info(f'Real-ESRGAN Upscale: {input_path} (escala: {scale}x)')

    if not os.path.exists(input_path):
        return None, 'Arquivo não encontrado.'

    try:
        # Carregar imagem
        img = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
        if img is None:
            return None, 'Falha ao ler imagem.'

        h_orig, w_orig = img.shape[:2]
        logger.debug(f'Resolução original: {w_orig}x{h_orig}')

        # Obter upsampler
        upsampler = get_realesrgan_upsampler(
            scale=scale, model_name=model_name
        )

        # Face enhance (opcional)
        face_enhancer = None
        if face_enhance:
            try:
                from gfpgan import GFPGANer

                face_enhancer = GFPGANer(
                    model_path='https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.3.pth',
                    upscale=scale,
                    arch='clean',
                    channel_multiplier=2,
                    bg_upsampler=upsampler,
                )
                logger.info('GFPGAN ativado para melhorar rostos')
            except Exception as e:
                logger.warning(f'GFPGAN não disponível: {e}')
                face_enhancer = None

        # Processar upscale
        logger.info('Processando upscale com Real-ESRGAN...')

        if face_enhancer is not None:
            # Com face enhance
            _, _, output = face_enhancer.enhance(
                img, has_aligned=False, only_center_face=False, paste_back=True
            )
        else:
            # Sem face enhance
            output, _ = upsampler.enhance(img, outscale=scale)

        new_h, new_w = output.shape[:2]
        logger.debug(f'Nova resolução: {new_w}x{new_h}')

        # Gerar caminho de saída
        if not output_path:
            base, ext = os.path.splitext(input_path)
            output_path = f'{base}_realesrgan_{scale}x{ext}'

        cv2.imwrite(output_path, output)
        logger.success(f'Real-ESRGAN concluído: {output_path}')
        return output_path, 'Sucesso'

    except Exception as e:
        logger.exception('Erro no Real-ESRGAN upscale')
        return None, str(e)


# --- FUNÇÃO: Upscale Profissional com Real-ESRGAN + Pós-processamento ---
def upscale_with_enhancement(
    input_path: str,
    output_path: Optional[str] = None,
    scale: int = 4,
    sharpen_strength: float = 0.3,
    denoise: bool = True,
    face_enhance: bool = False,
) -> Tuple[Optional[str], str]:
    """
    Upscale profissional com Real-ESRGAN + pós-processamento opcional.

    Args:
        input_path: Caminho da imagem de entrada
        output_path: Caminho de saída
        scale: Fator de upscale (2 ou 4)
        sharpen_strength: Intensidade do sharpening pós-upscale (0.0 a 1.0)
        denoise: Aplicar denoising leve pós-upscale
        face_enhance: Usar GFPGAN para melhorar rostos

    Returns:
        Tuple com (caminho_saída, mensagem_status)
    """
    logger.info(f'Upscale Real-ESRGAN: {input_path} (escala: {scale}x)')

    if not os.path.exists(input_path):
        return None, 'Arquivo não encontrado.'

    try:
        # Usar Real-ESRGAN
        model_name = 'RealESRGAN_x4plus' if scale == 4 else 'RealESRGAN_x2plus'
        temp_output = input_path.replace('.', '_temp_esrgan.')

        result, msg = upscale_realesrgan(
            input_path,
            output_path=temp_output,
            scale=scale,
            model_name=model_name,
            face_enhance=face_enhance,
        )

        if result is None:
            return None, msg

        # Carregar resultado para pós-processamento
        img = cv2.imread(result, cv2.IMREAD_UNCHANGED)

        # Pós-processamento
        if img is not None:
            # 1. Denoising leve (opcional)
            if denoise and len(img.shape) == 3:
                logger.debug('Aplicando denoising leve...')
                img = cv2.fastNlMeansDenoisingColored(img, None, 3, 3, 7, 21)

            # 2. Sharpening sutil (opcional)
            if sharpen_strength > 0:
                logger.debug(
                    f'Aplicando sharpening (força: {sharpen_strength})...'
                )
                # Unsharp mask (mais natural que kernel simples)
                gaussian = cv2.GaussianBlur(img, (0, 0), 3)
                img = cv2.addWeighted(
                    img, 1 + sharpen_strength, gaussian, -sharpen_strength, 0
                )

        # Gerar caminho de saída
        if not output_path:
            base, ext = os.path.splitext(input_path)
            output_path = f'{base}_realesrgan_{scale}x{ext}'

        cv2.imwrite(output_path, img)

        # Limpar arquivo temporário
        if 'temp_output' in locals() and os.path.exists(temp_output):
            if temp_output != output_path:
                os.remove(temp_output)

        logger.success(f'Real-ESRGAN concluído: {output_path}')
        return output_path, 'Sucesso'

    except Exception as e:
        logger.exception('Erro no Real-ESRGAN')
        return None, str(e)


# --- O Músculo (Backend) ---
def remove_signature(
    input_path, output_path=None, box_w=104, box_h=111, off_x=61, off_y=62
):
    logger.info(f'Processando assinatura: {input_path}')
    if not os.path.exists(input_path):
        return None, 'Arquivo não encontrado.'

    img = cv2.imread(input_path)
    if img is None:
        return None, 'Falha ao ler imagem.'

    h, w = img.shape[:2]
    x1 = w - (box_w + off_x)
    x2 = w - off_x
    y1 = h - (box_h + off_y)
    y2 = h - off_y

    # Proteção contra coordenadas malucas
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(w, x2), min(h, y2)

    logger.debug(f'ROI: X[{x1}:{x2}] Y[{y1}:{y2}]')
    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    mask[y1:y2, x1:x2] = 255

    try:
        result = cv2.inpaint(img, mask, 3, cv2.INPAINT_TELEA)
    except Exception as e:
        logger.exception('Erro inpainting')
        return None, str(e)

    if not output_path:
        base, ext = os.path.splitext(input_path)
        output_path = f'{base}_clean{ext}'

    cv2.imwrite(output_path, result)
    logger.success(f'Salvo: {output_path}')
    return output_path, 'Sucesso'


def show_debug_window(input_path, box_w, box_h, off_x, off_y):
    """Mostra janela de debug usando Tkinter (compatível com OpenCV headless)."""
    import tkinter as tk
    from tkinter import messagebox, ttk

    from PIL import Image, ImageDraw, ImageTk

    try:
        # Carregar imagem com PIL
        pil_img = Image.open(input_path)
        w, h = pil_img.size

        # Calcular coordenadas do retângulo
        x1 = w - (box_w + off_x)
        y1 = h - (box_h + off_y)
        x2 = w - off_x
        y2 = h - off_y

        # Desenhar retângulo verde
        draw = ImageDraw.Draw(pil_img)
        draw.rectangle([x1, y1, x2, y2], outline='lime', width=3)

        # Redimensionar se muito grande
        max_h = 900
        if h > max_h:
            scale = max_h / h
            new_size = (int(w * scale), int(h * scale))
            pil_img = pil_img.resize(new_size, Image.Resampling.LANCZOS)

        # Criar janela Tkinter
        debug_win = tk.Toplevel()
        debug_win.title('DEBUG - Área de Assinatura')
        debug_win.attributes('-topmost', True)

        # Converter para PhotoImage
        photo = ImageTk.PhotoImage(pil_img)

        # Label com imagem
        label = ttk.Label(debug_win, image=photo)
        label.image = photo  # Manter referência
        label.pack(padx=5, pady=5)

        # Botão fechar
        ttk.Button(debug_win, text='Fechar', command=debug_win.destroy).pack(
            pady=5
        )

        # Centralizar janela
        debug_win.update_idletasks()
        win_w = debug_win.winfo_width()
        win_h = debug_win.winfo_height()
        screen_w = debug_win.winfo_screenwidth()
        screen_h = debug_win.winfo_screenheight()
        x = (screen_w - win_w) // 2
        y = (screen_h - win_h) // 2
        debug_win.geometry(f'+{x}+{y}')

    except Exception as e:
        logger.error(f'Erro ao mostrar debug: {e}')
        messagebox.showerror('Erro', f'Não foi possível mostrar debug: {e}')


# --- Função de Inspeção de Metadata ---
def inspect_metadata(input_path):
    logger.info(f'Inspecionando metadata: {input_path}')
    try:
        from PIL import ExifTags, Image
    except ImportError:
        return "Biblioteca 'Pillow' não instalada.\nRode: pip install Pillow"

    report = []
    try:
        with Image.open(input_path) as img:
            report.append(f'Formato: {img.format}')
            report.append(f'Modo: {img.mode}')
            report.append(f'Tamanho: {img.size}')

            if img.info:
                report.append('\n--- INFO GERAL ---')
                for k, v in img.info.items():
                    if k != 'exif':
                        val_str = str(v)
                        if len(val_str) > 100:
                            val_str = val_str[:100] + '...'
                        report.append(f'{k}: {val_str}')

            exif_data = img.getexif()
            if exif_data:
                report.append('\n--- EXIF ---')
                for tag_id, value in exif_data.items():
                    tag = ExifTags.TAGS.get(tag_id, tag_id)
                    if isinstance(value, bytes) and len(value) > 50:
                        value = '(Dados Binários)'
                    report.append(f'{tag}: {value}')
            else:
                report.append('\n(Sem EXIF)')

    except Exception as e:
        return f'Erro ao ler metadata: {e}'

    return '\n'.join(report)


# --- DESTRUIDOR de Metadata ---
def nuke_metadata(input_path):
    logger.info(f'Limpando metadata: {input_path}')
    try:
        from PIL import Image
    except ImportError:
        return None, 'Instale Pillow: pip install Pillow'

    try:
        img = Image.open(input_path)
        data = list(img.getdata())
        clean_img = Image.new(img.mode, img.size)
        clean_img.putdata(data)

        base, ext = os.path.splitext(input_path)
        output_path = f'{base}_no_meta{ext}'
        clean_img.save(output_path)
        return output_path, 'Sucesso'
    except Exception as e:
        return None, str(e)


# --- GUI ---
def open_gui():
    import tkinter as tk
    from tkinter import filedialog, messagebox, scrolledtext, ttk

    root = tk.Tk()
    root.title("V's Cleaner - Auto & Manual + Upscale & BG Remove")
    root.geometry('600x950')
    root.configure(bg='#1e1e1e')

    file_path_var = tk.StringVar()
    status_var = tk.StringVar(value='Selecione uma imagem.')

    # Variáveis de controle (Defaults iniciais)
    var_width = tk.IntVar(value=104)
    var_height = tk.IntVar(value=111)
    var_off_x = tk.IntVar(value=61)
    var_off_y = tk.IntVar(value=62)

    # Variáveis para novas funcionalidades
    var_alpha_matting = tk.BooleanVar(value=False)
    tk.BooleanVar(value=True)
    var_sharpen = tk.DoubleVar(value=0.3)  # Valor menor para Real-ESRGAN
    var_denoise = tk.BooleanVar(value=True)
    var_scale = tk.StringVar(value='4x')  # Escala do upscale
    var_face_enhance = tk.BooleanVar(value=False)  # GFPGAN para rostos

    # Sistema de tarefas em background
    background_task = BackgroundTask()
    pending_callback = [None]  # Lista para armazenar callback pendente

    style_lbl = {'bg': '#1e1e1e', 'fg': '#00ff00', 'font': ('Consolas', 9)}
    style_val = {
        'bg': '#333',
        'fg': 'white',
        'font': ('Consolas', 10),
        'width': 8,
    }
    style_btn = {
        'bg': '#444',
        'fg': 'white',
        'relief': 'flat',
        'activebackground': '#555',
    }

    # --- Barra de Progresso ---
    progress_frame = tk.Frame(root, bg='#1e1e1e')
    progress_bar = ttk.Progressbar(
        progress_frame,
        mode='indeterminate',
        length=400,
    )
    progress_label = tk.Label(
        progress_frame,
        text='',
        bg='#1e1e1e',
        fg='#ffcc00',
        font=('Consolas', 9),
    )

    def show_progress(message: str):
        """Mostra barra de progresso com mensagem."""
        progress_label.config(text=message)
        progress_frame.pack(pady=5, fill='x', padx=10)
        progress_bar.pack(pady=2)
        progress_label.pack()
        progress_bar.start(10)
        root.update()

    def hide_progress():
        """Esconde barra de progresso."""
        progress_bar.stop()
        progress_frame.pack_forget()
        root.update()

    def check_background_task():
        """Verifica se a tarefa em background terminou."""
        result = background_task.get_result()
        if result:
            hide_progress()
            status, data = result
            callback = pending_callback[0]
            if callback:
                callback(status, data)
                pending_callback[0] = None
            # Reabilitar botões
            set_buttons_state('normal')
        elif background_task.is_running:
            # Continua verificando
            root.after(100, check_background_task)

    def set_buttons_state(state: str):
        """Habilita/desabilita botões durante processamento."""
        for widget in root.winfo_children():
            if isinstance(widget, tk.Button):
                try:
                    widget.config(state=state)
                except tk.TclError:
                    pass
            elif isinstance(widget, (tk.Frame, tk.LabelFrame)):
                for child in widget.winfo_children():
                    if isinstance(child, tk.Button):
                        try:
                            child.config(state=state)
                        except tk.TclError:
                            pass
                    elif isinstance(child, tk.Frame):
                        for btn in child.winfo_children():
                            if isinstance(btn, tk.Button):
                                try:
                                    btn.config(state=state)
                                except tk.TclError:
                                    pass

    def run_in_background(func, args, kwargs, message, callback):
        """Executa função em background com feedback visual."""
        set_buttons_state('disabled')
        show_progress(message)
        pending_callback[0] = callback
        background_task.run(func, *args, **kwargs)
        root.after(100, check_background_task)

    def update_inputs(w, h, ox, oy):
        var_width.set(int(w))
        var_height.set(int(h))
        var_off_x.set(int(ox))
        var_off_y.set(int(oy))

    def launch_selector(*args):
        fpath = file_path_var.get()
        if not fpath:
            return
        try:
            sel = ROISelector(fpath)
            rect = sel.select()
            if rect:
                rx, ry, rw, rh = rect
                # Converte coordenadas absolutas para W/H e Offsets
                ox = sel.w_orig - (rx + rw)
                oy = sel.h_orig - (ry + rh)
                update_inputs(rw, rh, ox, oy)
                status_var.set('Seleção manual aplicada.')
        except Exception as e:
            messagebox.showerror('Erro', str(e))

    def show_meta_popup():
        fpath = file_path_var.get()
        if not fpath:
            return
        data = inspect_metadata(fpath)
        top = tk.Toplevel(root)
        top.title('Metadata')
        top.geometry('500x500')
        top.configure(bg='#2b2b2b')
        txt = scrolledtext.ScrolledText(
            top, width=60, height=30, bg='#1e1e1e', fg='#00ff00'
        )
        txt.pack(padx=10, pady=10, fill='both', expand=True)
        txt.insert(tk.END, data)
        txt.config(state=tk.DISABLED)

    def run_nuke_meta():
        fpath = file_path_var.get()
        if not fpath:
            return
        out, msg = nuke_metadata(fpath)
        if out:
            messagebox.showinfo(
                'Limpeza', f'Metadata removido!\n{os.path.basename(out)}'
            )
        else:
            messagebox.showerror('Erro', msg)

    def select_file():
        filename = filedialog.askopenfilename(
            filetypes=[
                ('Imagens', '*.png *.jpg *.jpeg *.bmp *.webp *.tiff'),
                ('Todos', '*.*'),
            ]
        )
        if filename:
            file_path_var.set(filename)
            status_var.set('Arquivo carregado. Tentando autodetecção...')

            # --- TENTATIVA DE AUTO DETECÇÃO ---
            detected = auto_detect_watermark(filename)
            if detected:
                w, h, ox, oy = detected
                update_inputs(w, h, ox, oy)
                status_var.set(
                    'Autodetecção: Marca encontrada! Confiança alta.'
                )
                messagebox.showinfo(
                    "V's AutoScan",
                    "Achei a marca d'água usando o template e atualizei as coordenadas. Confere no DEBUG se tá certo, Boss.",
                )
            else:
                status_var.set(
                    'Autodetecção falhou (Sem template ou marca não encontrada).'
                )

    def run_cleaner():
        fpath = file_path_var.get()
        if not fpath:
            return
        out, msg = remove_signature(
            input_path=fpath,
            box_w=var_width.get(),
            box_h=var_height.get(),
            off_x=var_off_x.get(),
            off_y=var_off_y.get(),
        )
        if out:
            messagebox.showinfo('Sucesso', f'Salvo: {out}')
        else:
            messagebox.showerror('Erro', msg)

    def run_remove_bg():
        """Executa remoção de fundo em background."""
        fpath = file_path_var.get()
        if not fpath:
            messagebox.showwarning('Aviso', 'Selecione uma imagem primeiro!')
            return

        def on_complete(status, data):
            if status == 'success':
                out, msg = data
                if out:
                    messagebox.showinfo(
                        'Sucesso', f'Fundo removido!\n{os.path.basename(out)}'
                    )
                    status_var.set(
                        f'✓ Fundo removido: {os.path.basename(out)}'
                    )
                else:
                    messagebox.showerror('Erro', msg)
                    status_var.set(f'✗ Erro: {msg}')
            else:
                messagebox.showerror('Erro', f'Falha no processamento: {data}')
                status_var.set(f'✗ Erro: {data}')

        run_in_background(
            remove_background,
            args=(fpath,),
            kwargs={'alpha_matting': var_alpha_matting.get()},
            message='🎨 Removendo fundo... (1ª vez baixa modelo ~170MB)',
            callback=on_complete,
        )

    def get_scale_factor():
        """Retorna o fator de escala baseado na seleção."""
        scale_map = {'2x': 2, '4x': 4}
        return scale_map.get(var_scale.get(), 4)

    def run_upscale_realesrgan():
        """Executa upscale com Real-ESRGAN em background."""
        fpath = file_path_var.get()
        if not fpath:
            messagebox.showwarning('Aviso', 'Selecione uma imagem primeiro!')
            return

        scale = get_scale_factor()

        def on_complete(status, data):
            if status == 'success':
                out, msg = data
                if out:
                    messagebox.showinfo(
                        'Sucesso',
                        f'Real-ESRGAN concluído!\n{os.path.basename(out)}',
                    )
                    status_var.set(
                        f'✓ Real-ESRGAN {scale}x: {os.path.basename(out)}'
                    )
                else:
                    messagebox.showerror('Erro', msg)
                    status_var.set(f'✗ Erro: {msg}')
            else:
                messagebox.showerror('Erro', f'Falha no processamento: {data}')

        run_in_background(
            upscale_with_enhancement,
            args=(fpath,),
            kwargs={
                'scale': scale,
                'sharpen_strength': var_sharpen.get(),
                'denoise': var_denoise.get(),
                'face_enhance': var_face_enhance.get(),
            },
            message=f'🚀 Real-ESRGAN {scale}x... (1ª vez baixa modelo ~65MB)',
            callback=on_complete,
        )

    def run_full_pipeline():
        """Executa pipeline completo em background."""
        fpath = file_path_var.get()
        if not fpath:
            messagebox.showwarning('Aviso', 'Selecione uma imagem primeiro!')
            return

        scale = get_scale_factor()

        def pipeline_worker(
            input_path,
            alpha_matting,
            scale_factor,
            sharpen,
            denoise,
            face_enhance,
        ):
            """Worker que executa o pipeline completo."""
            results = []
            current_file = input_path

            # 1. Remover fundo
            out, msg = remove_background(
                current_file, alpha_matting=alpha_matting
            )
            if out:
                results.append('✓ Fundo removido')
                current_file = out
            else:
                results.append(f'✗ Fundo: {msg}')

            # 2. Upscale com Real-ESRGAN
            out, msg = upscale_with_enhancement(
                current_file,
                scale=scale_factor,
                sharpen_strength=sharpen,
                denoise=denoise,
                face_enhance=face_enhance,
            )
            if out:
                results.append(f'✓ Real-ESRGAN {scale_factor}x')
                current_file = out
            else:
                results.append(f'✗ Upscale: {msg}')

            return results, current_file

        def on_complete(status, data):
            if status == 'success':
                results, final_file = data
                result_text = '\n'.join(results)
                messagebox.showinfo(
                    'Pipeline Completo',
                    f'Resultados:\n\n{result_text}\n\nArquivo final: {os.path.basename(final_file)}',
                )
                status_var.set('✓ Pipeline completo!')
            else:
                messagebox.showerror('Erro', f'Falha no pipeline: {data}')
                status_var.set(f'✗ Pipeline falhou: {data}')

        run_in_background(
            pipeline_worker,
            args=(
                fpath,
                var_alpha_matting.get(),
                scale,
                var_sharpen.get(),
                var_denoise.get(),
                var_face_enhance.get(),
            ),
            kwargs={},
            message='🚀 Pipeline: Removendo fundo + Real-ESRGAN... (pode demorar)',
            callback=on_complete,
        )

    # Layout
    frame_top = tk.Frame(root, bg='#1e1e1e')
    frame_top.pack(pady=10, fill='x', padx=10)
    tk.Button(
        frame_top, text='[1] ABRIR IMAGEM', command=select_file, **style_btn
    ).pack(side='left')
    tk.Entry(
        frame_top, textvariable=file_path_var, bg='#333', fg='#ddd', width=40
    ).pack(side='left', padx=5)

    # --- SEÇÃO: Marca d'água ---
    frame_watermark = tk.LabelFrame(
        root,
        text="🔲 Remoção de Marca D'água",
        bg='#1e1e1e',
        fg='white',
        padx=10,
        pady=10,
    )
    frame_watermark.pack(pady=5, fill='x', padx=10)

    frame_ctrl = tk.Frame(frame_watermark, bg='#1e1e1e')
    frame_ctrl.pack()

    tk.Label(frame_ctrl, text='W:', **style_lbl).grid(row=0, column=0)
    tk.Entry(frame_ctrl, textvariable=var_width, **style_val).grid(
        row=0, column=1
    )
    tk.Label(frame_ctrl, text='H:', **style_lbl).grid(row=0, column=2)
    tk.Entry(frame_ctrl, textvariable=var_height, **style_val).grid(
        row=0, column=3
    )
    tk.Label(frame_ctrl, text='OffX:', **style_lbl).grid(row=1, column=0)
    tk.Entry(frame_ctrl, textvariable=var_off_x, **style_val).grid(
        row=1, column=1
    )
    tk.Label(frame_ctrl, text='OffY:', **style_lbl).grid(row=1, column=2)
    tk.Entry(frame_ctrl, textvariable=var_off_y, **style_val).grid(
        row=1, column=3
    )

    frame_watermark_btns = tk.Frame(frame_watermark, bg='#1e1e1e')
    frame_watermark_btns.pack(pady=5)

    tk.Button(
        frame_watermark_btns,
        text='DEBUG',
        command=lambda: (
            show_debug_window(
                file_path_var.get(),
                var_width.get(),
                var_height.get(),
                var_off_x.get(),
                var_off_y.get(),
            )
            if file_path_var.get()
            else None
        ),
        bg='#d4ac0d',
        fg='black',
        width=12,
    ).pack(side='left', padx=2)

    tk.Button(
        frame_watermark_btns,
        text='SELECIONAR 🖱️',
        command=launch_selector,
        bg='#007acc',
        fg='white',
        width=15,
    ).pack(side='left', padx=2)

    tk.Button(
        frame_watermark_btns,
        text='LIMPAR MARCA',
        command=run_cleaner,
        bg='#922b21',
        fg='white',
        width=15,
    ).pack(side='left', padx=2)

    # --- SEÇÃO: Remoção de Fundo ---
    frame_bg = tk.LabelFrame(
        root,
        text='🎨 Remoção de Fundo (IA)',
        bg='#1e1e1e',
        fg='white',
        padx=10,
        pady=10,
    )
    frame_bg.pack(pady=5, fill='x', padx=10)

    frame_bg_opts = tk.Frame(frame_bg, bg='#1e1e1e')
    frame_bg_opts.pack()

    tk.Checkbutton(
        frame_bg_opts,
        text='Alpha Matting (bordas suaves - mais lento)',
        variable=var_alpha_matting,
        bg='#1e1e1e',
        fg='#00ff00',
        selectcolor='#333',
        activebackground='#1e1e1e',
    ).pack(anchor='w')

    tk.Label(
        frame_bg,
        text='⚠️ Primeira execução baixa modelo (~170MB)',
        bg='#1e1e1e',
        fg='#ff9800',
        font=('Consolas', 8),
    ).pack()

    tk.Button(
        frame_bg,
        text='⚡ REMOVER FUNDO',
        command=run_remove_bg,
        bg='#8e44ad',
        fg='white',
        font=('Arial', 10, 'bold'),
        width=35,
    ).pack(pady=5)

    # --- SEÇÃO: Upscale Real-ESRGAN ---
    frame_upscale = tk.LabelFrame(
        root,
        text='📐 Upscale Real-ESRGAN (IA Profissional)',
        bg='#1e1e1e',
        fg='white',
        padx=10,
        pady=10,
    )
    frame_upscale.pack(pady=5, fill='x', padx=10)

    frame_upscale_opts = tk.Frame(frame_upscale, bg='#1e1e1e')
    frame_upscale_opts.pack()

    tk.Label(frame_upscale_opts, text='Escala:', **style_lbl).grid(
        row=0, column=0
    )
    scale_combo = ttk.Combobox(
        frame_upscale_opts,
        textvariable=var_scale,
        values=['2x', '4x'],
        width=6,
        state='readonly',
    )
    scale_combo.grid(row=0, column=1, padx=5)

    tk.Checkbutton(
        frame_upscale_opts,
        text='Face Enhance (GFPGAN)',
        variable=var_face_enhance,
        bg='#1e1e1e',
        fg='#00ff00',
        selectcolor='#333',
    ).grid(row=0, column=2, padx=10)

    frame_upscale_opts2 = tk.Frame(frame_upscale, bg='#1e1e1e')
    frame_upscale_opts2.pack(pady=5)

    tk.Label(frame_upscale_opts2, text='Sharpening:', **style_lbl).pack(
        side='left'
    )
    sharpen_scale = tk.Scale(
        frame_upscale_opts2,
        variable=var_sharpen,
        from_=0.0,
        to=1.0,
        resolution=0.1,
        orient='horizontal',
        bg='#333',
        fg='#00ff00',
        highlightthickness=0,
        length=120,
    )
    sharpen_scale.pack(side='left', padx=5)

    tk.Checkbutton(
        frame_upscale_opts2,
        text='Denoise',
        variable=var_denoise,
        bg='#1e1e1e',
        fg='#00ff00',
        selectcolor='#333',
    ).pack(side='left', padx=5)

    tk.Label(
        frame_upscale,
        text='⚠️ Primeira execução baixa modelo (~65MB). GPU acelera muito!',
        bg='#1e1e1e',
        fg='#ff9800',
        font=('Consolas', 8),
    ).pack()

    tk.Button(
        frame_upscale,
        text='🚀 EXECUTAR REAL-ESRGAN',
        command=run_upscale_realesrgan,
        bg='#2980b9',
        fg='white',
        font=('Arial', 10, 'bold'),
        width=35,
    ).pack(pady=5)

    # --- SEÇÃO: Metadata ---
    frame_meta = tk.LabelFrame(
        root, text='📋 Metadata', bg='#1e1e1e', fg='white', padx=10, pady=10
    )
    frame_meta.pack(pady=5, fill='x', padx=10)

    frame_meta_btns = tk.Frame(frame_meta, bg='#1e1e1e')
    frame_meta_btns.pack()

    tk.Button(
        frame_meta_btns,
        text='INSPECIONAR',
        command=show_meta_popup,
        bg='#5bc0de',
        fg='black',
        width=18,
    ).pack(side='left', padx=2)

    tk.Button(
        frame_meta_btns,
        text='DESTRUIR METADATA',
        command=run_nuke_meta,
        bg='#555',
        fg='white',
        width=18,
    ).pack(side='left', padx=2)

    # --- SEÇÃO: Pipeline Completo ---
    frame_pipeline = tk.LabelFrame(
        root,
        text='🚀 Pipeline Completo',
        bg='#1e1e1e',
        fg='white',
        padx=10,
        pady=10,
    )
    frame_pipeline.pack(pady=5, fill='x', padx=10)

    tk.Label(
        frame_pipeline,
        text='Executa: Remover Fundo → Real-ESRGAN Upscale',
        bg='#1e1e1e',
        fg='#888',
        font=('Consolas', 8),
    ).pack()

    tk.Button(
        frame_pipeline,
        text='⚡ EXECUTAR PIPELINE COMPLETO ⚡',
        command=run_full_pipeline,
        bg='#c0392b',
        fg='white',
        font=('Arial', 11, 'bold'),
        width=40,
        pady=8,
    ).pack(pady=5)

    tk.Label(root, textvariable=status_var, **style_lbl).pack(
        side='bottom', pady=5
    )

    root.mainloop()


if __name__ == '__main__':
    try:
        open_gui()
    except Exception as e:
        logger.critical(f'GUI Crash: {e}')
