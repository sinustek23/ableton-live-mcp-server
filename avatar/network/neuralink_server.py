"""
Neuralink Server - WebSocket server for collaborative music production

Ermöglicht Echtzeit-Zusammenarbeit zwischen mehreren Music Copilot Avatar Instances
über WAN (Wide Area Network). Alle Ableton-Aktionen werden synchronisiert.
"""

import asyncio
import json
import uuid
from typing import Dict, Set, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum

try:
    import websockets
    from websockets.server import WebSocketServerProtocol
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    print("[NeuralinkServer] Warning: websockets not available")


class ActionType(Enum):
    """Types of collaborative actions"""
    # MIDI Actions
    MIDI_NOTE_ON = "midi_note_on"
    MIDI_NOTE_OFF = "midi_note_off"
    MIDI_CC = "midi_cc"

    # Ableton Actions
    TEMPO_CHANGE = "tempo_change"
    TRACK_MUTE = "track_mute"
    TRACK_SOLO = "track_solo"
    TRACK_ARM = "track_arm"
    SCENE_TRIGGER = "scene_trigger"
    CLIP_TRIGGER = "clip_trigger"

    # Avatar Actions
    MODE_CHANGE = "mode_change"
    FEATURE_USE = "feature_use"

    # Chat
    CHAT_MESSAGE = "chat_message"

    # Session Control
    USER_JOIN = "user_join"
    USER_LEAVE = "user_leave"
    USER_CURSOR = "user_cursor"


@dataclass
class CollaborativeAction:
    """Represents a collaborative action"""
    action_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    action_type: ActionType = ActionType.CHAT_MESSAGE
    user_id: str = ""
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())
    data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "action_id": self.action_id,
            "action_type": self.action_type.value,
            "user_id": self.user_id,
            "timestamp": self.timestamp,
            "data": self.data
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CollaborativeAction":
        """Create from dictionary"""
        return cls(
            action_id=data.get("action_id", str(uuid.uuid4())),
            action_type=ActionType(data.get("action_type", "chat_message")),
            user_id=data["user_id"],
            timestamp=data.get("timestamp", datetime.now().timestamp()),
            data=data.get("data", {})
        )


@dataclass
class NeuralinkUser:
    """Represents a connected user"""
    user_id: str
    username: str
    websocket: Optional[WebSocketServerProtocol] = None
    color: str = "#00ff00"  # Avatar color
    is_host: bool = False
    last_action: Optional[CollaborativeAction] = None
    joined_at: float = field(default_factory=lambda: datetime.now().timestamp())


@dataclass
class NeuralinkSession:
    """Represents a collaborative session"""
    session_id: str
    session_name: str
    host_user_id: str
    created_at: float = field(default_factory=lambda: datetime.now().timestamp())
    users: Dict[str, NeuralinkUser] = field(default_factory=dict)
    action_history: list[CollaborativeAction] = field(default_factory=list)
    max_users: int = 8
    password: Optional[str] = None


