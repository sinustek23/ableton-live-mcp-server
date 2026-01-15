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
from avatar.gui.transparent_window import TransparentAvatarWindow
from avatar.brain.ai_controller import AIController, AIConfig
from avatar.brain.mode_manager import ModeManager, Mode
from avatar.audio.ableton_connector import AbletonConnector, AbletonConnectionConfig
from avatar.audio.midi_handler import MIDIHandler


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

            self._initialized = True
            print("[Avatar] ✅ Initialization complete!")
            print("[Avatar] Right-click the avatar to change modes")

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
