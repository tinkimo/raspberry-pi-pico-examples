import bluetooth
import time
from ble_uart import BLEUART

print("main.py starting (echo demo)...")

ble = bluetooth.BLE()
uart = BLEUART(ble, name="PicoEcho")  # this is the BLE name

_last_connected = False  # simple state flag


def handle_rx(data: bytes):
    """Called whenever data arrives over BLE."""
    try:
        text = data.decode("utf-8", "ignore")
    except Exception as e:
        print("Decode error:", e)
        return

    print("RX from PC:", repr(text))

    # Echo it straight back (prefix so you can see it’s from Pico)
    reply = "ECHO: " + text
    print("TX to PC:", repr(reply))
    uart.send(reply)


uart.on_rx(handle_rx)

print("Advertising as PicoEcho")

loop_count = 0
while True:
    loop_count += 1

    # Just a heartbeat so you know it's alive
    if loop_count % 20 == 0:
        print("loop heartbeat, connected =", uart.is_connected())

    connected = uart.is_connected()
    if connected != _last_connected:
        print("Connection state changed. Connected:", connected)
        _last_connected = connected

    time.sleep(0.1)

