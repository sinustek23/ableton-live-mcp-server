# tests/test_platform_compatibility.py
"""
Cross-platform compatibility tests for Ableton Live MCP Server.
These tests verify that the code works correctly on Windows, macOS, and Linux.
"""
import asyncio
import json
import os
import platform
import signal
import socket
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestEnvironmentConfiguration:
    """Test environment variable configuration."""

    def test_osc_daemon_default_values(self):
        """Test that OSC daemon uses correct default values."""
        from osc_daemon import (
            DEFAULT_SOCKET_HOST,
            DEFAULT_SOCKET_PORT,
            DEFAULT_ABLETON_HOST,
            DEFAULT_ABLETON_PORT,
            DEFAULT_RECEIVE_PORT,
            DEFAULT_TIMEOUT,
        )

        assert DEFAULT_SOCKET_HOST == '127.0.0.1'
        assert DEFAULT_SOCKET_PORT == 65432
        assert DEFAULT_ABLETON_HOST == '127.0.0.1'
        assert DEFAULT_ABLETON_PORT == 11000
        assert DEFAULT_RECEIVE_PORT == 11001
        assert DEFAULT_TIMEOUT == 5.0

    def test_mcp_server_default_values(self):
        """Test that MCP server uses correct default values."""
        from mcp_ableton_server import (
            DEFAULT_DAEMON_HOST,
            DEFAULT_DAEMON_PORT,
            DEFAULT_TIMEOUT,
        )

        assert DEFAULT_DAEMON_HOST == '127.0.0.1'
        assert DEFAULT_DAEMON_PORT == 65432
        assert DEFAULT_TIMEOUT == 5.0

    def test_osc_daemon_env_configuration(self):
        """Test OSC daemon reads environment variables."""
        with patch.dict(os.environ, {
            'ABLETON_SOCKET_HOST': '0.0.0.0',
            'ABLETON_SOCKET_PORT': '9999',
            'ABLETON_OSC_HOST': '192.168.1.100',
            'ABLETON_OSC_PORT': '12000',
            'ABLETON_RECEIVE_PORT': '12001',
            'ABLETON_TIMEOUT': '10.0',
        }):
            from osc_daemon import AbletonOSCDaemon
            daemon = AbletonOSCDaemon()

            assert daemon.socket_host == '0.0.0.0'
            assert daemon.socket_port == 9999
            assert daemon.ableton_host == '192.168.1.100'
            assert daemon.ableton_port == 12000
            assert daemon.receive_port == 12001
            assert daemon.timeout == 10.0

    def test_ableton_client_env_configuration(self):
        """Test Ableton client reads environment variables."""
        with patch.dict(os.environ, {
            'ABLETON_DAEMON_HOST': '192.168.1.50',
            'ABLETON_DAEMON_PORT': '8888',
            'ABLETON_TIMEOUT': '15.0',
        }):
            from mcp_ableton_server import AbletonClient
            client = AbletonClient()

            assert client.host == '192.168.1.50'
            assert client.port == 8888
            assert client.timeout == 15.0


class TestUTF8Encoding:
    """Test UTF-8 encoding for cross-platform text handling."""

    def test_json_encode_utf8(self):
        """Test JSON encoding with UTF-8 special characters."""
        test_data = {
            'track_name': 'Sänger Track 日本語',
            'status': 'ok',
            'symbols': '♪♫♬'
        }

        encoded = json.dumps(test_data).encode('utf-8')
        decoded = json.loads(encoded.decode('utf-8'))

        assert decoded == test_data
        assert decoded['track_name'] == 'Sänger Track 日本語'
        assert decoded['symbols'] == '♪♫♬'

    def test_unicode_track_names(self):
        """Test handling of Unicode track names."""
        track_names = [
            'Track 1',
            'Пианино',  # Russian
            '钢琴',     # Chinese
            'ピアノ',   # Japanese
            'Klänge',   # German
            '🎹🎵🎶',  # Emojis
        ]

        for name in track_names:
            encoded = name.encode('utf-8')
            decoded = encoded.decode('utf-8')
            assert decoded == name


