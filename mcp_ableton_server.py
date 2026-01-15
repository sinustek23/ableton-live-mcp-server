# mcp_ableton_server.py
"""
MCP Server for Ableton Live Controller.
Provides MCP tools for interacting with Ableton Live via OSC daemon.
Cross-platform compatible (Windows, macOS, Linux).
"""
import asyncio
import json
import logging
import os
import socket
import sys
from typing import List, Optional

from mcp.server.fastmcp import FastMCP

# Configure logging for cross-platform compatibility
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger(__name__)

# Configuration via environment variables with sensible defaults
DEFAULT_DAEMON_HOST = '127.0.0.1'
DEFAULT_DAEMON_PORT = 65432
DEFAULT_TIMEOUT = 5.0


class AbletonClient:
    """
    Client for communicating with the Ableton OSC Daemon.

    Supports configuration via environment variables:
        - ABLETON_DAEMON_HOST: OSC daemon host (default: 127.0.0.1)
        - ABLETON_DAEMON_PORT: OSC daemon port (default: 65432)
        - ABLETON_TIMEOUT: Response timeout in seconds (default: 5.0)
    """

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        timeout: Optional[float] = None
    ):
        # Load configuration from environment variables with fallback to defaults
        self.host = host or os.environ.get(
            'ABLETON_DAEMON_HOST', DEFAULT_DAEMON_HOST
        )
        self.port = port or int(os.environ.get(
            'ABLETON_DAEMON_PORT', DEFAULT_DAEMON_PORT
        ))
        self.timeout = timeout or float(os.environ.get(
            'ABLETON_TIMEOUT', DEFAULT_TIMEOUT
        ))

        self.sock: Optional[socket.socket] = None
        self.connected = False
        self.responses: dict = {}  # Store futures keyed by request_id
        self.lock = asyncio.Lock()
        self._request_id = 0  # Counter for unique request IDs

        # Task for reading responses asynchronously
        self.response_task: Optional[asyncio.Task] = None

    def _create_socket(self) -> socket.socket:
        """Create a new socket with cross-platform options."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Set socket options for cross-platform compatibility
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        # Set timeout for blocking operations
        sock.settimeout(self.timeout)
        return sock

    async def start_response_reader(self) -> None:
        """Background task to read responses from the socket."""
        if self.sock is None:
            return

        # Convert socket to async streams
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        loop = asyncio.get_running_loop()
        await loop.create_connection(lambda: protocol, sock=self.sock)

        while self.connected:
            try:
                data = await reader.read(4096)
                if not data:
                    # Connection closed
                    break

                try:
                    # Explicit UTF-8 encoding for cross-platform compatibility
                    msg = json.loads(data.decode('utf-8'))
                except json.JSONDecodeError:
                    logger.warning("Invalid JSON from daemon")
                    continue

                # Check for JSON-RPC response
                resp_id = msg.get('id')
                if 'result' in msg or 'error' in msg:
                    # Response to a request
                    async with self.lock:
                        fut = self.responses.pop(resp_id, None)
                    if fut and not fut.done():
                        fut.set_result(msg)
                else:
                    # OSC notification or other message type
                    if msg.get('type') == 'osc_response':
                        address = msg.get('address')
                        args = msg.get('args')
                        await self.handle_osc_response(address, args)
                    else:
                        logger.debug(f"Unknown message: {msg}")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error reading response: {e}")
                break

        self.connected = False

    async def handle_osc_response(self, address: str, args: list) -> None:
        """Callback when receiving OSC message from Ableton."""
        logger.info(f"OSC Notification from {address}: {args}")

    def connect(self) -> bool:
        """Connect to the OSC daemon via TCP socket."""
        if self.connected:
            return True

        try:
            self.sock = self._create_socket()
            self.sock.connect((self.host, self.port))
            self.sock.setblocking(False)  # Non-blocking for async operations
            self.connected = True

            # Start the response reader task
            self.response_task = asyncio.create_task(self.start_response_reader())
            logger.info(f"Connected to daemon at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to daemon: {e}")
            if self.sock:
                self.sock.close()
                self.sock = None
            return False

    async def send_rpc_request(self, method: str, params: dict) -> dict:
        """
        Send a JSON-RPC request and wait for response.

        Args:
            method: The RPC method name
            params: Dictionary of parameters

        Returns:
            Response dictionary with 'status' and 'result' or 'message'
        """
        if not self.connected:
            if not self.connect():
                return {'status': 'error', 'message': 'Not connected to daemon'}

        if self.sock is None:
            return {'status': 'error', 'message': 'Socket not initialized'}

        # Generate unique request ID
        self._request_id += 1
        request_id = str(self._request_id)

        # Build JSON-RPC request
        request_obj = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params
        }

        future: asyncio.Future = asyncio.Future()
        async with self.lock:
            self.responses[request_id] = future

        try:
            # Explicit UTF-8 encoding for cross-platform compatibility
            self.sock.sendall(json.dumps(request_obj).encode('utf-8'))

            # Wait for JSON-RPC response
            try:
                msg = await asyncio.wait_for(future, timeout=self.timeout)
            except asyncio.TimeoutError:
                async with self.lock:
                    self.responses.pop(request_id, None)
                return {'status': 'error', 'message': 'Response timeout'}

            # Check for result or error
            if 'error' in msg:
                return {
                    'status': 'error',
                    'code': msg['error'].get('code'),
                    'message': msg['error'].get('message')
                }
            else:
                return {
                    'status': 'ok',
                    'result': msg.get('result')
                }

        except Exception as e:
            self.connected = False
            logger.error(f"Error sending request: {e}")
            return {'status': 'error', 'message': str(e)}

    async def close(self) -> None:
        """Close the connection gracefully."""
        if not self.connected:
            return

        self.connected = False

        if self.response_task:
            self.response_task.cancel()
            try:
                await self.response_task
            except asyncio.CancelledError:
                pass

        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
            self.sock = None

        logger.info("Connection closed")


# Initialize the MCP server
mcp = FastMCP("Ableton Live Controller", dependencies=["python-osc"])

# Create Ableton client (lazily initialized)
ableton_client = AbletonClient()


# ----- MCP TOOLS -----

@mcp.tool()
async def get_track_names(
    index_min: Optional[int] = None,
    index_max: Optional[int] = None
) -> str:
    """
    Get the names of tracks in Ableton Live.

    Args:
        index_min: Optional minimum track index
        index_max: Optional maximum track index

    Returns:
        A formatted string containing track names
    """
    params = {
        "address": "/live/song/get/track_names",
        "args": [index_min, index_max] if index_min is not None and index_max is not None else []
    }

    response = await ableton_client.send_rpc_request("send_message", params)

    if response['status'] == 'ok':
        result = response.get('result', {})
        # Handle different response formats
        if isinstance(result, dict):
            track_data = result.get('data') or result.get('status')
            if track_data:
                return f"Track Names: {track_data}"
        elif isinstance(result, list):
            return f"Track Names: {', '.join(str(t) for t in result)}"
        return "No tracks found"
    else:
        return f"Error getting track names: {response.get('message', 'Unknown error')}"


@mcp.tool()
async def get_daemon_status() -> str:
    """
    Get the status of the Ableton OSC daemon.

    Returns:
        A formatted string with daemon connection status
    """
    params = {"command": "get_status"}

    response = await ableton_client.send_rpc_request("get_status", params)

    if response['status'] == 'ok':
        result = response.get('result', {})
        return f"Daemon Status: Connected\n{json.dumps(result, indent=2)}"
    else:
        return f"Daemon Status: Error - {response.get('message', 'Unknown error')}"


def main() -> None:
    """Main entry point for the MCP server."""
    try:
        mcp.run()
    except KeyboardInterrupt:
        logger.info("MCP server stopped by user")
    finally:
        # Cleanup
        try:
            asyncio.run(ableton_client.close())
        except Exception:
            pass


if __name__ == "__main__":
    main()
