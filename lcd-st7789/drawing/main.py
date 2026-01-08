from machine import Pin, SPI
import st7789py as st7789
import vga1_8x8 as font
import time

# --------------------
# SPI configuration
# --------------------
spi = SPI(
    1,
    baudrate=40_000_000,
    polarity=1,
    phase=1,
    sck=Pin(10),
    mosi=Pin(11)
)

dc  = Pin(8, Pin.OUT)
rst = Pin(12, Pin.OUT)

# Optional backlight control
bl = Pin(13, Pin.OUT)
bl.value(1)

# --------------------
# Create display
# --------------------
tft = st7789.ST7789(
    spi,
    240,
    240,
    reset=rst,
    dc=dc,
    cs=None,                 # no CS pin
    rotation=0,
    color_order=st7789.BGR   # change to RGB if colours look wrong
)

# --------------------
# Drawing demo
# --------------------
tft.fill(st7789.BLACK)

# Filled rectangle
tft.fill_rect(20, 20, 80, 40, st7789.RED)

# Rectangle outline
tft.rect(120, 20, 80, 40, st7789.GREEN)

# Horizontal line
tft.hline(20, 80, 200, st7789.YELLOW)

# Vertical line
tft.vline(120, 80, 100, st7789.CYAN)

# Circle (outline)
tft.circle(120, 170, 30, st7789.WHITE)

# Filled circle
tft.fill_circle(50, 170, 20, st7789.BLUE)

# Text
tft.text(font, "Drawing demo", 40, 210, st7789.WHITE)

while True:
    time.sleep(1)

