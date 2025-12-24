import asyncio
from bleak import BleakClient, BleakScanner

UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
UART_TX_UUID      = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"  # notify from Pico
UART_RX_UUID      = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"  # write to Pico


async def main():
    print("Scanning for PicoEcho...")
    device = None

    devices = await BleakScanner.discover(timeout=10.0)
    for d in devices:
        print("Found device:", d)  # debug
        if d.name and "PicoEcho" in d.name:
            device = d
            break

    if device is None:
        print("PicoEcho not found. Is the Pico running and advertising?")
        return

    print("Connecting to", device)

    async with BleakClient(device) as client:
        print("Connected:", client.is_connected)

        def handle_notify(_, data: bytearray):
            text = data.decode(errors="ignore")
            print("From Pico:", repr(text))

        # Start notifications from Pico
        await client.start_notify(UART_TX_UUID, handle_notify)

        print("Type messages to send to Pico.")
        print("Type 'quit' to exit.\n")

        while True:
            try:
                line = input("> ")
            except (EOFError, KeyboardInterrupt):
                break

            if line.strip().lower() == "quit":
                break

            # Send line + newline to Pico
            msg = (line + "\n").encode()
            await client.write_gatt_char(UART_RX_UUID, msg)

        try:
            await client.stop_notify(UART_TX_UUID)
        except Exception:
            pass

        print("Disconnected.")


if __name__ == "__main__":
    asyncio.run(main())
