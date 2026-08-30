import socket
import pytest


def test_can_connect_to_open_port():
    """A known-open port (google.com:80) should accept a TCP connection."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    try:
        sock.connect(("google.com", 80))
        connected = True
    except Exception:
        connected = False
    finally:
        sock.close()

    assert connected is True


def test_connection_to_closed_port_fails():
    """A port nothing is listening on should not connect successfully."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    with pytest.raises(socket.timeout):
        sock.connect(("google.com", 12345))
    sock.close()