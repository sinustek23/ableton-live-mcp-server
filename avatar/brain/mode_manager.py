"""
Mode Manager - Manages different operational modes of the avatar

Modes:
- Idle: Just observing
- Jam: Freestyle jam session (Call & Response)
- Learn: Learning by watching user play
- Lock: Meta-programming mode (creates new skills)
"""

from typing import Optional, List, Dict, Any, Callable
import asyncio
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import importlib.util
import sys

from avatar.brain.ai_controller import AIController
from avatar.audio.ableton_connector import AbletonConnector
from avatar.audio.midi_handler import MIDIHandler, MIDINote
from avatar.dynamic_tools import music_theory


class Mode(Enum):
    """Avatar operational modes"""
    IDLE = "idle"
    JAM = "jam"
    LEARN = "learn"
    LOCK = "lock"


@dataclass
class LearningSession:
    """Data structure for a learning session"""
    start_time: datetime
    midi_events: List[Dict[str, Any]] = field(default_factory=list)
    analysis: Optional[Dict[str, Any]] = None
    generated_skill: Optional[str] = None


class ModeManager:
    """
    Manages operational modes and coordinates between AI, MIDI, and Ableton
    """

    def __init__(
        self,
        ai_controller: AIController,
        ableton_connector: AbletonConnector,
        midi_handler: MIDIHandler
    ):
        self.ai = ai_controller
        self.ableton = ableton_connector
        self.midi = midi_handler

        # Current mode
        self._current_mode = Mode.IDLE

        # Mode-specific data
        self._learning_session: Optional[LearningSession] = None
        self._jam_task: Optional[asyncio.Task] = None

        # Loaded skills (Lock Mode)
        self._loaded_skills: Dict[str, Any] = {}

        # Callbacks
        self._mode_change_callbacks: List[Callable] = []

        # Skills directory
        self._skills_dir = Path(__file__).parent.parent / "dynamic_tools" / "generated_skills"
        self._skills_dir.mkdir(parents=True, exist_ok=True)

    def get_current_mode(self) -> Mode:
        """Get current operational mode"""
        return self._current_mode

    async def set_mode(self, mode: Mode) -> bool:
        """
        Set operational mode

        Args:
            mode: New mode to switch to

        Returns:
            True if mode switch successful
        """
        if self._current_mode == mode:
            return True

        # Clean up previous mode
        await self._cleanup_current_mode()

        # Set new mode
        self._current_mode = mode

        # Initialize new mode
        success = await self._initialize_mode(mode)

        # Notify callbacks
        for callback in self._mode_change_callbacks:
            await callback(mode)

        return success

    async def _cleanup_current_mode(self) -> None:
        """Clean up resources from current mode"""
        if self._current_mode == Mode.JAM:
            # Stop jam session
            if self._jam_task and not self._jam_task.done():
                self._jam_task.cancel()
                try:
                    await self._jam_task
                except asyncio.CancelledError:
                    pass

        elif self._current_mode == Mode.LEARN:
            # Finalize learning session
            if self._learning_session:
                await self._finalize_learning_session()

        elif self._current_mode == Mode.LOCK:
            # Nothing to clean up for now
            pass

    async def _initialize_mode(self, mode: Mode) -> bool:
        """Initialize a new mode"""
        try:
            if mode == Mode.IDLE:
                print("[ModeManager] Entering Idle mode")
                return True

            elif mode == Mode.JAM:
                print("[ModeManager] Entering Jam mode")
                # Start jam session in background
                self._jam_task = asyncio.create_task(self._jam_session())
                return True

            elif mode == Mode.LEARN:
                print("[ModeManager] Entering Learn mode")
                # Start new learning session
                self._learning_session = LearningSession(start_time=datetime.now())
                # Start MIDI listener
                await self.midi.start_listening()
                self.midi.add_note_callback(self._on_midi_input)
                return True

            elif mode == Mode.LOCK:
                print("[ModeManager] Entering Lock mode")
                # Analyze learned patterns and generate skill
                await self._enter_lock_mode()
                return True

            return False

        except Exception as e:
            print(f"[ModeManager] Error initializing mode {mode}: {e}")
            return False

    # ========== JAM MODE ==========

    async def _jam_session(self) -> None:
        """Run a jam session (Call & Response)"""
        print("[ModeManager] Starting jam session...")

        try:
            while True:
                # Generate a musical idea
                idea = await self.ai.generate_musical_idea(
                    "Create a short 4-note melodic phrase",
                    constraints={"key": "C", "scale": "major"}
                )

                print(f"[Jam] Playing: {idea.get('description', 'musical idea')}")

                # Play the idea
                notes = idea.get("notes", [60, 64, 67, 72])
                durations = idea.get("durations", [0.5] * len(notes))
                velocities = idea.get("velocities", [100] * len(notes))

                for note, duration, velocity in zip(notes, durations, velocities):
                    midi_note = MIDINote(note=note, velocity=velocity, duration=duration)
                    await self.midi.send_note_async(midi_note)

                # Wait before next phrase
                await asyncio.sleep(2.0)

        except asyncio.CancelledError:
            print("[ModeManager] Jam session stopped")
        except Exception as e:
            print(f"[ModeManager] Error in jam session: {e}")

    # ========== LEARN MODE ==========

    async def _on_midi_input(self, msg) -> None:
        """Callback for MIDI input during learning"""
        if not self._learning_session:
            return

        # Record MIDI event
        event = {
            "type": msg.type,
            "note": getattr(msg, 'note', None),
            "velocity": getattr(msg, 'velocity', None),
            "time": datetime.now().isoformat()
        }

        self._learning_session.midi_events.append(event)
        print(f"[Learn] Recorded: {msg}")

    async def _finalize_learning_session(self) -> None:
        """Finalize the learning session and analyze patterns"""
        if not self._learning_session:
            return

        print(f"[Learn] Finalizing session. Recorded {len(self._learning_session.midi_events)} events")

        # Stop MIDI listener
        self.midi.stop_listening()
        self.midi.remove_note_callback(self._on_midi_input)

        # Analyze pattern if we have enough data
        if len(self._learning_session.midi_events) > 10:
            print("[Learn] Analyzing pattern...")
            analysis = await self.ai.analyze_pattern(self._learning_session.midi_events)
            self._learning_session.analysis = analysis
            print(f"[Learn] Analysis: {analysis}")

    # ========== LOCK MODE ==========

    async def _enter_lock_mode(self) -> None:
        """Enter Lock Mode - analyze patterns and generate skills"""
        print("[Lock] Analyzing workflow and generating skill...")

        # Get analysis from learning session
        analysis = None
        if self._learning_session and self._learning_session.analysis:
            analysis = self._learning_session.analysis
        else:
            # Ask AI to analyze current context
            analysis = await self.ai.analyze_pattern([])

        # Generate task description based on analysis
        task_description = f"""Create a skill that automates the following musical pattern:
{analysis}

The skill should monitor user input and automatically complement their playing.
"""

        # Generate skill code
        print("[Lock] Generating skill code...")
        skill_code = await self.ai.generate_skill_code(task_description, analysis)

        # Save skill
        skill_filename = f"skill_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        skill_path = self._skills_dir / skill_filename

        with open(skill_path, "w") as f:
            f.write(skill_code)

        print(f"[Lock] Skill saved to: {skill_path}")

        # Load and execute skill
        success = await self._load_skill(skill_path)
        if success:
            print("[Lock] Skill loaded and ready!")
        else:
            print("[Lock] Failed to load skill")

        # Store in learning session
        if self._learning_session:
            self._learning_session.generated_skill = skill_filename

    async def _load_skill(self, skill_path: Path) -> bool:
        """
        Dynamically load a skill module

        Args:
            skill_path: Path to the skill .py file

        Returns:
            True if loaded successfully
        """
        try:
            # Import the module
            spec = importlib.util.spec_from_file_location(skill_path.stem, skill_path)
            if not spec or not spec.loader:
                print(f"[Lock] Failed to load spec for {skill_path}")
                return False

            module = importlib.util.module_from_spec(spec)
            sys.modules[skill_path.stem] = module
            spec.loader.exec_module(module)

            # Extract skill metadata
            skill_name = getattr(module, 'SKILL_NAME', skill_path.stem)
            skill_description = getattr(module, 'SKILL_DESCRIPTION', 'No description')

            # Store the skill
            self._loaded_skills[skill_name] = {
                'module': module,
                'path': skill_path,
                'description': skill_description,
                'execute': getattr(module, 'execute_skill', None)
            }

            print(f"[Lock] Loaded skill: {skill_name}")
            print(f"[Lock] Description: {skill_description}")

            return True

        except Exception as e:
            print(f"[Lock] Error loading skill from {skill_path}: {e}")
            return False

    async def execute_skill(self, skill_name: str, **kwargs) -> Any:
        """
        Execute a loaded skill

        Args:
            skill_name: Name of the skill to execute
            **kwargs: Arguments to pass to the skill

        Returns:
            Result from skill execution
        """
        if skill_name not in self._loaded_skills:
            print(f"[Lock] Skill not found: {skill_name}")
            return None

        skill = self._loaded_skills[skill_name]
        execute_func = skill.get('execute')

        if not execute_func:
            print(f"[Lock] Skill {skill_name} has no execute_skill function")
            return None

        try:
            # Execute skill with context
            result = await execute_func(
                midi_handler=self.midi,
                ableton_connector=self.ableton,
                **kwargs
            )
            return result

        except Exception as e:
            print(f"[Lock] Error executing skill {skill_name}: {e}")
            return None

    def list_loaded_skills(self) -> List[Dict[str, str]]:
        """Get list of loaded skills"""
        return [
            {
                'name': name,
                'description': skill['description'],
                'path': str(skill['path'])
            }
            for name, skill in self._loaded_skills.items()
        ]

    # ========== Callbacks ==========

    def add_mode_change_callback(self, callback: Callable) -> None:
        """Register a callback for mode changes"""
        self._mode_change_callbacks.append(callback)

    def remove_mode_change_callback(self, callback: Callable) -> None:
        """Remove a registered callback"""
        if callback in self._mode_change_callbacks:
            self._mode_change_callbacks.remove(callback)
