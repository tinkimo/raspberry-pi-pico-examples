from machine import Pin, SPI
import st7789py as st7789
import time
import os
import random

# ---- SPI pins (adjust to your wiring) ----
spi = SPI(1, baudrate=40_000_000, polarity=1, phase=1,
          sck=Pin(10), mosi=Pin(11))

dc  = Pin(8, Pin.OUT)
rst = Pin(12, Pin.OUT)

tft = st7789.ST7789(spi, 240, 240, reset=rst, dc=dc, cs=None, rotation=0)
tft.fill(st7789.BLACK)

TILES_DIR = "tiles"

def shuffle_list(lst):
    # Fisher–Yates shuffle (MicroPython-safe)
    for i in range(len(lst) - 1, 0, -1):
        j = random.randint(0, i)
        lst[i], lst[j] = lst[j], lst[i]
        
def parse_tile_filename(fn):
    # Expected: t_TX_TY_WxH.rgb565  e.g. t_3_1_64x64.rgb565
    if not (fn.startswith("t_") and fn.endswith(".rgb565")):
        return None

    base = fn[:-7]  # strip ".rgb565"
    parts = base.split("_")  # ["t", "3", "1", "64x64"]
    if len(parts) != 4:
        return None

    try:
        tx = int(parts[1])
        ty = int(parts[2])
        w_str, h_str = parts[3].split("x")
        tw = int(w_str)
        th = int(h_str)
        return tx, ty, tw, th
    except:
        return None

def draw_tiled_image_random():
    # Read manifest: "w,h,tile,cols,rows"
    with open(f"{TILES_DIR}/manifest.txt", "r") as f:
        disp_w, disp_h, tile, cols, rows = [int(x) for x in f.readline().strip().split(",")]
    # Build a list of all tile jobs
    jobs = []
    for fn in os.listdir(TILES_DIR):
        info = parse_tile_filename(fn)
        if info is None:
            continue
        tx, ty, tw, th = info
        x0 = tx * tile
        y0 = ty * tile
        jobs.append((fn, x0, y0, tw, th))

    if not jobs:
        raise OSError("No tile files found in /tiles")

    # Shuffle for random load order
    random.seed(time.ticks_ms())
    shuffle_list(jobs)

    # Draw each tile in random order
    for fn, x0, y0, tw, th in jobs:
        buf = bytearray(tw * th * 2)
        with open(f"{TILES_DIR}/{fn}", "rb") as f:
            f.readinto(buf)

        tft.blit_buffer(buf, x0, y0, tw, th)

draw_tiled_image_random()

while True:
    time.sleep(1)

