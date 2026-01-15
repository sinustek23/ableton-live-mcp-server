"""
Global Keyboard Shortcuts - System-wide hotkeys for DAIW

Allows triggering DAIW features even when app is not focused.
"""

from typing import Dict, Optional, Callable, List
from dataclasses import dataclass
from enum import Enum
import platform


class ShortcutContext(Enum):
    """Context where shortcut is active"""
    GLOBAL = "global"  # Active even when app not focused
    APPLICATION = "application"  # Active only in DAIW window
    MODE_SPECIFIC = "mode_specific"  # Active only in certain modes


@dataclass
class Shortcut:
    """Represents a keyboard shortcut"""
    id: str
    key_combination: str  # e.g., "Ctrl+K", "Cmd+Shift+P"
    description: str
    callback: Callable
    context: ShortcutContext = ShortcutContext.APPLICATION
    enabled: bool = True
    customizable: bool = True


class ShortcutManager:
    """
    Manages keyboard shortcuts for DAIW

    Features:
    - Global and application shortcuts
    - Customizable key bindings
    - Conflict detection
    - Platform-specific modifiers (Cmd on Mac, Ctrl on Win/Linux)
    - Shortcut profiles
    """

    def __init__(self):
        self.shortcuts: Dict[str, Shortcut] = {}
        self.key_map: Dict[str, str] = {}  # Maps key combo to shortcut ID

        # Platform detection
        self.platform = platform.system()
        self.is_mac = self.platform == "Darwin"

        # Initialize default shortcuts
        self._register_default_shortcuts()

    def _register_default_shortcuts(self) -> None:
        """Register default DAIW shortcuts"""

        # Use Cmd on Mac, Ctrl elsewhere
        mod = "Cmd" if self.is_mac else "Ctrl"

        # Command Palette
        self.register_shortcut(Shortcut(
            id="command_palette",
            key_combination=f"{mod}+K",
            description="Open Command Palette",
            callback=lambda: None,  # Will be set by main app
            context=ShortcutContext.APPLICATION
        ))

        # Mode switching
        self.register_shortcut(Shortcut(
            id="mode_idle",
            key_combination=f"{mod}+1",
            description="Switch to Idle Mode",
            callback=lambda: None,
            context=ShortcutContext.APPLICATION
        ))

        self.register_shortcut(Shortcut(
            id="mode_jam",
            key_combination=f"{mod}+2",
            description="Switch to Jam Mode",
            callback=lambda: None,
            context=ShortcutContext.APPLICATION
        ))

        self.register_shortcut(Shortcut(
            id="mode_learn",
            key_combination=f"{mod}+3",
            description="Switch to Learn Mode",
            callback=lambda: None,
            context=ShortcutContext.APPLICATION
        ))

        self.register_shortcut(Shortcut(
            id="mode_lock",
            key_combination=f"{mod}+4",
            description="Switch to Lock Mode",
            callback=lambda: None,
            context=ShortcutContext.APPLICATION
        ))

        # Audio features
        self.register_shortcut(Shortcut(
            id="youtube_analyzer",
            key_combination=f"{mod}+Y",
            description="Open YouTube Analyzer",
            callback=lambda: None,
            context=ShortcutContext.APPLICATION
        ))

        self.register_shortcut(Shortcut(
            id="stem_separator",
            key_combination=f"{mod}+Shift+S",
            description="Open STEM Separator",
            callback=lambda: None,
            context=ShortcutContext.APPLICATION
        ))

        self.register_shortcut(Shortcut(
            id="humming_recorder",
            key_combination=f"{mod}+H",
            description="Open Humming Recorder",
            callback=lambda: None,
            context=ShortcutContext.APPLICATION
        ))

        # Presets
        self.register_shortcut(Shortcut(
            id="save_preset",
            key_combination=f"{mod}+S",
            description="Save Preset",
            callback=lambda: None,
            context=ShortcutContext.APPLICATION
        ))

        self.register_shortcut(Shortcut(
            id="load_preset",
            key_combination=f"{mod}+O",
            description="Load Preset",
            callback=lambda: None,
            context=ShortcutContext.APPLICATION
        ))

        # Undo/Redo
        self.register_shortcut(Shortcut(
            id="undo",
            key_combination=f"{mod}+Z",
            description="Undo",
            callback=lambda: None,
            context=ShortcutContext.APPLICATION
        ))

        self.register_shortcut(Shortcut(
            id="redo",
            key_combination=f"{mod}+Shift+Z",
            description="Redo",
            callback=lambda: None,
            context=ShortcutContext.APPLICATION
        ))

        # View
        self.register_shortcut(Shortcut(
            id="toggle_mini_mode",
            key_combination=f"{mod}+M",
            description="Toggle Mini Mode",
            callback=lambda: None,
            context=ShortcutContext.APPLICATION
        ))

        self.register_shortcut(Shortcut(
            id="toggle_floating_menu",
            key_combination=f"{mod}+Space",
            description="Toggle Floating Menu",
            callback=lambda: None,
            context=ShortcutContext.APPLICATION
        ))

        # AI Assistant
        self.register_shortcut(Shortcut(
            id="ai_chat",
            key_combination=f"{mod}+/",
            description="Open AI Chat",
            callback=lambda: None,
            context=ShortcutContext.APPLICATION
        ))

        # System
        self.register_shortcut(Shortcut(
            id="settings",
            key_combination=f"{mod}+,",
            description="Open Settings",
            callback=lambda: None,
            context=ShortcutContext.APPLICATION
        ))

        self.register_shortcut(Shortcut(
            id="shortcuts_help",
            key_combination=f"{mod}+?",
            description="Show Keyboard Shortcuts",
            callback=lambda: None,
            context=ShortcutContext.APPLICATION
        ))

        # Quick actions
        self.register_shortcut(Shortcut(
            id="quick_record",
            key_combination=f"{mod}+R",
            description="Quick Record",
            callback=lambda: None,
            context=ShortcutContext.GLOBAL,
            customizable=True
        ))

        self.register_shortcut(Shortcut(
            id="quick_generate",
            key_combination=f"{mod}+G",
            description="Quick Generate (AI)",
            callback=lambda: None,
            context=ShortcutContext.APPLICATION
        ))

    def register_shortcut(self, shortcut: Shortcut) -> bool:
        """
        Register a new shortcut

        Args:
            shortcut: Shortcut to register

        Returns:
            True if registered successfully
        """
        # Check for conflicts
        if shortcut.key_combination in self.key_map:
            existing_id = self.key_map[shortcut.key_combination]
            existing = self.shortcuts[existing_id]

            # Don't allow conflicts unless explicitly overriding
            if existing.context == shortcut.context:
                print(f"[ShortcutManager] Conflict: {shortcut.key_combination} already assigned to {existing_id}")
                return False

        # Register shortcut
        self.shortcuts[shortcut.id] = shortcut
        self.key_map[shortcut.key_combination] = shortcut.id

        return True

    def unregister_shortcut(self, shortcut_id: str) -> bool:
        """Unregister a shortcut"""
        shortcut = self.shortcuts.get(shortcut_id)
        if not shortcut:
            return False

        # Remove from key map
        if shortcut.key_combination in self.key_map:
            del self.key_map[shortcut.key_combination]

        # Remove from shortcuts
        del self.shortcuts[shortcut_id]

        return True

    def get_shortcut(self, shortcut_id: str) -> Optional[Shortcut]:
        """Get shortcut by ID"""
        return self.shortcuts.get(shortcut_id)

    def get_shortcut_by_keys(self, key_combination: str) -> Optional[Shortcut]:
        """Get shortcut by key combination"""
        shortcut_id = self.key_map.get(key_combination)
        if shortcut_id:
            return self.shortcuts.get(shortcut_id)
        return None

    def execute_shortcut(self, shortcut_id: str) -> bool:
        """
        Execute a shortcut by ID

        Args:
            shortcut_id: Shortcut identifier

        Returns:
            True if executed successfully
        """
        shortcut = self.get_shortcut(shortcut_id)
        if not shortcut or not shortcut.enabled:
            return False

        try:
            shortcut.callback()
            return True
        except Exception as e:
            print(f"[ShortcutManager] Error executing shortcut {shortcut_id}: {e}")
            return False

    def execute_keys(self, key_combination: str) -> bool:
        """
        Execute shortcut by key combination

        Args:
            key_combination: Key combination (e.g., "Ctrl+K")

        Returns:
            True if executed successfully
        """
        shortcut = self.get_shortcut_by_keys(key_combination)
        if shortcut:
            return self.execute_shortcut(shortcut.id)
        return False

    def set_callback(self, shortcut_id: str, callback: Callable) -> bool:
        """
        Set callback for a shortcut

        Args:
            shortcut_id: Shortcut identifier
            callback: Function to call

        Returns:
            True if successful
        """
        shortcut = self.get_shortcut(shortcut_id)
        if not shortcut:
            return False

        shortcut.callback = callback
        return True

    def customize_shortcut(self, shortcut_id: str, new_keys: str) -> bool:
        """
        Customize key binding for a shortcut

        Args:
            shortcut_id: Shortcut to customize
            new_keys: New key combination

        Returns:
            True if successful
        """
        shortcut = self.get_shortcut(shortcut_id)
        if not shortcut or not shortcut.customizable:
            return False

        # Check for conflicts
        if new_keys in self.key_map and self.key_map[new_keys] != shortcut_id:
            print(f"[ShortcutManager] Cannot customize: {new_keys} already in use")
            return False

        # Remove old mapping
        if shortcut.key_combination in self.key_map:
            del self.key_map[shortcut.key_combination]

        # Update shortcut
        shortcut.key_combination = new_keys
        self.key_map[new_keys] = shortcut_id

        return True

    def enable_shortcut(self, shortcut_id: str) -> bool:
        """Enable a shortcut"""
        shortcut = self.get_shortcut(shortcut_id)
        if not shortcut:
            return False
        shortcut.enabled = True
        return True

    def disable_shortcut(self, shortcut_id: str) -> bool:
        """Disable a shortcut"""
        shortcut = self.get_shortcut(shortcut_id)
        if not shortcut:
            return False
        shortcut.enabled = False
        return True

    def get_shortcuts_by_context(self, context: ShortcutContext) -> List[Shortcut]:
        """Get all shortcuts for a specific context"""
        return [
            shortcut for shortcut in self.shortcuts.values()
            if shortcut.context == context
        ]

    def get_all_shortcuts(self) -> List[Shortcut]:
        """Get all registered shortcuts"""
        return list(self.shortcuts.values())

    def get_shortcuts_list(self) -> List[Dict[str, str]]:
        """
        Get shortcuts as a list of dictionaries for display

        Returns:
            List of shortcut info dicts
        """
        shortcuts = []
        for shortcut in sorted(self.shortcuts.values(), key=lambda s: s.description):
            shortcuts.append({
                "id": shortcut.id,
                "keys": shortcut.key_combination,
                "description": shortcut.description,
                "context": shortcut.context.value,
                "enabled": shortcut.enabled,
                "customizable": shortcut.customizable
            })
        return shortcuts

    def reset_to_defaults(self) -> None:
        """Reset all shortcuts to default bindings"""
        self.shortcuts.clear()
        self.key_map.clear()
        self._register_default_shortcuts()

    def export_shortcuts(self) -> Dict[str, str]:
        """
        Export shortcut customizations

        Returns:
            Dict mapping shortcut IDs to key combinations
        """
        return {
            shortcut_id: shortcut.key_combination
            for shortcut_id, shortcut in self.shortcuts.items()
        }

    def import_shortcuts(self, shortcuts_dict: Dict[str, str]) -> int:
        """
        Import shortcut customizations

        Args:
            shortcuts_dict: Dict mapping shortcut IDs to key combinations

        Returns:
            Number of shortcuts successfully imported
        """
        count = 0
        for shortcut_id, key_combination in shortcuts_dict.items():
            if self.customize_shortcut(shortcut_id, key_combination):
                count += 1
        return count

    def format_key_combination(self, key_combination: str) -> str:
        """
        Format key combination for display (platform-specific)

        Args:
            key_combination: Raw key combination

        Returns:
            Formatted string (e.g., "⌘K" on Mac, "Ctrl+K" elsewhere)
        """
        if self.is_mac:
            # Replace modifiers with Mac symbols
            formatted = key_combination
            formatted = formatted.replace("Cmd", "⌘")
            formatted = formatted.replace("Ctrl", "⌃")
            formatted = formatted.replace("Alt", "⌥")
            formatted = formatted.replace("Shift", "⇧")
            formatted = formatted.replace("+", "")
            return formatted
        else:
            return key_combination

    def parse_key_event(self, event) -> Optional[str]:
        """
        Parse Qt key event to key combination string

        Args:
            event: QKeyEvent

        Returns:
            Key combination string (e.g., "Ctrl+K")
        """
        from PyQt6.QtCore import Qt

        modifiers = []
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            modifiers.append("Ctrl")
        if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            modifiers.append("Shift")
        if event.modifiers() & Qt.KeyboardModifier.AltModifier:
            modifiers.append("Alt")
        if event.modifiers() & Qt.KeyboardModifier.MetaModifier:
            modifiers.append("Cmd" if self.is_mac else "Meta")

        # Get key name
        key = event.key()
        key_name = None

        # Handle special keys
        if key == Qt.Key.Key_Space:
            key_name = "Space"
        elif key == Qt.Key.Key_Return or key == Qt.Key.Key_Enter:
            key_name = "Enter"
        elif key == Qt.Key.Key_Escape:
            key_name = "Esc"
        elif key == Qt.Key.Key_Tab:
            key_name = "Tab"
        elif key == Qt.Key.Key_Backspace:
            key_name = "Backspace"
        elif key >= Qt.Key.Key_F1 and key <= Qt.Key.Key_F12:
            key_name = f"F{key - Qt.Key.Key_F1 + 1}"
        else:
            # Regular character
            key_name = event.text().upper()

        if not key_name or not modifiers:
            return None

        return "+".join(modifiers + [key_name])
