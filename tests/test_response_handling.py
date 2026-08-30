import socket
import pytest
from tests.echo_server import EchoServer


@pytest.fixture
def echo_server():
    """Starts a local echo server before the test, stops it after."""
    server = EchoServer()
    server.start()
    yield server
    server.stop()


@pytest.fixture
def client_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    yield sock
    sock.close()


def test_server_echoes_sent_data(echo_server, client_socket):
    """Data sent to the echo server should be returned unchanged."""
    client_socket.connect((echo_server.host, echo_server.port))
    message = b"Hello, network!"

    client_socket.sendall(message)
    response = client_socket.recv(1024)

    assert response == message


def test_server_response_is_not_empty(echo_server, client_socket):
    """Server should return some data, not an empty response, for valid input."""
    client_socket.connect((echo_server.host, echo_server.port))
    client_socket.sendall(b"ping")

    response = client_socket.recv(1024)

    assert len(response) > 0