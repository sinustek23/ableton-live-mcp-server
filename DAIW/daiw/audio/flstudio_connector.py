"""
FL Studio Connector - MIDI Script Integration

FL Studio integration via MIDI Remote Scripts and OSC
Provides bidirectional communication between DAIW and FL Studio

Author: DAIW Team
License: MIT
"""

import asyncio
import logging
from typing import Optional, Callable, List, Dict, Any
from dataclasses import dataclass
from enum import Enum

try:
    import mido
    MIDO_AVAILABLE = True
except ImportError:
    MIDO_AVAILABLE = False
    logging.warning("mido not available - FL Studio MIDI integration disabled")

try:
    from pythonosc import udp_client, dispatcher, osc_server
    OSC_AVAILABLE = True
except ImportError:
    OSC_AVAILABLE = False
    logging.warning("python-osc not available - FL Studio OSC integration disabled")


class FLStudioTransport(Enum):
    """FL Studio transport states"""
    STOPPED = 0
    PLAYING = 1
    RECORDING = 2
    PAUSED = 3


@dataclass
class FLStudioTrack:
    """FL Studio mixer track/channel"""
    index: int
    name: str
    volume: float = 0.8
    pan: float = 0.0
    muted: bool = False
    solo: bool = False
    armed: bool = False


@dataclass
class FLStudioPattern:
    """FL Studio pattern"""
    index: int
    name: str
    length: int = 16  # bars
    active: bool = False