class NeuralinkServer:
    """
    WebSocket server for Neuralink collaborative sessions
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 8765):
        self.host = host
        self.port = port

        # Sessions
        self.sessions: Dict[str, NeuralinkSession] = {}

        # WebSocket connections (user_id -> websocket)
        self.connections: Dict[str, WebSocketServerProtocol] = {}

        # Server state
        self._running = False
        self._server = None

    async def start(self) -> bool:
        """Start the Neuralink server"""
        if not WEBSOCKETS_AVAILABLE:
            print("[NeuralinkServer] websockets not available")
            return False

        try:
            print(f"[NeuralinkServer] Starting on {self.host}:{self.port}")

            self._server = await websockets.serve(
                self._handle_connection,
                self.host,
                self.port
            )

            self._running = True
            print(f"[NeuralinkServer] ✅ Server running on ws://{self.host}:{self.port}")

            return True

        except Exception as e:
            print(f"[NeuralinkServer] Failed to start: {e}")
            return False

    async def stop(self) -> None:
        """Stop the server"""
        self._running = False

        if self._server:
            self._server.close()
            await self._server.wait_closed()

        print("[NeuralinkServer] Server stopped")

    async def _handle_connection(self, websocket: WebSocketServerProtocol, path: str) -> None:
        """Handle a new WebSocket connection"""
        user_id = None

        try:
            print(f"[NeuralinkServer] New connection from {websocket.remote_address}")

            # Wait for authentication message
            auth_msg = await websocket.recv()
            auth_data = json.loads(auth_msg)

            if auth_data.get("type") != "auth":
                await websocket.send(json.dumps({"error": "Authentication required"}))
                return

            # Create user
            user_id = str(uuid.uuid4())
            username = auth_data.get("username", f"User_{user_id[:8]}")
            color = auth_data.get("color", "#00ff00")

            user = NeuralinkUser(
                user_id=user_id,
                username=username,
                websocket=websocket,
                color=color
            )

            self.connections[user_id] = websocket

            # Send user ID back
            await websocket.send(json.dumps({
                "type": "auth_success",
                "user_id": user_id,
                "username": username
            }))

            print(f"[NeuralinkServer] User authenticated: {username} ({user_id[:8]})")

            # Handle messages
            async for message in websocket:
                await self._handle_message(user_id, user, message)

        except websockets.exceptions.ConnectionClosed:
            print(f"[NeuralinkServer] Connection closed: {user_id}")
        except Exception as e:
            print(f"[NeuralinkServer] Error handling connection: {e}")
        finally:
            # Clean up
            if user_id:
                await self._handle_user_disconnect(user_id)

    async def _handle_message(self, user_id: str, user: NeuralinkUser, message: str) -> None:
        """Handle incoming message from client"""
        try:
            data = json.loads(message)
            msg_type = data.get("type")

            if msg_type == "create_session":
                await self._handle_create_session(user_id, user, data)

            elif msg_type == "join_session":
                await self._handle_join_session(user_id, user, data)

            elif msg_type == "leave_session":
                await self._handle_leave_session(user_id, data)

            elif msg_type == "action":
                await self._handle_action(user_id, data)

            elif msg_type == "list_sessions":
                await self._handle_list_sessions(user_id)

            else:
                print(f"[NeuralinkServer] Unknown message type: {msg_type}")

        except json.JSONDecodeError:
            print(f"[NeuralinkServer] Invalid JSON from {user_id}")
        except Exception as e:
            print(f"[NeuralinkServer] Error handling message: {e}")

    async def _handle_create_session(self, user_id: str, user: NeuralinkUser, data: dict) -> None:
        """Handle session creation"""
        session_name = data.get("session_name", f"Session_{uuid.uuid4()[:8]}")
        password = data.get("password")
        max_users = data.get("max_users", 8)

        session_id = str(uuid.uuid4())

        # Mark user as host
        user.is_host = True

        # Create session
        session = NeuralinkSession(
            session_id=session_id,
            session_name=session_name,
            host_user_id=user_id,
            max_users=max_users,
            password=password,
            users={user_id: user}
        )

        self.sessions[session_id] = session

        # Send success
        await self.connections[user_id].send(json.dumps({
            "type": "session_created",
            "session_id": session_id,
            "session_name": session_name
        }))

        print(f"[NeuralinkServer] Session created: {session_name} ({session_id[:8]}) by {user.username}")

    async def _handle_join_session(self, user_id: str, user: NeuralinkUser, data: dict) -> None:
        """Handle user joining a session"""
        session_id = data.get("session_id")
        password = data.get("password")

        if session_id not in self.sessions:
            await self.connections[user_id].send(json.dumps({
                "type": "error",
                "message": "Session not found"
            }))
            return

        session = self.sessions[session_id]

        # Check password
        if session.password and session.password != password:
            await self.connections[user_id].send(json.dumps({
                "type": "error",
                "message": "Invalid password"
            }))
            return

        # Check max users
        if len(session.users) >= session.max_users:
            await self.connections[user_id].send(json.dumps({
                "type": "error",
                "message": "Session is full"
            }))
            return

        # Add user to session
        session.users[user_id] = user

        # Send success to joining user
        await self.connections[user_id].send(json.dumps({
            "type": "session_joined",
            "session_id": session_id,
            "session_name": session.session_name,
            "users": [
                {"user_id": u.user_id, "username": u.username, "color": u.color, "is_host": u.is_host}
                for u in session.users.values()
            ]
        }))

        # Broadcast user join to all other users
        join_action = CollaborativeAction(
            action_type=ActionType.USER_JOIN,
            user_id=user_id,
            data={"username": user.username, "color": user.color}
        )

        await self._broadcast_action(session_id, join_action, exclude_user=user_id)

        print(f"[NeuralinkServer] {user.username} joined session {session.session_name}")

    async def _handle_leave_session(self, user_id: str, data: dict) -> None:
        """Handle user leaving a session"""
        session_id = data.get("session_id")

        if session_id not in self.sessions:
            return

        session = self.sessions[session_id]

        if user_id not in session.users:
            return

        user = session.users[user_id]

        # Remove user
        del session.users[user_id]

        # Broadcast leave
        leave_action = CollaborativeAction(
            action_type=ActionType.USER_LEAVE,
            user_id=user_id,
            data={"username": user.username}
        )

        await self._broadcast_action(session_id, leave_action)

        # Delete session if empty
        if len(session.users) == 0:
            del self.sessions[session_id]
            print(f"[NeuralinkServer] Session {session.session_name} deleted (empty)")

        print(f"[NeuralinkServer] {user.username} left session {session.session_name}")

    async def _handle_action(self, user_id: str, data: dict) -> None:
        """Handle collaborative action"""
        session_id = data.get("session_id")

        if session_id not in self.sessions:
            return

        session = self.sessions[session_id]

        if user_id not in session.users:
            return

        # Create action
        action = CollaborativeAction.from_dict(data["action"])
        action.user_id = user_id

        # Store in history
        session.action_history.append(action)

        # Keep history limited
        if len(session.action_history) > 1000:
            session.action_history = session.action_history[-1000:]

        # Broadcast to all other users
        await self._broadcast_action(session_id, action, exclude_user=user_id)

    async def _broadcast_action(
        self,
        session_id: str,
        action: CollaborativeAction,
        exclude_user: Optional[str] = None
    ) -> None:
        """Broadcast action to all users in session"""
        if session_id not in self.sessions:
            return

        session = self.sessions[session_id]

        message = json.dumps({
            "type": "action",
            "action": action.to_dict()
        })

        # Send to all users except excluded one
        for uid, user in session.users.items():
            if uid != exclude_user and user.websocket:
                try:
                    await user.websocket.send(message)
                except Exception as e:
                    print(f"[NeuralinkServer] Error sending to {user.username}: {e}")

    async def _handle_list_sessions(self, user_id: str) -> None:
        """Send list of available sessions"""
        sessions_list = [
            {
                "session_id": sid,
                "session_name": session.session_name,
                "user_count": len(session.users),
                "max_users": session.max_users,
                "has_password": session.password is not None,
                "host": session.users[session.host_user_id].username if session.host_user_id in session.users else "Unknown"
            }
            for sid, session in self.sessions.items()
        ]

        await self.connections[user_id].send(json.dumps({
            "type": "sessions_list",
            "sessions": sessions_list
        }))

    async def _handle_user_disconnect(self, user_id: str) -> None:
        """Handle user disconnection"""
        # Remove from all sessions
        for session_id, session in list(self.sessions.items()):
            if user_id in session.users:
                user = session.users[user_id]

                # Broadcast leave
                leave_action = CollaborativeAction(
                    action_type=ActionType.USER_LEAVE,
                    user_id=user_id,
                    data={"username": user.username}
                )

                await self._broadcast_action(session_id, leave_action)

                # Remove user
                del session.users[user_id]

                # Delete session if empty
                if len(session.users) == 0:
                    del self.sessions[session_id]

        # Remove connection
        if user_id in self.connections:
            del self.connections[user_id]


# Standalone server
async def run_server(host: str = "0.0.0.0", port: int = 8765):
    """Run the Neuralink server standalone"""
    server = NeuralinkServer(host, port)

    if await server.start():
        print("[NeuralinkServer] Server running. Press Ctrl+C to stop.")

        try:
            # Keep running
            await asyncio.Future()
        except KeyboardInterrupt:
            print("\n[NeuralinkServer] Shutting down...")
            await server.stop()


if __name__ == "__main__":
    asyncio.run(run_server())
