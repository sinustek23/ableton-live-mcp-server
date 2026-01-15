"""
Command Palette - Quick access to all DAIW features (Cmd+K / Ctrl+K)

Provides fuzzy search across all features, modes, actions, and commands
"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import re


class CommandCategory(Enum):
    """Categories for organizing commands"""
    MODE = "mode"
    FEATURE = "feature"
    AUDIO = "audio"
    AI = "ai"
    NETWORK = "network"
    PRESET = "preset"
    VIEW = "view"
    SYSTEM = "system"
    RECENT = "recent"


@dataclass
class Command:
    """Represents a single command in the palette"""
    id: str
    title: str
    description: str
    category: CommandCategory
    keywords: List[str]
    icon: str
    callback: Optional[Callable] = None
    shortcut: Optional[str] = None
    enabled: bool = True


class CommandPalette:
    """
    Command Palette system for quick access to all DAIW features

    Features:
    - Fuzzy search across all commands
    - Category filtering
    - Recent commands tracking
    - Keyboard shortcuts display
    - Context-aware suggestions
    """

    def __init__(self):
        self.commands: Dict[str, Command] = {}
        self.recent_commands: List[str] = []
        self.max_recent = 10

        # Initialize built-in commands
        self._register_builtin_commands()

    def _register_builtin_commands(self) -> None:
        """Register all built-in DAIW commands"""

        # Mode commands
        self.register_command(Command(
            id="mode.idle",
            title="Switch to Idle Mode",
            description="Passive observation mode",
            category=CommandCategory.MODE,
            keywords=["idle", "passive", "rest"],
            icon="💤",
            shortcut="Ctrl+1"
        ))

        self.register_command(Command(
            id="mode.jam",
            title="Switch to Jam Mode",
            description="AI generates musical ideas in real-time",
            category=CommandCategory.MODE,
            keywords=["jam", "freestyle", "improvise", "play"],
            icon="🎸",
            shortcut="Ctrl+2"
        ))

        self.register_command(Command(
            id="mode.learn",
            title="Switch to Learn Mode",
            description="Avatar observes and learns your playing style",
            category=CommandCategory.MODE,
            keywords=["learn", "watch", "observe", "analyze"],
            icon="👁️",
            shortcut="Ctrl+3"
        ))

        self.register_command(Command(
            id="mode.lock",
            title="Switch to Lock Mode",
            description="Meta-programming - generate custom skills",
            category=CommandCategory.MODE,
            keywords=["lock", "meta", "generate", "automate"],
            icon="🔒",
            shortcut="Ctrl+4"
        ))

        # Audio features
        self.register_command(Command(
            id="audio.youtube",
            title="Analyze YouTube Song",
            description="Download and analyze tempo, key, style from YouTube",
            category=CommandCategory.AUDIO,
            keywords=["youtube", "reference", "analyze", "download"],
            icon="🎥",
            shortcut="Ctrl+Y"
        ))

        self.register_command(Command(
            id="audio.stem",
            title="Separate STEM",
            description="Extract vocals, drums, bass, and other from audio",
            category=CommandCategory.AUDIO,
            keywords=["stem", "separate", "isolate", "demucs"],
            icon="✂️",
            shortcut="Ctrl+S"
        ))

        self.register_command(Command(
            id="audio.humming",
            title="Humming to MIDI",
            description="Record humming and convert to MIDI notes",
            category=CommandCategory.AUDIO,
            keywords=["hum", "sing", "melody", "record", "pitch"],
            icon="🎤",
            shortcut="Ctrl+H"
        ))

        # AI features
        self.register_command(Command(
            id="ai.generate_melody",
            title="Generate Melody",
            description="AI generates a melodic phrase",
            category=CommandCategory.AI,
            keywords=["generate", "melody", "ai", "create"],
            icon="🎵"
        ))

        self.register_command(Command(
            id="ai.generate_harmony",
            title="Generate Harmony",
            description="AI creates harmonic progressions",
            category=CommandCategory.AI,
            keywords=["generate", "harmony", "chords", "progression"],
            icon="🎹"
        ))

        self.register_command(Command(
            id="ai.generate_rhythm",
            title="Generate Rhythm",
            description="AI creates rhythmic patterns",
            category=CommandCategory.AI,
            keywords=["generate", "rhythm", "drums", "pattern"],
            icon="🥁"
        ))

        self.register_command(Command(
            id="ai.harmonize",
            title="Harmonize Melody",
            description="Add harmonies to current melody",
            category=CommandCategory.AI,
            keywords=["harmonize", "chords", "accompany"],
            icon="🎼"
        ))

        self.register_command(Command(
            id="ai.assistant",
            title="AI Assistant Chat",
            description="Talk to AI about anything (not just music!)",
            category=CommandCategory.AI,
            keywords=["chat", "ask", "assistant", "help"],
            icon="💬",
            shortcut="Ctrl+/"
        ))

        # Network features
        self.register_command(Command(
            id="network.collabnet_host",
            title="Host CollabNet Session",
            description="Start a collaborative session as host",
            category=CommandCategory.NETWORK,
            keywords=["collaborate", "host", "server", "collabnet"],
            icon="🌐"
        ))

        self.register_command(Command(
            id="network.collabnet_join",
            title="Join CollabNet Session",
            description="Join an existing collaborative session",
            category=CommandCategory.NETWORK,
            keywords=["collaborate", "join", "client", "collabnet"],
            icon="🔗"
        ))

        # Preset features
        self.register_command(Command(
            id="preset.save",
            title="Save Preset",
            description="Save current configuration as preset",
            category=CommandCategory.PRESET,
            keywords=["save", "preset", "template", "store"],
            icon="💾",
            shortcut="Ctrl+Shift+S"
        ))

        self.register_command(Command(
            id="preset.load",
            title="Load Preset",
            description="Load a saved preset",
            category=CommandCategory.PRESET,
            keywords=["load", "preset", "template", "open"],
            icon="📂",
            shortcut="Ctrl+O"
        ))

        self.register_command(Command(
            id="preset.manage",
            title="Manage Presets",
            description="Browse and organize presets",
            category=CommandCategory.PRESET,
            keywords=["manage", "organize", "presets"],
            icon="📋"
        ))

        # View features
        self.register_command(Command(
            id="view.mini_mode",
            title="Toggle Mini Mode",
            description="Collapse to minimal view",
            category=CommandCategory.VIEW,
            keywords=["mini", "collapse", "minimize", "compact"],
            icon="⚡",
            shortcut="Ctrl+M"
        ))

        self.register_command(Command(
            id="view.status_bar",
            title="Toggle Status Bar",
            description="Show/hide status bar",
            category=CommandCategory.VIEW,
            keywords=["status", "bar", "info"],
            icon="📊"
        ))

        self.register_command(Command(
            id="view.floating_menu",
            title="Toggle Floating Menu",
            description="Show/hide floating quick access menu",
            category=CommandCategory.VIEW,
            keywords=["floating", "menu", "bubble"],
            icon="🔘",
            shortcut="Ctrl+Space"
        ))

        # System features
        self.register_command(Command(
            id="system.settings",
            title="Settings",
            description="Open settings dialog",
            category=CommandCategory.SYSTEM,
            keywords=["settings", "preferences", "config"],
            icon="⚙️",
            shortcut="Ctrl+,"
        ))

        self.register_command(Command(
            id="system.shortcuts",
            title="Keyboard Shortcuts",
            description="View all keyboard shortcuts",
            category=CommandCategory.SYSTEM,
            keywords=["shortcuts", "hotkeys", "keyboard"],
            icon="⌨️",
            shortcut="Ctrl+?"
        ))

        self.register_command(Command(
            id="system.tutorial",
            title="Interactive Tutorial",
            description="Learn DAIW features interactively",
            category=CommandCategory.SYSTEM,
            keywords=["tutorial", "help", "learn", "guide"],
            icon="🎓"
        ))

        self.register_command(Command(
            id="system.undo",
            title="Undo",
            description="Undo last action",
            category=CommandCategory.SYSTEM,
            keywords=["undo", "revert", "back"],
            icon="↶",
            shortcut="Ctrl+Z"
        ))

        self.register_command(Command(
            id="system.redo",
            title="Redo",
            description="Redo last undone action",
            category=CommandCategory.SYSTEM,
            keywords=["redo", "forward"],
            icon="↷",
            shortcut="Ctrl+Shift+Z"
        ))

        self.register_command(Command(
            id="system.backup",
            title="Backup Workspace",
            description="Create backup of entire workspace",
            category=CommandCategory.SYSTEM,
            keywords=["backup", "save", "export"],
            icon="💼"
        ))

        self.register_command(Command(
            id="system.restore",
            title="Restore Workspace",
            description="Restore from backup",
            category=CommandCategory.SYSTEM,
            keywords=["restore", "load", "import"],
            icon="📥"
        ))

    def register_command(self, command: Command) -> None:
        """Register a new command"""
        self.commands[command.id] = command

    def unregister_command(self, command_id: str) -> None:
        """Unregister a command"""
        if command_id in self.commands:
            del self.commands[command_id]

    def get_command(self, command_id: str) -> Optional[Command]:
        """Get a command by ID"""
        return self.commands.get(command_id)

    def search(self, query: str, max_results: int = 10) -> List[Command]:
        """
        Fuzzy search for commands

        Args:
            query: Search query
            max_results: Maximum number of results to return

        Returns:
            List of matching commands sorted by relevance
        """
        if not query:
            # Return recent commands if no query
            return self._get_recent_commands()

        query = query.lower()
        results = []

        for cmd in self.commands.values():
            if not cmd.enabled:
                continue

            score = self._calculate_match_score(cmd, query)
            if score > 0:
                results.append((score, cmd))

        # Sort by score descending
        results.sort(key=lambda x: x[0], reverse=True)

        return [cmd for _, cmd in results[:max_results]]

    def _calculate_match_score(self, command: Command, query: str) -> float:
        """
        Calculate match score for fuzzy search

        Returns:
            Score (higher is better, 0 means no match)
        """
        score = 0.0

        # Title exact match (highest priority)
        if query in command.title.lower():
            score += 100
            if command.title.lower().startswith(query):
                score += 50

        # Description match
        if query in command.description.lower():
            score += 30

        # Keywords match
        for keyword in command.keywords:
            if query in keyword.lower():
                score += 20
                if keyword.lower().startswith(query):
                    score += 10

        # Category match
        if query in command.category.value:
            score += 10

        # Fuzzy match (character sequence)
        if self._fuzzy_match(query, command.title.lower()):
            score += 15

        return score

    def _fuzzy_match(self, query: str, text: str) -> bool:
        """
        Check if query characters appear in order in text

        Example: "ytb" matches "YouTube"
        """
        query_idx = 0
        for char in text:
            if query_idx < len(query) and char == query[query_idx]:
                query_idx += 1
        return query_idx == len(query)

    def _get_recent_commands(self) -> List[Command]:
        """Get recently executed commands"""
        recent = []
        for cmd_id in self.recent_commands:
            cmd = self.get_command(cmd_id)
            if cmd and cmd.enabled:
                recent.append(cmd)
        return recent

    def execute_command(self, command_id: str) -> bool:
        """
        Execute a command by ID

        Args:
            command_id: Command identifier

        Returns:
            True if executed successfully
        """
        command = self.get_command(command_id)
        if not command or not command.enabled:
            return False

        # Add to recent
        self._add_to_recent(command_id)

        # Execute callback if available
        if command.callback:
            try:
                command.callback()
                return True
            except Exception as e:
                print(f"[CommandPalette] Error executing {command_id}: {e}")
                return False

        return True

    def _add_to_recent(self, command_id: str) -> None:
        """Add command to recent list"""
        # Remove if already in list
        if command_id in self.recent_commands:
            self.recent_commands.remove(command_id)

        # Add to front
        self.recent_commands.insert(0, command_id)

        # Trim to max size
        if len(self.recent_commands) > self.max_recent:
            self.recent_commands = self.recent_commands[:self.max_recent]

    def get_commands_by_category(self, category: CommandCategory) -> List[Command]:
        """Get all commands in a category"""
        return [
            cmd for cmd in self.commands.values()
            if cmd.category == category and cmd.enabled
        ]

    def get_all_categories(self) -> List[CommandCategory]:
        """Get all available categories"""
        categories = set()
        for cmd in self.commands.values():
            if cmd.enabled:
                categories.add(cmd.category)
        return sorted(list(categories), key=lambda c: c.value)

    def set_command_callback(self, command_id: str, callback: Callable) -> bool:
        """
        Set/update callback for a command

        Args:
            command_id: Command identifier
            callback: Function to call when command executed

        Returns:
            True if successful
        """
        command = self.get_command(command_id)
        if not command:
            return False

        command.callback = callback
        return True

    def enable_command(self, command_id: str) -> None:
        """Enable a command"""
        command = self.get_command(command_id)
        if command:
            command.enabled = True

    def disable_command(self, command_id: str) -> None:
        """Disable a command"""
        command = self.get_command(command_id)
        if command:
            command.enabled = False

    def get_command_by_shortcut(self, shortcut: str) -> Optional[Command]:
        """Find command by keyboard shortcut"""
        for cmd in self.commands.values():
            if cmd.shortcut == shortcut and cmd.enabled:
                return cmd
        return None

    def clear_recent(self) -> None:
        """Clear recent commands list"""
        self.recent_commands.clear()
