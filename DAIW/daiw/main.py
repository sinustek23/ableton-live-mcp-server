"""
Main Entry Point for Music Copilot Avatar

Startet den Desktop-Avatar mit allen Komponenten
"""

import sys
import asyncio
from typing import Optional
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
import qasync

# Avatar components
from daiw.gui.transparent_window import TransparentAvatarWindow
from daiw.gui.feature_dialogs import (
    YouTubeAnalyzerDialog,
    STEMSeparatorDialog,
    HummingRecorderDialog,
    FeatureMenuDialog
)
from daiw.brain.ai_controller import AIController, AIConfig
from daiw.brain.mode_manager import ModeManager, Mode
from daiw.brain.feature_manager import InteractiveFeatureManager
from daiw.audio.ableton_connector import AbletonConnector, AbletonConnectionConfig
from daiw.audio.midi_handler import MIDIHandler


class MusicCopilotAvatar:
    """
    Main application class for the Music Copilot Avatar
    """

    def __init__(self, app: QApplication):
        self.app = app

        # Components (will be initialized)
        self.window: Optional[TransparentAvatarWindow] = None
        self.ai_controller: Optional[AIController] = None
        self.ableton_connector: Optional[AbletonConnector] = None
        self.midi_handler: Optional[MIDIHandler] = None
        self.mode_manager: Optional[ModeManager] = None
        self.feature_manager: Optional[InteractiveFeatureManager] = None

        # Dialogs
        self.youtube_dialog: Optional[YouTubeAnalyzerDialog] = None
        self.stem_dialog: Optional[STEMSeparatorDialog] = None
        self.humming_dialog: Optional[HummingRecorderDialog] = None
        self.feature_menu_dialog: Optional[FeatureMenuDialog] = None

        # Connection status
        self._initialized = False

    async def initialize(self) -> bool:
        """
        Initialize all components

        Returns:
            True if initialization successful
        """
        print("[Avatar] Initializing Music Copilot Avatar...")

        try:
            # 1. Initialize GUI
            print("[Avatar] Creating GUI window...")
            self.window = TransparentAvatarWindow()

            # Connect signals
            self.window.mode_changed.connect(self._on_mode_changed)
            self.window.exit_requested.connect(self._on_exit_requested)

            # Connect interactive feature signals
            self.window.interactive_features_requested.connect(self._on_show_feature_menu)
            self.window.youtube_analyze_requested.connect(self._on_show_youtube_dialog)
            self.window.stem_separate_requested.connect(self._on_show_stem_dialog)
            self.window.humming_record_requested.connect(self._on_show_humming_dialog)

            # Show window
            self.window.show()

            # 2. Initialize AI Controller
            print("[Avatar] Initializing AI controller...")
            ai_config = AIConfig(
                provider="anthropic",  # or "openai"
                model="claude-3-5-sonnet-20241022",
                temperature=0.7
            )
            self.ai_controller = AIController(config=ai_config)

            # 3. Initialize MIDI Handler
            print("[Avatar] Initializing MIDI handler...")
            self.midi_handler = MIDIHandler()

            # Try to open MIDI ports
            print("[Avatar] Available MIDI output ports:")
            for port in self.midi_handler.list_output_ports():
                print(f"  - {port}")

            if self.midi_handler.open_output():
                print("[Avatar] MIDI output opened successfully")
            else:
                print("[Avatar] Warning: Could not open MIDI output port")

            # 4. Initialize Ableton Connector
            print("[Avatar] Initializing Ableton connector...")
            ableton_config = AbletonConnectionConfig()
            self.ableton_connector = AbletonConnector(config=ableton_config)

            # Try to connect (non-blocking, will retry later if fails)
            connected = await self.ableton_connector.connect()
            if connected:
                print("[Avatar] Connected to Ableton OSC daemon")
                status = await self.ableton_connector.get_status()
                print(f"[Avatar] Daemon status: {status}")
            else:
                print("[Avatar] Warning: Could not connect to Ableton daemon")
                print("[Avatar] Make sure osc_daemon.py is running")

            # 5. Initialize Mode Manager
            print("[Avatar] Initializing mode manager...")
            self.mode_manager = ModeManager(
                ai_controller=self.ai_controller,
                ableton_connector=self.ableton_connector,
                midi_handler=self.midi_handler
            )

            # Set initial mode to IDLE
            await self.mode_manager.set_mode(Mode.IDLE)

            # 6. Initialize Interactive Feature Manager
            print("[Avatar] Initializing interactive features...")
            self.feature_manager = InteractiveFeatureManager(
                ai_controller=self.ai_controller,
                midi_handler=self.midi_handler
            )

            self._initialized = True
            print("[Avatar] ✅ Initialization complete!")
            print("[Avatar] Right-click the avatar to access modes and features")
            print("[Avatar] Try: YouTube Analyzer, STEM Separator, or Humming Recorder!")

            return True

        except Exception as e:
            print(f"[Avatar] ❌ Initialization failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def shutdown(self) -> None:
        """Shutdown all components gracefully"""
        print("[Avatar] Shutting down...")

        try:
            # Set mode to idle
            if self.mode_manager:
                await self.mode_manager.set_mode(Mode.IDLE)

            # Close MIDI
            if self.midi_handler:
                self.midi_handler.close()

            # Disconnect from Ableton
            if self.ableton_connector:
                await self.ableton_connector.disconnect()

            # Close window
            if self.window:
                self.window.close()

            print("[Avatar] Shutdown complete")

        except Exception as e:
            print(f"[Avatar] Error during shutdown: {e}")

    def _on_mode_changed(self, mode_str: str) -> None:
        """Handle mode change from GUI"""
        if not self.mode_manager:
            return

        # Map string to Mode enum
        mode_map = {
            "idle": Mode.IDLE,
            "jam": Mode.JAM,
            "learn": Mode.LEARN,
            "lock": Mode.LOCK,
        }

        mode = mode_map.get(mode_str)
        if mode:
            # Set mode (async)
            asyncio.create_task(self._async_set_mode(mode))

    async def _async_set_mode(self, mode: Mode) -> None:
        """Asynchronously set mode"""
        if self.window:
            self.window.set_thinking_state(True)

        success = await self.mode_manager.set_mode(mode)

        if self.window:
            self.window.set_thinking_state(False)

        if success:
            print(f"[Avatar] Mode changed to: {mode.value}")
        else:
            print(f"[Avatar] Failed to change mode to: {mode.value}")

    def _on_exit_requested(self) -> None:
        """Handle exit request from GUI"""
        print("[Avatar] Exit requested")
        asyncio.create_task(self._async_exit())

    async def _async_exit(self) -> None:
        """Asynchronously exit application"""
        await self.shutdown()
        self.app.quit()

    # ========== Interactive Feature Handlers ==========

    def _on_show_feature_menu(self) -> None:
        """Show the feature selection menu"""
        if not self.feature_menu_dialog:
            self.feature_menu_dialog = FeatureMenuDialog(self.window)
            self.feature_menu_dialog.youtube_requested.connect(self._on_show_youtube_dialog)
            self.feature_menu_dialog.stem_requested.connect(self._on_show_stem_dialog)
            self.feature_menu_dialog.humming_requested.connect(self._on_show_humming_dialog)

        self.feature_menu_dialog.show()

    def _on_show_youtube_dialog(self) -> None:
        """Show YouTube analyzer dialog"""
        if not self.youtube_dialog:
            self.youtube_dialog = YouTubeAnalyzerDialog(self.window)
            self.youtube_dialog.analyze_requested.connect(self._on_analyze_youtube)

        self.youtube_dialog.show()

    def _on_show_stem_dialog(self) -> None:
        """Show STEM separator dialog"""
        if not self.stem_dialog:
            self.stem_dialog = STEMSeparatorDialog(self.window)
            self.stem_dialog.separate_requested.connect(self._on_separate_stem)

        self.stem_dialog.show()

    def _on_show_humming_dialog(self) -> None:
        """Show humming recorder dialog"""
        if not self.humming_dialog:
            self.humming_dialog = HummingRecorderDialog(self.window)

            # Connect signals
            self.humming_dialog.record_requested.connect(self._on_start_humming)
            self.humming_dialog.stop_requested.connect(self._on_stop_humming)
            self.humming_dialog.playback_requested.connect(self._on_playback_humming)

            # Set available devices
            devices = self.feature_manager.list_audio_input_devices()
            self.humming_dialog.set_devices(devices)

        self.humming_dialog.show()

    def _on_analyze_youtube(self, url: str) -> None:
        """Handle YouTube analysis request"""
        asyncio.create_task(self._async_analyze_youtube(url))

    async def _async_analyze_youtube(self, url: str) -> None:
        """Asynchronously analyze YouTube track"""
        if not self.feature_manager or not self.youtube_dialog:
            return

        # Progress callback
        async def progress(value: int, status: str):
            self.youtube_dialog.set_progress(value, status)

        # Analyze
        track = await self.feature_manager.analyze_youtube_song(url, progress)

        if track:
            # Format results
            results = f"""Title: {track.title}
Artist: {track.artist or 'Unknown'}
Duration: {track.duration:.1f} seconds

Musical Analysis:
- Tempo: {track.tempo:.1f} BPM
- Key: {track.key}
- Energy: {track.energy:.3f}
- Style: {track.style}
"""
            self.youtube_dialog.set_results(results)
        else:
            self.youtube_dialog.set_results("Analysis failed. Check the URL/query.")

    def _on_separate_stem(self, file_path: str, stem_types: list) -> None:
        """Handle STEM separation request"""
        asyncio.create_task(self._async_separate_stem(file_path, stem_types))

    async def _async_separate_stem(self, file_path: str, stem_types: list) -> None:
        """Asynchronously separate stems"""
        if not self.feature_manager or not self.stem_dialog:
            return

        from pathlib import Path

        # Progress callback
        async def progress(value: float, status: str):
            self.stem_dialog.set_progress(value, status)

        # Separate
        stems = await self.feature_manager.separate_stems(
            Path(file_path),
            stems_to_extract=stem_types,
            progress_callback=progress
        )

        if stems:
            print(f"[Avatar] Stems saved to: {stems.output_dir}")

    def _on_start_humming(self) -> None:
        """Handle start humming recording"""
        asyncio.create_task(self._async_start_humming())

    async def _async_start_humming(self) -> None:
        """Asynchronously start humming recording"""
        if not self.feature_manager:
            return

        # Add pitch callback for real-time display
        async def pitch_callback(hz: float, confidence: float):
            if self.humming_dialog:
                # Convert Hz to note name
                import numpy as np
                midi_num = 69 + 12 * np.log2(hz / 440.0)
                note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
                note_name = note_names[int(midi_num) % 12]
                octave = int(midi_num // 12) - 1
                self.humming_dialog.update_pitch(hz, f"{note_name}{octave}")

        self.feature_manager.add_humming_pitch_callback(pitch_callback)

        # Start recording
        await self.feature_manager.start_humming_recording()

    def _on_stop_humming(self) -> None:
        """Handle stop humming recording"""
        asyncio.create_task(self._async_stop_humming())

    async def _async_stop_humming(self) -> None:
        """Asynchronously stop humming recording"""
        if not self.feature_manager or not self.humming_dialog:
            return

        # Stop recording
        phrase = await self.feature_manager.stop_humming_recording()

        if phrase and phrase.midi_notes:
            # Format results
            results = f"""Recorded {phrase.duration:.2f} seconds
Detected {len(phrase.midi_notes)} notes:

"""
            for i, note in enumerate(phrase.midi_notes[:10], 1):
                note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
                note_name = note_names[note.note % 12]
                octave = (note.note // 12) - 1
                results += f"{i}. {note_name}{octave} ({note.duration:.2f}s)\n"

            if len(phrase.midi_notes) > 10:
                results += f"... and {len(phrase.midi_notes) - 10} more notes\n"

            self.humming_dialog.set_results(results)

    def _on_playback_humming(self) -> None:
        """Handle playback humming as MIDI"""
        asyncio.create_task(self._async_playback_humming())

    async def _async_playback_humming(self) -> None:
        """Asynchronously play back humming as MIDI"""
        if not self.feature_manager:
            return

        await self.feature_manager.playback_humming_as_midi()


async def main():
    """Main entry point"""
    # Create Qt Application
    app = QApplication(sys.argv)

    # Create event loop
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)

    # Create avatar
    avatar = MusicCopilotAvatar(app)

    # Initialize
    success = await avatar.initialize()

    if not success:
        print("[Avatar] Failed to initialize. Exiting...")
        sys.exit(1)

    # Run event loop
    with loop:
        loop.run_forever()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[Avatar] Interrupted by user")
        sys.exit(0)
