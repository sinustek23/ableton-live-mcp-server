"""
CollabNet Client - WebSocket client for collaborative music production

Verbindet den Avatar mit dem CollabNet Server und ermöglicht
Echtzeit-Synchronisation von Ableton-Aktionen mit anderen Users.
"""

import asyncio
import json
import uuid
from typing import Optional, Callable, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime

try:
    import websockets
    from websockets.client import WebSocketClientProtocol
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    print("[CollabNetClient] Warning: websockets not available")

from daiw.network.collabnet_server import ActionType, CollaborativeAction


@dataclass
class RemoteUser:
    """Represents a remote user in the session"""
    user_id: str
    username: str
    color: str
    is_host: bool = False
    last_action: Optional[CollaborativeAction] = None


class CollabNetClient:
    """
    WebSocket client for connecting to CollabNet server
    """

    def __init__(self, username: str = "Producer", color: str = "#00ff00"):
        self.username = username
        self.color = color

        # Connection
        self._websocket: Optional[WebSocketClientProtocol] = None
        self._connected = False
        self._user_id: Optional[str] = None

        # Session
        self._current_session_id: Optional[str] = None
        self._current_session_name: Optional[str] = None
        self._remote_users: Dict[str, RemoteUser] = {}
        self._is_host = False

        # Callbacks
        self._action_callbacks: List[Callable] = []
        self._user_join_callbacks: List[Callable] = []
        self._user_leave_callbacks: List[Callable] = []
        self._session_update_callbacks: List[Callable] = []

        # Message queue for outgoing actions
        self._action_queue: asyncio.Queue = asyncio.Queue()

        # Background tasks
        self._receive_task: Optional[asyncio.Task] = None
        self._send_task: Optional[asyncio.Task] = None

    async def connect(self, server_url: str = "ws://localhost:8765") -> bool:
        """
        Connect to CollabNet server

        Args:
            server_url: WebSocket server URL

        Returns:
            True if connected successfully
        """
        if not WEBSOCKETS_AVAILABLE:
            print("[CollabNetClient] websockets not available")
            return False

        try:
            print(f"[CollabNetClient] Connecting to {server_url}")

            self._websocket = await websockets.connect(server_url)

            # Authenticate
            auth_msg = {
                "type": "auth",
                "username": self.username,
                "color": self.color
            }

            await self._websocket.send(json.dumps(auth_msg))

            # Wait for auth response
            response = await self._websocket.recv()
            data = json.loads(response)

            if data.get("type") == "auth_success":
                self._user_id = data["user_id"]
                self._connected = True

                print(f"[CollabNetClient] ✅ Connected as {self.username} ({self._user_id[:8]})")

                # Start background tasks
                self._receive_task = asyncio.create_task(self._receive_loop())
                self._send_task = asyncio.create_task(self._send_loop())

                return True
            else:
                print(f"[CollabNetClient] Authentication failed: {data}")
                return False

        except Exception as e:
            print(f"[CollabNetClient] Connection failed: {e}")
            return False

    async def disconnect(self) -> None:
        """Disconnect from server"""
        self._connected = False

        # Cancel background tasks
        if self._receive_task and not self._receive_task.done():
            self._receive_task.cancel()

        if self._send_task and not self._send_task.done():
            self._send_task.cancel()

        # Close websocket
        if self._websocket:
            await self._websocket.close()

        print("[CollabNetClient] Disconnected")

    def is_connected(self) -> bool:
        """Check if connected"""
        return self._connected

    def is_in_session(self) -> bool:
        """Check if currently in a session"""
        return self._current_session_id is not None

    # ========== Session Management ==========

    async def create_session(
        self,
        session_name: str,
        password: Optional[str] = None,
        max_users: int = 8
    ) -> bool:
        """
        Create a new collaboration session

        Args:
            session_name: Name of the session
            password: Optional password protection
            max_users: Maximum number of users

        Returns:
            True if created successfully
        """
        if not self._connected:
            print("[CollabNetClient] Not connected")
            return False

        try:
            await self._websocket.send(json.dumps({
                "type": "create_session",
                "session_name": session_name,
                "password": password,
                "max_users": max_users
            }))

            return True

        except Exception as e:
            print(f"[CollabNetClient] Error creating session: {e}")
            return False

    async def join_session(
        self,
        session_id: str,
        password: Optional[str] = None
    ) -> bool:
        """
        Join an existing session

        Args:
            session_id: ID of the session to join
            password: Optional password if required

        Returns:
            True if joined successfully
        """
        if not self._connected:
            print("[CollabNetClient] Not connected")
            return False

        try:
            await self._websocket.send(json.dumps({
                "type": "join_session",
                "session_id": session_id,
                "password": password
            }))

            return True

        except Exception as e:
            print(f"[CollabNetClient] Error joining session: {e}")
            return False

    async def leave_session(self) -> bool:
        """Leave current session"""
        if not self._current_session_id:
            return False

        try:
            await self._websocket.send(json.dumps({
                "type": "leave_session",
                "session_id": self._current_session_id
            }))

            self._current_session_id = None
            self._current_session_name = None
            self._remote_users.clear()
            self._is_host = False

            return True

        except Exception as e:
            print(f"[CollabNetClient] Error leaving session: {e}")
            return False

    async def list_sessions(self) -> None:
        """Request list of available sessions"""
        if not self._connected:
            return

        try:
            await self._websocket.send(json.dumps({
                "type": "list_sessions"
            }))

        except Exception as e:
            print(f"[CollabNetClient] Error listing sessions: {e}")

    # ========== Action Synchronization ==========

    async def send_action(self, action_type: ActionType, data: Dict[str, Any]) -> None:
        """
        Send a collaborative action

        Args:
            action_type: Type of action
            data: Action data
        """
        if not self._current_session_id:
            return

        action = CollaborativeAction(
            action_type=action_type,
            user_id=self._user_id or "",
            data=data
        )

        # Add to queue
        await self._action_queue.put(action)

    async def send_midi_note(self, note: int, velocity: int, duration: float) -> None:
        """Send MIDI note action"""
        await self.send_action(ActionType.MIDI_NOTE_ON, {
            "note": note,
            "velocity": velocity,
            "duration": duration
        })

    async def send_tempo_change(self, tempo: float) -> None:
        """Send tempo change action"""
        await self.send_action(ActionType.TEMPO_CHANGE, {"tempo": tempo})

    async def send_mode_change(self, mode: str) -> None:
        """Send mode change action"""
        await self.send_action(ActionType.MODE_CHANGE, {"mode": mode})

    async def send_chat_message(self, message: str) -> None:
        """Send chat message"""
        await self.send_action(ActionType.CHAT_MESSAGE, {"message": message})

    # ========== Background Tasks ==========

    async def _receive_loop(self) -> None:
        """Background task for receiving messages"""
        try:
            async for message in self._websocket:
                await self._handle_message(message)

        except websockets.exceptions.ConnectionClosed:
            print("[CollabNetClient] Connection closed")
            self._connected = False
        except Exception as e:
            print(f"[CollabNetClient] Receive error: {e}")

    async def _send_loop(self) -> None:
        """Background task for sending queued actions"""
        while self._connected:
            try:
                # Get action from queue (with timeout)
                action = await asyncio.wait_for(
                    self._action_queue.get(),
                    timeout=1.0
                )

                # Send to server
                await self._websocket.send(json.dumps({
                    "type": "action",
                    "session_id": self._current_session_id,
                    "action": action.to_dict()
                }))

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"[CollabNetClient] Send error: {e}")

    async def _handle_message(self, message: str) -> None:
        """Handle incoming message from server"""
        try:
            data = json.loads(message)
            msg_type = data.get("type")

            if msg_type == "session_created":
                self._handle_session_created(data)

            elif msg_type == "session_joined":
                self._handle_session_joined(data)

            elif msg_type == "action":
                await self._handle_action(data)

            elif msg_type == "sessions_list":
                self._handle_sessions_list(data)

            elif msg_type == "error":
                print(f"[CollabNetClient] Server error: {data.get('message')}")

        except json.JSONDecodeError:
            print(f"[CollabNetClient] Invalid JSON: {message}")
        except Exception as e:
            print(f"[CollabNetClient] Error handling message: {e}")

    def _handle_session_created(self, data: dict) -> None:
        """Handle session created response"""
        self._current_session_id = data["session_id"]
        self._current_session_name = data["session_name"]
        self._is_host = True

        print(f"[CollabNetClient] ✅ Session created: {self._current_session_name}")

        # Notify callbacks
        for callback in self._session_update_callbacks:
            asyncio.create_task(callback("created", data))

    def _handle_session_joined(self, data: dict) -> None:
        """Handle session joined response"""
        self._current_session_id = data["session_id"]
        self._current_session_name = data["session_name"]

        # Update remote users
        self._remote_users.clear()
        for user_data in data.get("users", []):
            if user_data["user_id"] != self._user_id:
                self._remote_users[user_data["user_id"]] = RemoteUser(
                    user_id=user_data["user_id"],
                    username=user_data["username"],
                    color=user_data["color"],
                    is_host=user_data["is_host"]
                )

        print(f"[CollabNetClient] ✅ Joined session: {self._current_session_name}")
        print(f"[CollabNetClient] Remote users: {[u.username for u in self._remote_users.values()]}")

        # Notify callbacks
        for callback in self._session_update_callbacks:
            asyncio.create_task(callback("joined", data))

    async def _handle_action(self, data: dict) -> None:
        """Handle incoming collaborative action"""
        action = CollaborativeAction.from_dict(data["action"])

        # Special handling for user join/leave
        if action.action_type == ActionType.USER_JOIN:
            user_id = action.user_id
            self._remote_users[user_id] = RemoteUser(
                user_id=user_id,
                username=action.data["username"],
                color=action.data["color"]
            )

            print(f"[CollabNetClient] 👤 {action.data['username']} joined")

            # Notify callbacks
            for callback in self._user_join_callbacks:
                await callback(user_id, action.data["username"], action.data["color"])

        elif action.action_type == ActionType.USER_LEAVE:
            user_id = action.user_id
            username = action.data.get("username", "Unknown")

            if user_id in self._remote_users:
                del self._remote_users[user_id]

            print(f"[CollabNetClient] 👤 {username} left")

            # Notify callbacks
            for callback in self._user_leave_callbacks:
                await callback(user_id, username)

        else:
            # Regular action - update last action for user
            if action.user_id in self._remote_users:
                self._remote_users[action.user_id].last_action = action

            # Notify action callbacks
            for callback in self._action_callbacks:
                await callback(action)

    def _handle_sessions_list(self, data: dict) -> None:
        """Handle sessions list response"""
        sessions = data.get("sessions", [])

        print(f"[CollabNetClient] Available sessions ({len(sessions)}):")
        for session in sessions:
            print(f"  - {session['session_name']} ({session['user_count']}/{session['max_users']}) - Host: {session['host']}")

        # Notify callbacks
        for callback in self._session_update_callbacks:
            asyncio.create_task(callback("list", data))

    # ========== Callbacks ==========

    def add_action_callback(self, callback: Callable) -> None:
        """Add callback for incoming actions"""
        self._action_callbacks.append(callback)

    def add_user_join_callback(self, callback: Callable) -> None:
        """Add callback for user joins"""
        self._user_join_callbacks.append(callback)

    def add_user_leave_callback(self, callback: Callable) -> None:
        """Add callback for user leaves"""
        self._user_leave_callbacks.append(callback)

    def add_session_update_callback(self, callback: Callable) -> None:
        """Add callback for session updates"""
        self._session_update_callbacks.append(callback)

    # ========== Getters ==========

    def get_current_session(self) -> Optional[tuple]:
        """Get current session info"""
        if self._current_session_id:
            return (self._current_session_id, self._current_session_name)
        return None

    def get_remote_users(self) -> List[RemoteUser]:
        """Get list of remote users"""
        return list(self._remote_users.values())

    def get_user_id(self) -> Optional[str]:
        """Get own user ID"""
        return self._user_id


# Example usage
async def _example_usage():
    """Example usage of CollabNetClient"""
    client = CollabNetClient(username="TestProducer", color="#ff0000")

    # Connect
    if await client.connect("ws://localhost:8765"):
        # Create session
        await client.create_session("Test Session", password="1234")

        await asyncio.sleep(1)

        # Send some actions
        await client.send_midi_note(60, 100, 0.5)
        await client.send_tempo_change(120.0)
        await client.send_chat_message("Hello from client!")

        await asyncio.sleep(5)

        # Disconnect
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(_example_usage())
