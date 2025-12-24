import bluetooth
from micropython import const

_IRQ_CENTRAL_CONNECT    = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE        = const(3)

# Nordic UART Service UUIDs
_UART_SERVICE_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_TX_UUID      = bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E")  # notify
_UART_RX_UUID      = bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E")  # write

_UART_TX = (_UART_TX_UUID, bluetooth.FLAG_NOTIFY)
_UART_RX = (_UART_RX_UUID, bluetooth.FLAG_WRITE)

_UART_SERVICE = (_UART_SERVICE_UUID, (_UART_TX, _UART_RX))


class BLEUART:
    def __init__(self, ble, name="PicoEcho"):
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(self._irq)

        ((self._tx_handle, self._rx_handle),) = self._ble.gatts_register_services(
            (_UART_SERVICE,)
        )

        self._connections = set()
        self._rx_cb = None

        self._name = name
        self._adv_payload = self._build_adv_payload(name)
        self._advertise()

    def _build_adv_payload(self, name):
        name_bytes = bytes(name, "utf-8")
        payload = bytearray()
        # Flags: LE only, general discoverable
        payload.extend(b"\x02\x01\x06")
        # Complete Local Name
        payload.extend(bytes((len(name_bytes) + 1, 0x09)))
        payload.extend(name_bytes)
        return bytes(payload)

    def _advertise(self):
        # Advertise indefinitely every 100 ms
        self._ble.gap_advertise(100_000, adv_data=self._adv_payload)

    def _irq(self, event, data):
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            print("BLE: central connected", conn_handle)
            self._connections.add(conn_handle)

        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            print("BLE: central disconnected", conn_handle)
            if conn_handle in self._connections:
                self._connections.remove(conn_handle)
            # Restart advertising
            self._advertise()

        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            if value_handle == self._rx_handle:
                msg = self._ble.gatts_read(self._rx_handle)
                if self._rx_cb:
                    self._rx_cb(msg)

    def on_rx(self, callback):
        self._rx_cb = callback

    def send(self, data):
        if isinstance(data, str):
            data = data.encode()

        for conn_handle in self._connections:
            try:
                self._ble.gatts_notify(conn_handle, self._tx_handle, data)
            except Exception as e:
                print("BLE notify error:", e)

    def is_connected(self):
        return bool(self._connections)

