"""
Humming Detector - Record humming/singing and convert to MIDI

Ermöglicht Echtzeit-Aufnahme von gesummten Melodien und Konvertierung zu MIDI
"""

import asyncio
from typing import Optional, List, Callable, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
import tempfile
import numpy as np

try:
    import sounddevice as sd
    import soundfile as sf
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    SOUNDDEVICE_AVAILABLE = False
    print("[HummingDetector] Warning: sounddevice not available")

try:
    import aubio
    AUBIO_AVAILABLE = True
except ImportError:
    AUBIO_AVAILABLE = False
    print("[HummingDetector] Warning: aubio not available")

from avatar.audio.midi_handler import MIDINote


@dataclass
class HummingPhrase:
    """Represents a recorded humming phrase"""
    timestamp: datetime = field(default_factory=datetime.now)
    audio_data: Optional[np.ndarray] = None
    sample_rate: int = 44100
    duration: float = 0.0

    # MIDI conversion
    midi_notes: List[MIDINote] = field(default_factory=list)
    detected_pitches: List[float] = field(default_factory=list)
    confidence_scores: List[float] = field(default_factory=list)

    # Analysis
    tempo: Optional[float] = None
    key: Optional[str] = None
    audio_path: Optional[Path] = None


class HummingDetector:
    """
    Real-time humming/singing detection and MIDI conversion
    """

    def __init__(
        self,
        sample_rate: int = 44100,
        channels: int = 1,
        buffer_size: int = 2048,
        hop_size: int = 512
    ):
        self.sample_rate = sample_rate
        self.channels = channels
        self.buffer_size = buffer_size
        self.hop_size = hop_size

        # Recording state
        self._recording = False
        self._recorded_frames: List[np.ndarray] = []

        # Pitch detection
        self._pitch_detector = None
        if AUBIO_AVAILABLE:
            self._pitch_detector = aubio.pitch("yin", self.buffer_size, self.hop_size, self.sample_rate)
            self._pitch_detector.set_unit("Hz")
            self._pitch_detector.set_silence(-40)  # Silence threshold in dB

        # Real-time callbacks
        self._note_callbacks: List[Callable] = []
        self._pitch_callbacks: List[Callable] = []

        # Storage
        self._output_dir = Path(tempfile.gettempdir()) / "music_copilot_humming"
        self._output_dir.mkdir(parents=True, exist_ok=True)

        # Current phrase
        self._current_phrase: Optional[HummingPhrase] = None

    def list_input_devices(self) -> List[Tuple[int, str]]:
        """List available audio input devices"""
        if not SOUNDDEVICE_AVAILABLE:
            return []

        devices = []
        for idx, device in enumerate(sd.query_devices()):
            if device['max_input_channels'] > 0:
                devices.append((idx, device['name']))

        return devices

    async def start_recording(self, device_id: Optional[int] = None) -> bool:
        """
        Start recording humming

        Args:
            device_id: Optional specific input device ID

        Returns:
            True if recording started
        """
        if not SOUNDDEVICE_AVAILABLE:
            print("[HummingDetector] sounddevice not available")
            return False

        if self._recording:
            print("[HummingDetector] Already recording")
            return False

        try:
            self._recording = True
            self._recorded_frames = []
            self._current_phrase = HummingPhrase(sample_rate=self.sample_rate)

            print("[HummingDetector] Started recording (speak/hum now...)")

            # Start async recording
            asyncio.create_task(self._record_loop(device_id))

            return True

        except Exception as e:
            print(f"[HummingDetector] Error starting recording: {e}")
            self._recording = False
            return False

    async def _record_loop(self, device_id: Optional[int] = None) -> None:
        """Background recording loop"""
        try:
            # Callback for audio chunks
            def audio_callback(indata, frames, time, status):
                if status:
                    print(f"[HummingDetector] Status: {status}")

                # Store frame
                self._recorded_frames.append(indata.copy())

                # Real-time pitch detection
                if self._pitch_detector and AUBIO_AVAILABLE:
                    # Convert to float32
                    audio_chunk = indata[:, 0].astype(np.float32)

                    # Detect pitch
                    pitch = self._pitch_detector(audio_chunk)[0]
                    confidence = self._pitch_detector.get_confidence()

                    if pitch > 0 and confidence > 0.5:
                        # Call pitch callbacks
                        for callback in self._pitch_callbacks:
                            asyncio.create_task(callback(pitch, confidence))

            # Open stream
            with sd.InputStream(
                device=device_id,
                channels=self.channels,
                samplerate=self.sample_rate,
                blocksize=self.hop_size,
                callback=audio_callback
            ):
                # Record while flag is set
                while self._recording:
                    await asyncio.sleep(0.1)

        except Exception as e:
            print(f"[HummingDetector] Recording error: {e}")
            self._recording = False

    async def stop_recording(self) -> Optional[HummingPhrase]:
        """
        Stop recording and process the phrase

        Returns:
            Processed HummingPhrase
        """
        if not self._recording:
            print("[HummingDetector] Not recording")
            return None

        self._recording = False
        await asyncio.sleep(0.2)  # Let final frames be processed

        if not self._recorded_frames or not self._current_phrase:
            print("[HummingDetector] No audio recorded")
            return None

        try:
            # Concatenate frames
            audio_data = np.concatenate(self._recorded_frames, axis=0)
            self._current_phrase.audio_data = audio_data
            self._current_phrase.duration = len(audio_data) / self.sample_rate

            print(f"[HummingDetector] Recorded {self._current_phrase.duration:.2f} seconds")

            # Save audio
            audio_path = self._output_dir / f"humming_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
            await asyncio.get_event_loop().run_in_executor(
                None,
                sf.write,
                str(audio_path),
                audio_data,
                self.sample_rate
            )
            self._current_phrase.audio_path = audio_path
            print(f"[HummingDetector] Saved: {audio_path}")

            # Convert to MIDI
            await self._convert_to_midi(self._current_phrase)

            return self._current_phrase

        except Exception as e:
            print(f"[HummingDetector] Error processing recording: {e}")
            return None
        finally:
            self._recorded_frames = []

    async def _convert_to_midi(self, phrase: HummingPhrase) -> None:
        """
        Convert recorded audio to MIDI notes

        Args:
            phrase: HummingPhrase to process
        """
        if not phrase.audio_data is not None or not AUBIO_AVAILABLE:
            return

        try:
            print("[HummingDetector] Converting to MIDI...")

            # Process audio in chunks
            audio = phrase.audio_data[:, 0].astype(np.float32) if phrase.audio_data.ndim > 1 else phrase.audio_data.astype(np.float32)

            pitches = []
            confidences = []
            timestamps = []

            # Analyze in chunks
            for i in range(0, len(audio) - self.hop_size, self.hop_size):
                chunk = audio[i:i + self.hop_size]

                pitch = self._pitch_detector(chunk)[0]
                confidence = self._pitch_detector.get_confidence()

                if pitch > 0 and confidence > 0.5:
                    pitches.append(pitch)
                    confidences.append(confidence)
                    timestamps.append(i / self.sample_rate)
                else:
                    pitches.append(0)
                    confidences.append(0)
                    timestamps.append(i / self.sample_rate)

            phrase.detected_pitches = pitches
            phrase.confidence_scores = confidences

            # Convert pitches to MIDI notes
            midi_notes = []
            current_note = None
            note_start_time = None

            for i, (pitch, conf, time) in enumerate(zip(pitches, confidences, timestamps)):
                if pitch > 0 and conf > 0.5:
                    midi_num = self._hz_to_midi(pitch)

                    # Start of new note or continuation?
                    if current_note is None:
                        # Start new note
                        current_note = midi_num
                        note_start_time = time
                    elif abs(midi_num - current_note) > 1:  # Significant pitch change
                        # End previous note
                        duration = time - note_start_time
                        if duration > 0.1:  # Minimum note length
                            midi_notes.append(MIDINote(
                                note=int(current_note),
                                velocity=int(80 + conf * 40),  # 80-120 based on confidence
                                duration=duration
                            ))

                        # Start new note
                        current_note = midi_num
                        note_start_time = time
                else:
                    # Silence - end current note
                    if current_note is not None and note_start_time is not None:
                        duration = time - note_start_time
                        if duration > 0.1:
                            midi_notes.append(MIDINote(
                                note=int(current_note),
                                velocity=100,
                                duration=duration
                            ))

                        current_note = None
                        note_start_time = None

            # Handle last note
            if current_note is not None and note_start_time is not None:
                duration = timestamps[-1] - note_start_time
                if duration > 0.1:
                    midi_notes.append(MIDINote(
                        note=int(current_note),
                        velocity=100,
                        duration=duration
                    ))

            phrase.midi_notes = midi_notes
            print(f"[HummingDetector] Detected {len(midi_notes)} notes")

        except Exception as e:
            print(f"[HummingDetector] Error converting to MIDI: {e}")
            import traceback
            traceback.print_exc()

    def _hz_to_midi(self, frequency: float) -> float:
        """
        Convert frequency in Hz to MIDI note number

        Args:
            frequency: Frequency in Hz

        Returns:
            MIDI note number (can be float for microtones)
        """
        if frequency <= 0:
            return 0

        # MIDI note = 69 + 12 * log2(f / 440)
        return 69 + 12 * np.log2(frequency / 440.0)

    def add_pitch_callback(self, callback: Callable) -> None:
        """
        Add callback for real-time pitch detection

        Callback signature: async def callback(pitch_hz: float, confidence: float)
        """
        self._pitch_callbacks.append(callback)

    def remove_pitch_callback(self, callback: Callable) -> None:
        """Remove pitch callback"""
        if callback in self._pitch_callbacks:
            self._pitch_callbacks.remove(callback)

    async def play_back_as_midi(self, phrase: HummingPhrase, midi_handler) -> None:
        """
        Play back a humming phrase as MIDI

        Args:
            phrase: HummingPhrase to play
            midi_handler: MIDIHandler instance
        """
        if not phrase.midi_notes:
            print("[HummingDetector] No MIDI notes to play")
            return

        print(f"[HummingDetector] Playing back {len(phrase.midi_notes)} notes")

        for note in phrase.midi_notes:
            await midi_handler.send_note_async(note)

        print("[HummingDetector] Playback complete")

    def cleanup_old_recordings(self, keep_recent: int = 10) -> None:
        """Clean up old humming recordings"""
        try:
            files = sorted(
                self._output_dir.glob("humming_*.wav"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )

            for file in files[keep_recent:]:
                file.unlink()
                print(f"[HummingDetector] Removed: {file.name}")

        except Exception as e:
            print(f"[HummingDetector] Cleanup error: {e}")


# Example usage
async def _example_usage():
    """Example usage of HummingDetector"""
    from avatar.audio.midi_handler import MIDIHandler

    detector = HummingDetector()

    # List devices
    print("Available input devices:")
    for idx, name in detector.list_input_devices():
        print(f"  {idx}: {name}")

    # Record for 5 seconds
    if await detector.start_recording():
        await asyncio.sleep(5)
        phrase = await detector.stop_recording()

        if phrase and phrase.midi_notes:
            print(f"Detected {len(phrase.midi_notes)} notes:")
            for note in phrase.midi_notes[:5]:
                print(f"  Note: {note.note}, Duration: {note.duration:.2f}s")

            # Play back
            midi = MIDIHandler()
            if midi.open_output():
                await detector.play_back_as_midi(phrase, midi)
                midi.close()


if __name__ == "__main__":
    asyncio.run(_example_usage())
