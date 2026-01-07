from machine import Pin, SPI
import st7789py as st7789
import vga1_8x8 as font
import time

# --- SPI wiring example (change GPIOs to match your wiring) ---
# SCK  -> GP10
# MOSI -> GP11
# DC   -> GP8
# RST  -> GP12
# BL   -> (optional) GP13 or tie to 3V3

spi = SPI(
    1,
    baudrate=40_000_000,
    polarity=1,
    phase=1,
    sck=Pin(10),
    mosi=Pin(11),
)

dc  = Pin(8, Pin.OUT)
rst = Pin(12, Pin.OUT)

# Optional backlight pin (or comment out and wire BL to 3V3)
bl = Pin(13, Pin.OUT)
bl.value(1)

# Create display object (cs=None because your board has no CS pin)
tft = st7789.ST7789(
    spi,
    240,
    240,
    reset=rst,
    dc=dc,
    cs=None,
    backlight=bl,   # can be omitted if you don't use BL on a GPIO
    rotation=0,
    color_order=st7789.BGR,  # many modules are BGR; if colors look wrong, try st7789.RGB
)

# Clear and draw text
tft.fill(st7789.BLACK)
tft.text(font, "Hello Lucy!", 40, 120, st7789.WHITE, st7789.BLACK)

while True:
    time.sleep(1)

