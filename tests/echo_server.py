import socket
import threading


class EchoServer:
    """A minimal TCP server that echoes back whatever it receives.
    Used only for testing — not part of the framework's 'production' logic."""

    def __init__(self, host="127.0.0.1", port=0):
        self.host = host
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen(1)
        self.port = self.server_socket.getsockname()[1]  # actual port assigned
        self._thread = None
        self._running = False

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        while self._running:
            try:
                self.server_socket.settimeout(1)
                conn, _ = self.server_socket.accept()
                data = conn.recv(1024)
                conn.sendall(data)  # echo it back
                conn.close()
            except socket.timeout:
                continue
            except OSError:
                break

    def stop(self):
        self._running = False
        self.server_socket.close()