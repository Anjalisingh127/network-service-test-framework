"""Integration-test fixtures."""

from collections.abc import Iterator

import pytest

from ..fixtures.tcp_server import LocalTCPServer


@pytest.fixture
def local_tcp_server() -> Iterator[LocalTCPServer]:
    server = LocalTCPServer()
    server.start()
    yield server
    server.stop()