class TestSocketCreation:
    """Test socket creation and options."""

    def test_socket_creation(self):
        """Test socket is created with correct options."""
        from mcp_ableton_server import AbletonClient

        client = AbletonClient()
        sock = client._create_socket()

        assert sock.family == socket.AF_INET
        assert sock.type == socket.SOCK_STREAM

        # Verify SO_KEEPALIVE is set
        keepalive = sock.getsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE)
        assert keepalive == 1

        sock.close()

    def test_socket_ipv4_compatibility(self):
        """Test IPv4 socket works on all platforms."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Should not raise on any platform
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
        assert port > 0

        sock.close()


class TestAsyncioCompatibility:
    """Test asyncio compatibility across platforms."""

    @pytest.mark.asyncio
    async def test_get_running_loop(self):
        """Test asyncio.get_running_loop() works correctly."""
        loop = asyncio.get_running_loop()
        assert loop is not None
        assert loop.is_running()

    @pytest.mark.asyncio
    async def test_async_future(self):
        """Test asyncio.Future works correctly."""
        future = asyncio.Future()
        assert not future.done()

        future.set_result({'status': 'ok'})
        assert future.done()
        assert future.result() == {'status': 'ok'}

    @pytest.mark.asyncio
    async def test_async_lock(self):
        """Test asyncio.Lock works correctly."""
        lock = asyncio.Lock()

        async with lock:
            assert lock.locked()

        assert not lock.locked()

    @pytest.mark.asyncio
    async def test_wait_for_timeout(self):
        """Test asyncio.wait_for timeout handling."""
        async def slow_task():
            await asyncio.sleep(10)
            return "done"

        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(slow_task(), timeout=0.1)


class TestSignalHandling:
    """Test signal handling across platforms."""

    def test_sigint_exists(self):
        """Test SIGINT signal exists on all platforms."""
        assert hasattr(signal, 'SIGINT')
        assert signal.SIGINT is not None

    def test_sigterm_exists(self):
        """Test SIGTERM signal exists on all platforms."""
        assert hasattr(signal, 'SIGTERM')
        assert signal.SIGTERM is not None

    @pytest.mark.skipif(
        sys.platform == 'win32',
        reason="add_signal_handler not supported on Windows"
    )
    @pytest.mark.asyncio
    async def test_signal_handler_unix(self):
        """Test signal handler registration on Unix-like systems."""
        loop = asyncio.get_running_loop()
        handler_called = asyncio.Event()

        def handler():
            handler_called.set()

        # Should not raise on Unix
        loop.add_signal_handler(signal.SIGUSR1, handler)
        loop.remove_signal_handler(signal.SIGUSR1)


class TestPlatformDetection:
    """Test platform detection utilities."""

    def test_platform_system(self):
        """Test platform.system() returns valid value."""
        system = platform.system()
        assert system in ('Windows', 'Linux', 'Darwin')

    def test_sys_platform(self):
        """Test sys.platform returns valid value."""
        assert sys.platform in ('win32', 'linux', 'darwin')


class TestOSCDaemonMethods:
    """Test OSC daemon methods."""

    def test_daemon_initialization(self):
        """Test daemon initializes correctly."""
        from osc_daemon import AbletonOSCDaemon

        daemon = AbletonOSCDaemon(
            socket_host='127.0.0.1',
            socket_port=65432,
            ableton_host='127.0.0.1',
            ableton_port=11000,
            receive_port=11001,
            timeout=5.0
        )

        assert daemon.socket_host == '127.0.0.1'
        assert daemon.socket_port == 65432
        assert daemon.pending_responses == {}
        assert daemon.osc_server is None
        assert daemon.tcp_server is None

    def test_handle_ableton_message(self):
        """Test handling of Ableton messages."""
        from osc_daemon import AbletonOSCDaemon

        daemon = AbletonOSCDaemon()

        # Create a pending response
        future = asyncio.Future()
        daemon.pending_responses['/live/song/get/track_names'] = future

        # Simulate receiving a message
        daemon.handle_ableton_message('/live/song/get/track_names', 'Track1', 'Track2')

        assert future.done()
        result = future.result()
        assert result['status'] == 'success'
        assert result['address'] == '/live/song/get/track_names'
        assert result['data'] == ('Track1', 'Track2')

    @pytest.mark.asyncio
    async def test_process_message_unknown_command(self):
        """Test handling of unknown commands."""
        from osc_daemon import AbletonOSCDaemon

        daemon = AbletonOSCDaemon()
        response = await daemon._process_message({'command': 'unknown'})

        assert response['status'] == 'error'
        assert 'Unknown command' in response['message']

    def test_handle_get_status(self):
        """Test get_status command response."""
        from osc_daemon import AbletonOSCDaemon

        daemon = AbletonOSCDaemon(
            socket_host='127.0.0.1',
            socket_port=65432,
            ableton_host='192.168.1.100',
            ableton_port=11000,
            receive_port=11001
        )

        response = daemon._handle_get_status({})

        assert response['status'] == 'ok'
        assert response['socket_host'] == '127.0.0.1'
        assert response['socket_port'] == 65432
        assert response['ableton_host'] == '192.168.1.100'
        assert response['ableton_port'] == 11000
        assert response['receive_port'] == 11001


class TestAbletonClient:
    """Test Ableton client methods."""

    def test_client_initialization(self):
        """Test client initializes correctly."""
        from mcp_ableton_server import AbletonClient

        client = AbletonClient(
            host='127.0.0.1',
            port=65432,
            timeout=5.0
        )

        assert client.host == '127.0.0.1'
        assert client.port == 65432
        assert client.timeout == 5.0
        assert client.connected is False
        assert client.sock is None

    @pytest.mark.asyncio
    async def test_send_rpc_request_not_connected(self):
        """Test RPC request when not connected."""
        from mcp_ableton_server import AbletonClient

        client = AbletonClient()

        # Mock connect to return False
        with patch.object(client, 'connect', return_value=False):
            response = await client.send_rpc_request('test', {})

        assert response['status'] == 'error'
        assert 'Not connected' in response['message']

    @pytest.mark.asyncio
    async def test_close_not_connected(self):
        """Test close when not connected."""
        from mcp_ableton_server import AbletonClient

        client = AbletonClient()

        # Should not raise
        await client.close()

        assert client.connected is False
        assert client.sock is None


class TestLogging:
    """Test logging configuration."""

    def test_logging_format(self):
        """Test logging is configured correctly."""
        import logging

        # Both modules should have loggers
        mcp_logger = logging.getLogger('mcp_ableton_server')
        daemon_logger = logging.getLogger('osc_daemon')

        assert mcp_logger is not None
        assert daemon_logger is not None

    def test_logger_level(self):
        """Test logger level can be configured."""
        import logging

        logger = logging.getLogger('test_logger')
        logger.setLevel(logging.DEBUG)

        assert logger.level == logging.DEBUG

        logger.setLevel(logging.WARNING)
        assert logger.level == logging.WARNING


class TestJSONRPCProtocol:
    """Test JSON-RPC protocol handling."""

    def test_jsonrpc_request_format(self):
        """Test JSON-RPC request format."""
        request = {
            "jsonrpc": "2.0",
            "id": "1",
            "method": "send_message",
            "params": {
                "address": "/live/song/get/track_names",
                "args": []
            }
        }

        assert request["jsonrpc"] == "2.0"
        assert "id" in request
        assert "method" in request
        assert "params" in request

    def test_jsonrpc_response_format(self):
        """Test JSON-RPC response formats."""
        success_response = {
            "jsonrpc": "2.0",
            "id": "1",
            "result": {"status": "ok", "data": ["Track1", "Track2"]}
        }

        error_response = {
            "jsonrpc": "2.0",
            "id": "1",
            "error": {"code": -32600, "message": "Invalid Request"}
        }

        assert "result" in success_response
        assert "error" in error_response


class TestCrossPlatformPaths:
    """Test that no platform-specific paths are hardcoded."""

    def test_no_hardcoded_paths_in_daemon(self):
        """Verify no hardcoded file paths in daemon."""
        with open('osc_daemon.py', 'r', encoding='utf-8') as f:
            content = f.read()

        # Should not contain Windows paths
        assert 'C:\\' not in content
        assert '%APPDATA%' not in content

        # Should not contain Unix absolute paths (except in comments/docstrings)
        # Note: /live/ is an OSC address, not a file path
        lines = content.split('\n')
        for line in lines:
            if not line.strip().startswith('#') and not line.strip().startswith('"'):
                # Skip OSC addresses
                if '/live/' not in line:
                    assert '/Users/' not in line
                    assert '/home/' not in line

    def test_no_hardcoded_paths_in_server(self):
        """Verify no hardcoded file paths in server."""
        with open('mcp_ableton_server.py', 'r', encoding='utf-8') as f:
            content = f.read()

        # Should not contain Windows paths
        assert 'C:\\' not in content
        assert '%APPDATA%' not in content

        # Should not contain Unix absolute paths (except in comments/docstrings)
        lines = content.split('\n')
        for line in lines:
            if not line.strip().startswith('#') and not line.strip().startswith('"'):
                # Skip OSC addresses
                if '/live/' not in line:
                    assert '/Users/' not in line
                    assert '/home/' not in line
