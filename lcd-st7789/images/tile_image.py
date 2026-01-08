from PIL import Image
from pathlib import Path
import math

TILE = 64

def rgb888_to_rgb565(r, g, b) -> int:
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)

def save_tile_rgb565(tile_img: Image.Image, out_path: Path) -> None:
    tile_img = tile_img.convert("RGB")
    w, h = tile_img.size
    px = tile_img.load()

    data = bytearray(w * h * 2)
    i = 0
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            c = rgb888_to_rgb565(r, g, b)
            data[i] = (c >> 8) & 0xFF  # big-endian
            data[i + 1] = c & 0xFF
            i += 2

    out_path.write_bytes(data)

def main(png_path: str, out_dir: str = "tiles"):
    img = Image.open(png_path).convert("RGB")
    w, h = img.size

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    cols = math.ceil(w / TILE)
    rows = math.ceil(h / TILE)

    # Write a simple manifest for the Pico
    (out / "manifest.txt").write_text(
        f"{w},{h},{TILE},{cols},{rows}\n", encoding="utf-8"
    )

    for ty in range(rows):
        for tx in range(cols):
            x0 = tx * TILE
            y0 = ty * TILE
            tw = min(TILE, w - x0)
            th = min(TILE, h - y0)

            tile = img.crop((x0, y0, x0 + tw, y0 + th))
            # filename includes tile position and size
            fname = f"t_{tx}_{ty}_{tw}x{th}.rgb565"
            save_tile_rgb565(tile, out / fname)

    print(f"Done. Wrote {cols*rows} tiles to: {out.resolve()}")
    print("Copy the whole 'tiles' folder to the Pico.")

if __name__ == "__main__":
    main("tinkimo-logo-240x240.png")