class FLStudioConnector:
    """
    FL Studio Connector for DAIW

    Supports two integration methods:
    1. MIDI (via MIDI Remote Scripts) - Basic control
    2. OSC (via FL Studio OSC plugin) - Advanced control

    FL Studio MIDI CC Map:
    - CC 7: Volume
    - CC 10: Pan
    - CC 16-23: Track Mute (0=unmute, 127=mute)
    - CC 32-39: Track Solo
    - CC 48: Transport (0=stop, 127=play)
    - CC 49: Record (0=off, 127=on)
    """

    def __init__(
        self,
        midi_port_name: str = "FL Studio MIDI",
        osc_host: str = "127.0.0.1",
        osc_send_port: int = 9001,
        osc_receive_port: int = 9002,
    ):
        self.midi_port_name = midi_port_name
        self.osc_host = osc_host
        self.osc_send_port = osc_send_port
        self.osc_receive_port = osc_receive_port

        self.midi_output: Optional[mido.ports.BaseOutput] = None
        self.midi_input: Optional[mido.ports.BaseInput] = None
        self.osc_client: Optional[udp_client.SimpleUDPClient] = None
        self.osc_server: Optional[osc_server.ThreadingOSCUDPServer] = None

        self.connected = False
        self.transport_state = FLStudioTransport.STOPPED
        self.tempo = 140.0
        self.song_position = 0.0

        self.tracks: Dict[int, FLStudioTrack] = {}
        self.patterns: Dict[int, FLStudioPattern] = {}

        # Callbacks
        self.tempo_callback: Optional[Callable[[float], None]] = None
        self.transport_callback: Optional[Callable[[FLStudioTransport], None]] = None
        self.track_callback: Optional[Callable[[FLStudioTrack], None]] = None

        self.logger = logging.getLogger("FLStudioConnector")

    async def connect(self) -> bool:
        """Connect to FL Studio via MIDI and/or OSC"""
        success = False

        # Try MIDI connection
        if MIDO_AVAILABLE:
            if await self._connect_midi():
                success = True
                self.logger.info("Connected to FL Studio via MIDI")

        # Try OSC connection
        if OSC_AVAILABLE:
            if await self._connect_osc():
                success = True
                self.logger.info("Connected to FL Studio via OSC")

        if success:
            self.connected = True
            await self._initialize_state()
        else:
            self.logger.error("Failed to connect to FL Studio")

        return success

    async def disconnect(self):
        """Disconnect from FL Studio"""
        if self.midi_output:
            self.midi_output.close()
        if self.midi_input:
            self.midi_input.close()
        if self.osc_server:
            self.osc_server.shutdown()

        self.connected = False
        self.logger.info("Disconnected from FL Studio")

    async def _connect_midi(self) -> bool:
        """Connect via MIDI"""
        try:
            # Find FL Studio MIDI ports
            output_ports = mido.get_output_names()
            input_ports = mido.get_input_names()

            # Find matching port
            fl_output = None
            fl_input = None

            for port in output_ports:
                if "fl studio" in port.lower() or "fruity" in port.lower():
                    fl_output = port
                    break

            for port in input_ports:
                if "fl studio" in port.lower() or "fruity" in port.lower():
                    fl_input = port
                    break

            if fl_output:
                self.midi_output = mido.open_output(fl_output)
                self.logger.info(f"MIDI output: {fl_output}")

            if fl_input:
                self.midi_input = mido.open_input(fl_input, callback=self._handle_midi_message)
                self.logger.info(f"MIDI input: {fl_input}")

            return fl_output is not None or fl_input is not None

        except Exception as e:
            self.logger.error(f"MIDI connection failed: {e}")
            return False

    async def _connect_osc(self) -> bool:
        """Connect via OSC"""
        try:
            # Create OSC client (for sending to FL Studio)
            self.osc_client = udp_client.SimpleUDPClient(
                self.osc_host,
                self.osc_send_port
            )

            # Create OSC server (for receiving from FL Studio)
            disp = dispatcher.Dispatcher()
            disp.map("/tempo", self._handle_osc_tempo)
            disp.map("/transport", self._handle_osc_transport)
            disp.map("/track/*", self._handle_osc_track)
            disp.map("/pattern/*", self._handle_osc_pattern)

            self.osc_server = osc_server.ThreadingOSCUDPServer(
                (self.osc_host, self.osc_receive_port),
                disp
            )

            # Start server in background
            import threading
            server_thread = threading.Thread(target=self.osc_server.serve_forever)
            server_thread.daemon = True
            server_thread.start()

            self.logger.info(f"OSC client -> {self.osc_host}:{self.osc_send_port}")
            self.logger.info(f"OSC server <- {self.osc_host}:{self.osc_receive_port}")

            return True

        except Exception as e:
            self.logger.error(f"OSC connection failed: {e}")
            return False

    async def _initialize_state(self):
        """Initialize FL Studio state"""
        # Request current state
        if self.osc_client:
            self.osc_client.send_message("/request/tempo", [])
            self.osc_client.send_message("/request/transport", [])
            self.osc_client.send_message("/request/tracks", [])

    # ========================================================================
    # Transport Control
    # ========================================================================

    async def play(self):
        """Start playback"""
        if self.midi_output:
            self.midi_output.send(mido.Message('control_change', control=48, value=127))
        if self.osc_client:
            self.osc_client.send_message("/transport/play", [1])

        self.transport_state = FLStudioTransport.PLAYING

    async def stop(self):
        """Stop playback"""
        if self.midi_output:
            self.midi_output.send(mido.Message('control_change', control=48, value=0))
        if self.osc_client:
            self.osc_client.send_message("/transport/stop", [])

        self.transport_state = FLStudioTransport.STOPPED

    async def record(self, enable: bool = True):
        """Enable/disable recording"""
        if self.midi_output:
            self.midi_output.send(mido.Message('control_change', control=49, value=127 if enable else 0))
        if self.osc_client:
            self.osc_client.send_message("/transport/record", [1 if enable else 0])

    async def set_tempo(self, bpm: float):
        """Set tempo (BPM)"""
        if self.osc_client:
            self.osc_client.send_message("/tempo", [bpm])

        self.tempo = bpm

        if self.tempo_callback:
            self.tempo_callback(bpm)

    # ========================================================================
    # Track/Mixer Control
    # ========================================================================

    async def set_track_volume(self, track_index: int, volume: float):
        """Set track volume (0.0-1.0)"""
        if self.midi_output:
            # CC 7 for volume
            midi_value = int(volume * 127)
            self.midi_output.send(mido.Message(
                'control_change',
                channel=track_index,
                control=7,
                value=midi_value
            ))

        if self.osc_client:
            self.osc_client.send_message(f"/track/{track_index}/volume", [volume])

        if track_index in self.tracks:
            self.tracks[track_index].volume = volume

    async def set_track_pan(self, track_index: int, pan: float):
        """Set track pan (-1.0 to 1.0)"""
        if self.midi_output:
            # CC 10 for pan
            midi_value = int((pan + 1.0) * 63.5)
            self.midi_output.send(mido.Message(
                'control_change',
                channel=track_index,
                control=10,
                value=midi_value
            ))

        if self.osc_client:
            self.osc_client.send_message(f"/track/{track_index}/pan", [pan])

        if track_index in self.tracks:
            self.tracks[track_index].pan = pan

    async def mute_track(self, track_index: int, mute: bool = True):
        """Mute/unmute track"""
        if self.midi_output:
            # CC 16-23 for track mutes
            cc_number = 16 + (track_index % 8)
            self.midi_output.send(mido.Message(
                'control_change',
                control=cc_number,
                value=127 if mute else 0
            ))

        if self.osc_client:
            self.osc_client.send_message(f"/track/{track_index}/mute", [1 if mute else 0])

        if track_index in self.tracks:
            self.tracks[track_index].muted = mute

    async def solo_track(self, track_index: int, solo: bool = True):
        """Solo/unsolo track"""
        if self.midi_output:
            # CC 32-39 for track solos
            cc_number = 32 + (track_index % 8)
            self.midi_output.send(mido.Message(
                'control_change',
                control=cc_number,
                value=127 if solo else 0
            ))

        if self.osc_client:
            self.osc_client.send_message(f"/track/{track_index}/solo", [1 if solo else 0])

        if track_index in self.tracks:
            self.tracks[track_index].solo = solo

    # ========================================================================
    # Pattern Control
    # ========================================================================

    async def trigger_pattern(self, pattern_index: int):
        """Trigger pattern"""
        if self.osc_client:
            self.osc_client.send_message(f"/pattern/{pattern_index}/trigger", [])

    async def select_pattern(self, pattern_index: int):
        """Select pattern for editing"""
        if self.osc_client:
            self.osc_client.send_message(f"/pattern/{pattern_index}/select", [])

    # ========================================================================
    # MIDI Handlers
    # ========================================================================

    def _handle_midi_message(self, message: mido.Message):
        """Handle incoming MIDI from FL Studio"""
        if message.type == 'control_change':
            control = message.control
            value = message.value

            # Tempo (if FL Studio sends it via CC)
            if control == 50:
                self.tempo = 20 + (value / 127.0) * 280  # 20-300 BPM range
                if self.tempo_callback:
                    self.tempo_callback(self.tempo)

            # Track updates
            elif 16 <= control <= 23:  # Mutes
                track_index = control - 16
                muted = value > 64
                if track_index in self.tracks:
                    self.tracks[track_index].muted = muted

    # ========================================================================
    # OSC Handlers
    # ========================================================================

    def _handle_osc_tempo(self, address: str, *args):
        """Handle tempo update from FL Studio"""
        if args:
            self.tempo = float(args[0])
            if self.tempo_callback:
                self.tempo_callback(self.tempo)

    def _handle_osc_transport(self, address: str, *args):
        """Handle transport state from FL Studio"""
        if args:
            state = int(args[0])
            self.transport_state = FLStudioTransport(state)
            if self.transport_callback:
                self.transport_callback(self.transport_state)

    def _handle_osc_track(self, address: str, *args):
        """Handle track updates from FL Studio"""
        # Parse: /track/1/volume 0.8
        parts = address.split('/')
        if len(parts) >= 4:
            track_index = int(parts[2])
            property_name = parts[3]

            if track_index not in self.tracks:
                self.tracks[track_index] = FLStudioTrack(
                    index=track_index,
                    name=f"Track {track_index}"
                )

            track = self.tracks[track_index]

            if property_name == "volume" and args:
                track.volume = float(args[0])
            elif property_name == "pan" and args:
                track.pan = float(args[0])
            elif property_name == "mute" and args:
                track.muted = bool(args[0])
            elif property_name == "solo" and args:
                track.solo = bool(args[0])
            elif property_name == "name" and args:
                track.name = str(args[0])

            if self.track_callback:
                self.track_callback(track)

    def _handle_osc_pattern(self, address: str, *args):
        """Handle pattern updates from FL Studio"""
        parts = address.split('/')
        if len(parts) >= 3:
            pattern_index = int(parts[2])

            if pattern_index not in self.patterns:
                self.patterns[pattern_index] = FLStudioPattern(
                    index=pattern_index,
                    name=f"Pattern {pattern_index}"
                )

    # ========================================================================
    # Getters
    # ========================================================================

    def get_tempo(self) -> float:
        """Get current tempo"""
        return self.tempo

    def get_transport_state(self) -> FLStudioTransport:
        """Get transport state"""
        return self.transport_state

    def get_tracks(self) -> List[FLStudioTrack]:
        """Get all tracks"""
        return list(self.tracks.values())

    def get_track(self, track_index: int) -> Optional[FLStudioTrack]:
        """Get specific track"""
        return self.tracks.get(track_index)


# ============================================================================
# Example Usage
# ============================================================================

async def example_usage():
    """Example FL Studio integration"""
    connector = FLStudioConnector()

    # Connect
    if await connector.connect():
        print("✅ Connected to FL Studio")

        # Play
        await connector.play()
        await asyncio.sleep(2)

        # Set tempo
        await connector.set_tempo(128.0)

        # Mute track 1
        await connector.mute_track(1, True)

        # Adjust volume
        await connector.set_track_volume(2, 0.7)

        # Stop
        await connector.stop()

        # Disconnect
        await connector.disconnect()
    else:
        print("❌ Failed to connect to FL Studio")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(example_usage())
