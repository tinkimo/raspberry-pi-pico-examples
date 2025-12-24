from machine import Pin, I2C
from pico_i2c_lcd import I2cLcd
from time import sleep

I2C_ADDR = 0x27
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16

i2c = I2C(sda=Pin(0), scl=Pin(1), freq=400000)
lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)

while True:
    lcd.blink_cursor_on()
        
    lcd.clear()
    sleep(1)
    
    lcd.blink_cursor_off()
    lcd.putstr("  Hello from")
    lcd.move_to(0, 1)
    lcd.putstr("  Tinkimo <3")
    sleep(1)

