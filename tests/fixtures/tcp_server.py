"""Small local TCP server used only by the integration suite."""

import socket
import threading


class LocalTCPServer:
    """Accept local connections and optionally return a fixed response."""

    def __init__(self, response: bytes = b"PONG") -> None:
        self.host = "127.0.0.1"
        self.response = response
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind((self.host, 0))
        self._socket.listen()
        self._socket.settimeout(0.1)
        self.port = self._socket.getsockname()[1]
        self._stopped = threading.Event()
        self._thread = threading.Thread(target=self._serve, daemon=True)

    def start(self) -> None:
        self._thread.start()

    def _serve(self) -> None:
        while not self._stopped.is_set():
            try:
                connection, _ = self._socket.accept()
            except TimeoutError:
                continue
            except OSError:
                return
            with connection:
                connection.settimeout(0.5)
                try:
                    request = connection.recv(65_536)
                except TimeoutError:
                    continue
                if request and self.response:
                    connection.sendall(self.response)

    def stop(self) -> None:
        self._stopped.set()
        self._socket.close()
        self._thread.join(timeout=1)
