"""
MIDI Handler - Direct MIDI communication via mido

Ermöglicht das direkte Senden von MIDI-Noten an Ableton Live oder andere DAWs
"""

from typing import List, Optional, Dict, Callable
import asyncio
from dataclasses import dataclass
import mido


@dataclass
class MIDINote:
    """Represents a MIDI note with all parameters"""
    note: int  # 0-127
    velocity: int = 100  # 0-127
    duration: float = 0.5  # in seconds
    channel: int = 0  # 0-15


class MIDIHandler:
    """
    Handler for MIDI input/output operations
    """

    def __init__(self, port_name: Optional[str] = None):
        self.port_name = port_name
        self._output_port: Optional[mido.ports.BaseOutput] = None
        self._input_port: Optional[mido.ports.BaseInput] = None
        self._listening = False
        self._note_callbacks: List[Callable] = []

    def list_output_ports(self) -> List[str]:
        """List available MIDI output ports"""
        return mido.get_output_names()

    def list_input_ports(self) -> List[str]:
        """List available MIDI input ports"""
        return mido.get_input_names()

    def open_output(self, port_name: Optional[str] = None) -> bool:
        """
        Open a MIDI output port

        Args:
            port_name: Name of the port to open (uses default if None)

        Returns:
            True if successful
        """
        try:
            if port_name:
                self._output_port = mido.open_output(port_name)
            else:
                # Try to find a virtual port or use default
                available_ports = self.list_output_ports()
                if available_ports:
                    # Prefer ports with "Ableton" or "IAC" in name
                    ableton_ports = [p for p in available_ports if "Ableton" in p or "IAC" in p]
                    if ableton_ports:
                        self._output_port = mido.open_output(ableton_ports[0])
                    else:
                        self._output_port = mido.open_output(available_ports[0])
                else:
                    print("[MIDIHandler] No MIDI output ports available")
                    return False

            print(f"[MIDIHandler] Opened output port: {self._output_port.name}")
            return True

        except Exception as e:
            print(f"[MIDIHandler] Error opening output port: {e}")
            return False

    def open_input(self, port_name: Optional[str] = None) -> bool:
        """
        Open a MIDI input port

        Args:
            port_name: Name of the port to open (uses default if None)

        Returns:
            True if successful
        """
        try:
            if port_name:
                self._input_port = mido.open_input(port_name)
            else:
                available_ports = self.list_input_ports()
                if available_ports:
                    # Prefer ports with "Ableton" or "IAC" in name
                    ableton_ports = [p for p in available_ports if "Ableton" in p or "IAC" in p]
                    if ableton_ports:
                        self._input_port = mido.open_input(ableton_ports[0])
                    else:
                        self._input_port = mido.open_input(available_ports[0])
                else:
                    print("[MIDIHandler] No MIDI input ports available")
                    return False

            print(f"[MIDIHandler] Opened input port: {self._input_port.name}")
            return True

        except Exception as e:
            print(f"[MIDIHandler] Error opening input port: {e}")
            return False

    def close(self) -> None:
        """Close all MIDI ports"""
        if self._output_port:
            self._output_port.close()
            self._output_port = None

        if self._input_port:
            self._input_port.close()
            self._input_port = None

        self._listening = False
        print("[MIDIHandler] Closed all MIDI ports")

    def send_note(self, note: MIDINote) -> bool:
        """
        Send a single MIDI note (note on + note off)

        Args:
            note: MIDINote object

        Returns:
            True if successful
        """
        if not self._output_port:
            print("[MIDIHandler] Output port not open")
            return False

        try:
            # Send note on
            msg_on = mido.Message(
                'note_on',
                note=note.note,
                velocity=note.velocity,
                channel=note.channel
            )
            self._output_port.send(msg_on)

            # Send note off after duration (synchronously for now)
            # In production, this should be handled asynchronously
            import time
            time.sleep(note.duration)

            msg_off = mido.Message(
                'note_off',
                note=note.note,
                velocity=0,
                channel=note.channel
            )
            self._output_port.send(msg_off)

            return True

        except Exception as e:
            print(f"[MIDIHandler] Error sending note: {e}")
            return False

    async def send_note_async(self, note: MIDINote) -> bool:
        """
        Send a MIDI note asynchronously

        Args:
            note: MIDINote object

        Returns:
            True if successful
        """
        if not self._output_port:
            print("[MIDIHandler] Output port not open")
            return False

        try:
            # Send note on
            msg_on = mido.Message(
                'note_on',
                note=note.note,
                velocity=note.velocity,
                channel=note.channel
            )
            await asyncio.get_event_loop().run_in_executor(
                None,
                self._output_port.send,
                msg_on
            )

            # Wait for duration
            await asyncio.sleep(note.duration)

            # Send note off
            msg_off = mido.Message(
                'note_off',
                note=note.note,
                velocity=0,
                channel=note.channel
            )
            await asyncio.get_event_loop().run_in_executor(
                None,
                self._output_port.send,
                msg_off
            )

            return True

        except Exception as e:
            print(f"[MIDIHandler] Error sending note: {e}")
            return False

    async def send_chord(self, notes: List[int], velocity: int = 100,
                        duration: float = 1.0, channel: int = 0) -> bool:
        """
        Send multiple notes simultaneously (chord)

        Args:
            notes: List of MIDI note numbers
            velocity: Velocity for all notes
            duration: Duration in seconds
            channel: MIDI channel

        Returns:
            True if successful
        """
        if not self._output_port:
            print("[MIDIHandler] Output port not open")
            return False

        try:
            # Send all note ons
            for note in notes:
                msg_on = mido.Message('note_on', note=note, velocity=velocity, channel=channel)
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    self._output_port.send,
                    msg_on
                )

            # Wait for duration
            await asyncio.sleep(duration)

            # Send all note offs
            for note in notes:
                msg_off = mido.Message('note_off', note=note, velocity=0, channel=channel)
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    self._output_port.send,
                    msg_off
                )

            return True

        except Exception as e:
            print(f"[MIDIHandler] Error sending chord: {e}")
            return False

    async def send_sequence(self, notes: List[MIDINote], delay: float = 0.0) -> bool:
        """
        Send a sequence of notes

        Args:
            notes: List of MIDINote objects
            delay: Additional delay between notes (in seconds)

        Returns:
            True if successful
        """
        for note in notes:
            await self.send_note_async(note)
            if delay > 0:
                await asyncio.sleep(delay)

        return True

    async def start_listening(self) -> None:
        """Start listening for MIDI input (in background)"""
        if not self._input_port:
            print("[MIDIHandler] Input port not open")
            return

        self._listening = True
        print("[MIDIHandler] Started listening for MIDI input")

        async def listen():
            while self._listening:
                # Check for messages (non-blocking)
                for msg in self._input_port.iter_pending():
                    # Call registered callbacks
                    for callback in self._note_callbacks:
                        await callback(msg)

                await asyncio.sleep(0.01)  # Small delay to avoid busy-waiting

        # Start listening task in background
        asyncio.create_task(listen())

    def stop_listening(self) -> None:
        """Stop listening for MIDI input"""
        self._listening = False
        print("[MIDIHandler] Stopped listening for MIDI input")

    def add_note_callback(self, callback: Callable) -> None:
        """
        Register a callback for received MIDI messages

        Args:
            callback: Async function that takes a mido.Message as parameter
        """
        self._note_callbacks.append(callback)

    def remove_note_callback(self, callback: Callable) -> None:
        """Remove a registered callback"""
        if callback in self._note_callbacks:
            self._note_callbacks.remove(callback)

    def send_cc(self, control: int, value: int, channel: int = 0) -> bool:
        """
        Send a MIDI CC (Control Change) message

        Args:
            control: CC number (0-127)
            value: CC value (0-127)
            channel: MIDI channel

        Returns:
            True if successful
        """
        if not self._output_port:
            print("[MIDIHandler] Output port not open")
            return False

        try:
            msg = mido.Message('control_change', control=control, value=value, channel=channel)
            self._output_port.send(msg)
            return True

        except Exception as e:
            print(f"[MIDIHandler] Error sending CC: {e}")
            return False

    def panic(self) -> None:
        """Send all notes off (panic button)"""
        if not self._output_port:
            return

        try:
            for channel in range(16):
                # All notes off CC
                self._output_port.send(mido.Message('control_change', control=123, value=0, channel=channel))

                # Also send note offs for all notes
                for note in range(128):
                    self._output_port.send(mido.Message('note_off', note=note, velocity=0, channel=channel))

            print("[MIDIHandler] Panic: All notes off sent")

        except Exception as e:
            print(f"[MIDIHandler] Error during panic: {e}")


# Example usage
async def _example_usage():
    """Example usage of MIDIHandler"""
    handler = MIDIHandler()

    print("Available output ports:")
    for port in handler.list_output_ports():
        print(f"  - {port}")

    if handler.open_output():
        # Send a single note
        note = MIDINote(note=60, velocity=100, duration=0.5)  # Middle C
        await handler.send_note_async(note)

        # Send a chord
        chord = [60, 64, 67]  # C Major
        await handler.send_chord(chord, duration=1.0)

        # Send a sequence
        sequence = [
            MIDINote(note=60, velocity=100, duration=0.25),
            MIDINote(note=62, velocity=100, duration=0.25),
            MIDINote(note=64, velocity=100, duration=0.25),
            MIDINote(note=65, velocity=100, duration=0.25),
        ]
        await handler.send_sequence(sequence)

        handler.close()


if __name__ == "__main__":
    asyncio.run(_example_usage())
