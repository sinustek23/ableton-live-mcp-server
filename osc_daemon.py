# osc_daemon.py
"""
OSC Daemon for Ableton Live MCP Server.
Bridges MCP server and Ableton Live via OSC protocol.
Cross-platform compatible (Windows, macOS, Linux).
"""
import asyncio
import json
import logging
import os
import signal
import sys
from typing import Dict, Optional

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient

# Configure logging for cross-platform compatibility
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Configuration via environment variables with sensible defaults
DEFAULT_SOCKET_HOST = '127.0.0.1'
DEFAULT_SOCKET_PORT = 65432
DEFAULT_ABLETON_HOST = '127.0.0.1'
DEFAULT_ABLETON_PORT = 11000
DEFAULT_RECEIVE_PORT = 11001
DEFAULT_TIMEOUT = 5.0


class AbletonOSCDaemon:
    """
    OSC Daemon handling communication between MCP server and Ableton Live.

    Supports configuration via environment variables:
        - ABLETON_SOCKET_HOST: Host for MCP socket server (default: 127.0.0.1)
        - ABLETON_SOCKET_PORT: Port for MCP socket server (default: 65432)
        - ABLETON_OSC_HOST: Ableton Live OSC host (default: 127.0.0.1)
        - ABLETON_OSC_PORT: Ableton Live OSC send port (default: 11000)
        - ABLETON_RECEIVE_PORT: OSC receive port (default: 11001)
        - ABLETON_TIMEOUT: Response timeout in seconds (default: 5.0)
    """

    def __init__(
        self,
        socket_host: Optional[str] = None,
        socket_port: Optional[int] = None,
        ableton_host: Optional[str] = None,
        ableton_port: Optional[int] = None,
        receive_port: Optional[int] = None,
        timeout: Optional[float] = None
    ):
        # Load configuration from environment variables with fallback to defaults
        self.socket_host = socket_host or os.environ.get(
            'ABLETON_SOCKET_HOST', DEFAULT_SOCKET_HOST
        )
        self.socket_port = socket_port or int(os.environ.get(
            'ABLETON_SOCKET_PORT', DEFAULT_SOCKET_PORT
        ))
        self.ableton_host = ableton_host or os.environ.get(
            'ABLETON_OSC_HOST', DEFAULT_ABLETON_HOST
        )
        self.ableton_port = ableton_port or int(os.environ.get(
            'ABLETON_OSC_PORT', DEFAULT_ABLETON_PORT
        ))
        self.receive_port = receive_port or int(os.environ.get(
            'ABLETON_RECEIVE_PORT', DEFAULT_RECEIVE_PORT
        ))
        self.timeout = timeout or float(os.environ.get(
            'ABLETON_TIMEOUT', DEFAULT_TIMEOUT
        ))

        # Initialize OSC client for Ableton
        self.osc_client = SimpleUDPClient(self.ableton_host, self.ableton_port)

        # Store active connections waiting for responses
        self.pending_responses: Dict[str, asyncio.Future] = {}

        # Initialize OSC server dispatcher
        self.dispatcher = Dispatcher()
        self.dispatcher.set_default_handler(self.handle_ableton_message)

        # Server references for graceful shutdown
        self.osc_server = None
        self.tcp_server = None
        self._shutdown_event = asyncio.Event()

    def handle_ableton_message(self, address: str, *args) -> None:
        """Handle incoming OSC messages from Ableton."""
        logger.info(f"[ABLETON MESSAGE] Address: {address}, Args: {args}")

        # If this address has a pending response, resolve it
        if address in self.pending_responses:
            future = self.pending_responses[address]
            if not future.done():
                future.set_result({
                    'status': 'success',
                    'address': address,
                    'data': args
                })
            del self.pending_responses[address]

    async def start(self) -> None:
        """Start both the socket server and OSC server."""
        # Set up signal handlers for graceful shutdown (cross-platform)
        self._setup_signal_handlers()

        # Start OSC server to receive Ableton messages
        # Use get_running_loop() for Python 3.10+ compatibility
        loop = asyncio.get_running_loop()
        self.osc_server = AsyncIOOSCUDPServer(
            (self.socket_host, self.receive_port),
            self.dispatcher,
            loop
        )
        await self.osc_server.create_serve_endpoint()

        # Start socket server for MCP communication
        self.tcp_server = await asyncio.start_server(
            self.handle_socket_client,
            self.socket_host,
            self.socket_port,
            reuse_address=True  # Cross-platform socket reuse
        )

        logger.info(f"Ableton OSC Daemon listening on {self.socket_host}:{self.socket_port}")
        logger.info(f"OSC Server receiving on {self.socket_host}:{self.receive_port}")
        logger.info(f"Sending to Ableton on {self.ableton_host}:{self.ableton_port}")

        try:
            async with self.tcp_server:
                await self.tcp_server.serve_forever()
        except asyncio.CancelledError:
            logger.info("Server shutdown requested")
        finally:
            await self.shutdown()

    def _setup_signal_handlers(self) -> None:
        """Set up signal handlers for graceful shutdown on all platforms."""
        loop = asyncio.get_running_loop()

        # SIGINT and SIGTERM work on all platforms
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(
                    sig,
                    lambda s=sig: asyncio.create_task(self._handle_signal(s))
                )
            except NotImplementedError:
                # Windows doesn't support add_signal_handler for all signals
                # Fall back to signal.signal for Windows compatibility
                signal.signal(sig, lambda s, f: asyncio.create_task(self._handle_signal(s)))

    async def _handle_signal(self, sig: signal.Signals) -> None:
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {sig.name}, initiating graceful shutdown...")
        self._shutdown_event.set()
        if self.tcp_server:
            self.tcp_server.close()

    async def shutdown(self) -> None:
        """Gracefully shutdown all servers and connections."""
        logger.info("Shutting down daemon...")

        # Cancel all pending responses
        for address, future in list(self.pending_responses.items()):
            if not future.done():
                future.cancel()
        self.pending_responses.clear()

        # Close TCP server
        if self.tcp_server:
            self.tcp_server.close()
            await self.tcp_server.wait_closed()

        logger.info("Daemon shutdown complete")

    async def handle_socket_client(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter
    ) -> None:
        """Handle incoming socket connections from MCP server."""
        client_address = writer.get_extra_info('peername')
        logger.info(f"[NEW CONNECTION] Client connected from {client_address}")

        try:
            while True:
                data = await reader.read(1024)
                if not data:
                    break

                try:
                    # Explicit UTF-8 encoding for cross-platform compatibility
                    message = json.loads(data.decode('utf-8'))
                    logger.debug(f"[RECEIVED MESSAGE] From {client_address}: {message}")

                    response = await self._process_message(message)

                    # Explicit UTF-8 encoding for response
                    writer.write(json.dumps(response).encode('utf-8'))
                    await writer.drain()

                except json.JSONDecodeError as e:
                    logger.warning(f"[JSON ERROR] Could not decode message: {data!r}, error: {e}")
                    response = {'status': 'error', 'message': 'Invalid JSON'}
                    writer.write(json.dumps(response).encode('utf-8'))
                    await writer.drain()

        except ConnectionResetError:
            logger.warning(f"[CONNECTION RESET] Client {client_address} connection reset")
        except Exception as e:
            logger.error(f"[CONNECTION ERROR] Error handling client: {e}", exc_info=True)
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass  # Ignore errors during close
            logger.info(f"[CONNECTION CLOSED] Client {client_address} disconnected")

    async def _process_message(self, message: dict) -> dict:
        """Process incoming JSON message and return response."""
        command = message.get('command')

        # Support both 'command' and JSON-RPC 'method' format
        if not command:
            method = message.get('method')
            if method:
                command = method
                message['command'] = method
                if 'params' in message:
                    message.update(message['params'])

        if command == 'send_message':
            return await self._handle_send_message(message)
        elif command == 'get_status':
            return self._handle_get_status(message)
        else:
            logger.warning(f"[UNKNOWN COMMAND] Received: {message}")
            return {'status': 'error', 'message': f'Unknown command: {command}'}

    async def _handle_send_message(self, message: dict) -> dict:
        """Handle send_message command."""
        address = message.get('address')
        args = message.get('args', [])

        if not address:
            return {'status': 'error', 'message': 'Missing address parameter'}

        # Addresses that expect responses from Ableton
        response_prefixes = (
            '/live/device/get',
            '/live/scene/get',
            '/live/view/get',
            '/live/clip/get',
            '/live/clip_slot/get',
            '/live/track/get',
            '/live/song/get',
            '/live/api/get',
            '/live/application/get',
            '/live/test',
            '/live/error'
        )

        if address.startswith(response_prefixes):
            return await self._send_with_response(address, args)
        else:
            return self._send_without_response(address, args)

    async def _send_with_response(self, address: str, args: list) -> dict:
        """Send OSC message and wait for response."""
        future: asyncio.Future = asyncio.Future()
        self.pending_responses[address] = future

        try:
            # Send to Ableton
            self.osc_client.send_message(address, args)

            # Wait for response with timeout
            response = await asyncio.wait_for(future, timeout=self.timeout)
            logger.debug(f"[OSC RESPONSE] Received: {response}")
            return response

        except asyncio.TimeoutError:
            # Clean up pending response
            self.pending_responses.pop(address, None)
            response = {
                'status': 'error',
                'message': f'Timeout waiting for response to {address}'
            }
            logger.warning(f"[OSC TIMEOUT] {response}")
            return response
        except Exception as e:
            self.pending_responses.pop(address, None)
            logger.error(f"[OSC ERROR] Error sending message: {e}")
            return {'status': 'error', 'message': str(e)}

    def _send_without_response(self, address: str, args: list) -> dict:
        """Send OSC message without waiting for response."""
        try:
            self.osc_client.send_message(address, args)
            return {'status': 'sent'}
        except Exception as e:
            logger.error(f"[OSC ERROR] Error sending message: {e}")
            return {'status': 'error', 'message': str(e)}

    def _handle_get_status(self, message: dict) -> dict:
        """Handle get_status command."""
        response = {
            'status': 'ok',
            'ableton_host': self.ableton_host,
            'ableton_port': self.ableton_port,
            'receive_port': self.receive_port,
            'socket_host': self.socket_host,
            'socket_port': self.socket_port
        }
        logger.debug(f"[STATUS REQUEST] Responding with: {response}")
        return response


def main() -> None:
    """Main entry point for the OSC daemon."""
    daemon = AbletonOSCDaemon()

    try:
        asyncio.run(daemon.start())
    except KeyboardInterrupt:
        logger.info("Daemon stopped by user")


if __name__ == "__main__":
    main()
