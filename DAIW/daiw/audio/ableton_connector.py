"""
Ableton Connector - Bridge to Ableton Live via OSC and MIDI

Nutzt die bestehende OSC Daemon Infrastruktur und erweitert sie um
direkte MIDI-Kommunikation.
"""

import asyncio
import json
import socket
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass


@dataclass
class AbletonConnectionConfig:
    """Configuration for Ableton connection"""
    daemon_host: str = "127.0.0.1"
    daemon_port: int = 65432
    timeout: float = 5.0


class AbletonConnector:
    """
    Connector for communicating with Ableton Live via the OSC daemon
    """

    def __init__(self, config: Optional[AbletonConnectionConfig] = None):
        self.config = config or AbletonConnectionConfig()
        self._socket: Optional[socket.socket] = None
        self._connected = False

        # Callbacks
        self._message_callbacks: List[Callable] = []

    async def connect(self) -> bool:
        """
        Connect to the OSC daemon

        Returns:
            True if connected successfully, False otherwise
        """
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(self.config.timeout)
            await asyncio.get_event_loop().run_in_executor(
                None,
                self._socket.connect,
                (self.config.daemon_host, self.config.daemon_port)
            )
            self._connected = True
            print(f"[AbletonConnector] Connected to OSC daemon at {self.config.daemon_host}:{self.config.daemon_port}")
            return True

        except (socket.error, socket.timeout) as e:
            print(f"[AbletonConnector] Failed to connect: {e}")
            self._connected = False
            return False

    async def disconnect(self) -> None:
        """Disconnect from the OSC daemon"""
        if self._socket:
            self._socket.close()
            self._socket = None
        self._connected = False
        print("[AbletonConnector] Disconnected")

    def is_connected(self) -> bool:
        """Check if connected to the daemon"""
        return self._connected

    async def send_osc_message(self, address: str, args: List[Any] = None) -> Dict[str, Any]:
        """
        Send an OSC message to Ableton via the daemon

        Args:
            address: OSC address (e.g., "/live/song/get/tempo")
            args: OSC arguments (optional)

        Returns:
            Response dictionary from the daemon
        """
        if not self._connected:
            raise ConnectionError("Not connected to OSC daemon")

        if args is None:
            args = []

        message = {
            "command": "send_message",
            "address": address,
            "args": args
        }

        try:
            # Send message
            await asyncio.get_event_loop().run_in_executor(
                None,
                self._socket.sendall,
                json.dumps(message).encode()
            )

            # Receive response
            data = await asyncio.get_event_loop().run_in_executor(
                None,
                self._socket.recv,
                4096
            )

            response = json.loads(data.decode())

            # Notify callbacks
            for callback in self._message_callbacks:
                await callback(address, response)

            return response

        except (socket.error, json.JSONDecodeError) as e:
            print(f"[AbletonConnector] Error sending OSC message: {e}")
            return {"status": "error", "message": str(e)}

    async def get_status(self) -> Dict[str, Any]:
        """
        Get daemon status

        Returns:
            Status dictionary
        """
        if not self._connected:
            raise ConnectionError("Not connected to OSC daemon")

        message = {"command": "get_status"}

        try:
            await asyncio.get_event_loop().run_in_executor(
                None,
                self._socket.sendall,
                json.dumps(message).encode()
            )

            data = await asyncio.get_event_loop().run_in_executor(
                None,
                self._socket.recv,
                4096
            )

            return json.loads(data.decode())

        except (socket.error, json.JSONDecodeError) as e:
            print(f"[AbletonConnector] Error getting status: {e}")
            return {"status": "error", "message": str(e)}

    # ========== Convenience methods for common Ableton operations ==========

    async def get_tempo(self) -> Optional[float]:
        """Get current song tempo"""
        response = await self.send_osc_message("/live/song/get/tempo")
        if response.get("status") == "success":
            data = response.get("data", [])
            return float(data[0]) if data else None
        return None

    async def set_tempo(self, tempo: float) -> bool:
        """Set song tempo"""
        response = await self.send_osc_message("/live/song/set/tempo", [tempo])
        return response.get("status") == "sent"

    async def play(self) -> bool:
        """Start playback"""
        response = await self.send_osc_message("/live/song/start_playing")
        return response.get("status") == "sent"

    async def stop(self) -> bool:
        """Stop playback"""
        response = await self.send_osc_message("/live/song/stop_playing")
        return response.get("status") == "sent"

    async def get_is_playing(self) -> Optional[bool]:
        """Check if song is playing"""
        response = await self.send_osc_message("/live/song/get/is_playing")
        if response.get("status") == "success":
            data = response.get("data", [])
            return bool(data[0]) if data else None
        return None

    async def get_current_beat(self) -> Optional[float]:
        """Get current beat position"""
        response = await self.send_osc_message("/live/song/get/current_song_time")
        if response.get("status") == "success":
            data = response.get("data", [])
            return float(data[0]) if data else None
        return None

    async def create_midi_track(self, name: str = "MIDI Track") -> bool:
        """Create a new MIDI track"""
        response = await self.send_osc_message("/live/song/create_midi_track", [-1])
        if response.get("status") == "sent":
            # Set track name
            await self.send_osc_message("/live/track/set/name", [-1, name])
            return True
        return False

    async def get_track_count(self) -> Optional[int]:
        """Get number of tracks"""
        response = await self.send_osc_message("/live/song/get/num_tracks")
        if response.get("status") == "success":
            data = response.get("data", [])
            return int(data[0]) if data else None
        return None

    async def get_track_name(self, track_index: int) -> Optional[str]:
        """Get track name by index"""
        response = await self.send_osc_message("/live/track/get/name", [track_index])
        if response.get("status") == "success":
            data = response.get("data", [])
            return str(data[0]) if data else None
        return None

    async def arm_track(self, track_index: int, armed: bool = True) -> bool:
        """Arm/disarm a track for recording"""
        response = await self.send_osc_message(
            "/live/track/set/arm",
            [track_index, 1 if armed else 0]
        )
        return response.get("status") == "sent"

    async def get_scene_count(self) -> Optional[int]:
        """Get number of scenes"""
        response = await self.send_osc_message("/live/song/get/num_scenes")
        if response.get("status") == "success":
            data = response.get("data", [])
            return int(data[0]) if data else None
        return None

    async def trigger_scene(self, scene_index: int) -> bool:
        """Trigger a scene"""
        response = await self.send_osc_message("/live/scene/fire", [scene_index])
        return response.get("status") == "sent"

    # ========== Callback registration ==========

    def add_message_callback(self, callback: Callable) -> None:
        """
        Register a callback for OSC messages

        Args:
            callback: Async function that takes (address, response) as parameters
        """
        self._message_callbacks.append(callback)

    def remove_message_callback(self, callback: Callable) -> None:
        """Remove a registered callback"""
        if callback in self._message_callbacks:
            self._message_callbacks.remove(callback)


# Example usage
async def _example_usage():
    """Example usage of AbletonConnector"""
    connector = AbletonConnector()

    # Connect
    if await connector.connect():
        # Get status
        status = await connector.get_status()
        print(f"Daemon status: {status}")

        # Get tempo
        tempo = await connector.get_tempo()
        print(f"Current tempo: {tempo} BPM")

        # Get track count
        track_count = await connector.get_track_count()
        print(f"Number of tracks: {track_count}")

        # Check if playing
        is_playing = await connector.get_is_playing()
        print(f"Is playing: {is_playing}")

        # Disconnect
        await connector.disconnect()


if __name__ == "__main__":
    asyncio.run(_example_usage())
