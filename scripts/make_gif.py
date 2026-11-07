import os
import glob
from PIL import Image

def generate_optimized_gif(
    frames_dir: str = "docs/frames",
    output_path: str = "docs/demo.gif",
    target_width: int = 380,
    fps: int = 5,
    max_colors: int = 128
):
    frames_paths = sorted(glob.glob(os.path.join(frames_dir, "*.png")))
    if not frames_paths:
        print(f"No frames found in {frames_dir}")
        return False

    print(f"Processing {len(frames_paths)} frames for GIF...")
    processed_images = []

    for i, fp in enumerate(frames_paths):
        img = Image.open(fp).convert("RGB")
        w, h = img.size
        target_height = int(h * (target_width / w))
        img_resized = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
        
        quantized = img_resized.quantize(colors=max_colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG)
        processed_images.append(quantized)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    duration_ms = 450

    print(f"Saving GIF to {output_path} (width={target_width}px, colors={max_colors})...")
    processed_images[0].save(
        output_path,
        save_all=True,
        append_images=processed_images[1:],
        optimize=True,
        duration=duration_ms,
        loop=0
    )

    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"GIF created successfully! File size: {size_mb:.2f} MB")
    return True

if __name__ == "__main__":
    generate_optimized_gif()
