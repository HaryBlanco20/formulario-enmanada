#!/usr/bin/env python3
"""Genera iconos PWA simples (cuadrado verde GymVe). Requiere: pip install pillow."""

from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    raise SystemExit("Instala Pillow: pip install pillow")

OUT = Path(__file__).resolve().parents[1] / "app" / "static"
BG = (0x2D, 0x4A, 0x3E)


def make(size: int) -> None:
    img = Image.new("RGB", (size, size), BG)
    draw = ImageDraw.Draw(img)
    text = "GV"
    font_size = max(size // 3, 12)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except OSError:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((size - tw) / 2, (size - th) / 2 - 2), text, fill=(255, 255, 255), font=font)
    img.save(OUT / f"icon-{size}.png")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    make(192)
    make(512)
    print("Iconos escritos en", OUT)


if __name__ == "__main__":
    main()
