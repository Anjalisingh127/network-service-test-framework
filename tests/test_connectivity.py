import socket
import pytest


@pytest.fixture
def tcp_socket():
    """Provides a fresh TCP socket for each test, and guarantees it's closed afterward."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    yield sock          # test runs here, using this socket
    sock.close()         # runs after the test, even if it fails


@pytest.mark.parametrize("host,port", [
    ("google.com", 80),
    ("google.com", 443),
])
def test_known_open_ports_connect_successfully(tcp_socket, host, port):
    """Well-known open ports (HTTP, HTTPS) should accept TCP connections."""
    try:
        tcp_socket.connect((host, port))
        connected = True
    except Exception:
        connected = False

    assert connected is True


def test_closed_port_times_out(tcp_socket):
    """An unused high-numbered port should not respond, causing a timeout."""
    with pytest.raises(socket.timeout):
        tcp_socket.connect(("google.com", 12345))