import asyncio
import json
from bleak import BleakClient, BleakScanner

# Nordic UART Service UUIDs (must match the Pico side)
UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
UART_TX_UUID      = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"  # notify (Pico -> PC)
UART_RX_UUID      = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"  # write  (PC -> Pico)


async def main():
    print("Scanning for PicoRobot...")
    device = None

    # Scan for BLE devices
    devices = await BleakScanner.discover(timeout=10.0)
    for d in devices:
        # Debug print if you want to see everything:
        # print(d)
        if d.name and "PicoRobot" in d.name:
            device = d
            break

    if device is None:
        print("PicoRobot not found. Make sure:")
        print(" - The Pico W is powered and running main.py")
        print(" - It is advertising as 'PicoRobot'")
        print(" - Your PC's Bluetooth is turned on")
        return

    print("Connecting to", device)

    async with BleakClient(device) as client:
        # is_connected is a property now, not an async method
        print("Connected:", client.is_connected)

        # Callback for telemetry/state notifications from the Pico
        def handle_notify(_, data: bytearray):
            text = data.decode(errors="ignore")
            for line in text.splitlines():
                if not line:
                    continue
                try:
                    state = json.loads(line)
                    print("State:", state)
                except Exception as e:
                    print("Parse error:", e, "raw:", line)

        # Start receiving notifications
        await client.start_notify(UART_TX_UUID, handle_notify)

        print("Commands:")
        print("  speed <v> <omega>")
        print("     e.g. speed 0.3 0.0")
        print("  mode <NAME>")
        print("     e.g. mode AUTO")
        print("  stop")
        print("  quit")

        # Simple REPL loop for sending commands
        while True:
            try:
                line = input("> ").strip()
            except (EOFError, KeyboardInterrupt):
                break

            if line == "quit":
                break

            if line.startswith("speed"):
                parts = line.split()
                if len(parts) != 3:
                    print("Usage: speed <v> <omega>")
                    continue
                _, v, w = parts
                cmd = {"cmd": "SET_SPEED", "v": float(v), "omega": float(w)}

            elif line.startswith("mode"):
                parts = line.split()
                if len(parts) != 2:
                    print("Usage: mode <NAME>")
                    continue
                _, m = parts
                cmd = {"cmd": "SET_MODE", "mode": m}

            elif line == "stop":
                cmd = {"cmd": "STOP"}

            else:
                print("Unknown command. Try: speed, mode, stop, quit")
                continue

            msg = (json.dumps(cmd) + "\n").encode()
            try:
                await client.write_gatt_char(UART_RX_UUID, msg)
            except Exception as e:
                print("Write failed:", e)
                break

        # Stop notifications before exiting
        try:
            await client.stop_notify(UART_TX_UUID)
        except Exception:
            pass

        print("Disconnected.")


if __name__ == "__main__":
    asyncio.run(main())
