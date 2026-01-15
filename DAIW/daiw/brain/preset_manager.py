"""
Preset Manager - Save and load configurations, templates, and workflows

Allows users to save favorite settings and quickly switch between different
production setups.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import json
from enum import Enum


class PresetType(Enum):
    """Types of presets"""
    WORKSPACE = "workspace"  # Full workspace config
    MODE_CONFIG = "mode_config"  # Mode-specific settings
    AI_PROMPT = "ai_prompt"  # AI prompt templates
    AUDIO_SETTINGS = "audio_settings"  # Audio/MIDI config
    VISUAL_THEME = "visual_theme"  # UI appearance
    SESSION_TEMPLATE = "session_template"  # Pre-configured session
    WORKFLOW = "workflow"  # Multi-step workflow


@dataclass
class Preset:
    """Represents a saved preset"""
    id: str
    name: str
    description: str
    preset_type: PresetType
    data: Dict[str, Any]
    tags: List[str]
    created_at: datetime
    modified_at: datetime
    author: str = "user"
    favorite: bool = False
    thumbnail: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "preset_type": self.preset_type.value,
            "data": self.data,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "modified_at": self.modified_at.isoformat(),
            "author": self.author,
            "favorite": self.favorite,
            "thumbnail": self.thumbnail
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Preset':
        """Create from dictionary"""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            preset_type=PresetType(data["preset_type"]),
            data=data["data"],
            tags=data["tags"],
            created_at=datetime.fromisoformat(data["created_at"]),
            modified_at=datetime.fromisoformat(data["modified_at"]),
            author=data.get("author", "user"),
            favorite=data.get("favorite", False),
            thumbnail=data.get("thumbnail")
        )


class PresetManager:
    """
    Manages presets for DAIW

    Features:
    - Save/load presets
    - Organize by type and tags
    - Search presets
    - Import/export presets
    - Preset templates
    - Auto-save current state
    """

    def __init__(self, presets_dir: Optional[Path] = None):
        """
        Initialize preset manager

        Args:
            presets_dir: Directory to store presets (default: ~/.daiw/presets)
        """
        if presets_dir is None:
            presets_dir = Path.home() / ".daiw" / "presets"

        self.presets_dir = presets_dir
        self.presets_dir.mkdir(parents=True, exist_ok=True)

        # In-memory preset storage
        self.presets: Dict[str, Preset] = {}

        # Current state for auto-save
        self.current_state: Dict[str, Any] = {}

        # Load all presets
        self._load_all_presets()

        # Initialize built-in presets
        self._create_builtin_presets()

    def _load_all_presets(self) -> None:
        """Load all presets from disk"""
        for preset_file in self.presets_dir.glob("*.json"):
            try:
                with open(preset_file, 'r') as f:
                    data = json.load(f)
                    preset = Preset.from_dict(data)
                    self.presets[preset.id] = preset
            except Exception as e:
                print(f"[PresetManager] Error loading preset {preset_file}: {e}")

    def _create_builtin_presets(self) -> None:
        """Create built-in preset templates"""

        # Only create if they don't exist
        if not self.get_preset("builtin.jam_session"):
            self.save_preset(
                name="Jam Session",
                description="Ready for improvisation with AI co-pilot",
                preset_type=PresetType.SESSION_TEMPLATE,
                data={
                    "mode": "jam",
                    "ai_config": {
                        "temperature": 0.9,
                        "style": "experimental"
                    },
                    "midi_config": {
                        "velocity_range": [80, 120],
                        "note_length": "medium"
                    }
                },
                tags=["jam", "improvise", "creative"],
                preset_id="builtin.jam_session"
            )

        if not self.get_preset("builtin.learning"):
            self.save_preset(
                name="Learning Mode",
                description="Optimized for learning your style",
                preset_type=PresetType.SESSION_TEMPLATE,
                data={
                    "mode": "learn",
                    "ai_config": {
                        "observation_depth": "detailed",
                        "pattern_sensitivity": "high"
                    }
                },
                tags=["learn", "analyze", "observe"],
                preset_id="builtin.learning"
            )

        if not self.get_preset("builtin.production"):
            self.save_preset(
                name="Production Mode",
                description="Full-featured music production setup",
                preset_type=PresetType.SESSION_TEMPLATE,
                data={
                    "mode": "idle",
                    "features": {
                        "youtube_analyzer": True,
                        "stem_separator": True,
                        "humming_recorder": True
                    },
                    "view": {
                        "status_bar": True,
                        "floating_menu": True
                    }
                },
                tags=["production", "full-featured"],
                preset_id="builtin.production"
            )

        if not self.get_preset("builtin.minimal"):
            self.save_preset(
                name="Minimal Setup",
                description="Clean, distraction-free workspace",
                preset_type=PresetType.SESSION_TEMPLATE,
                data={
                    "mode": "idle",
                    "view": {
                        "mini_mode": True,
                        "status_bar": False,
                        "floating_menu": False
                    }
                },
                tags=["minimal", "clean", "focus"],
                preset_id="builtin.minimal"
            )

        if not self.get_preset("builtin.collaboration"):
            self.save_preset(
                name="Collaboration Session",
                description="Ready for CollabNet real-time collaboration",
                preset_type=PresetType.SESSION_TEMPLATE,
                data={
                    "collabnet": {
                        "enabled": True,
                        "auto_sync": True,
                        "show_avatars": True
                    },
                    "features": {
                        "chat": True,
                        "screen_share": False
                    }
                },
                tags=["collaboration", "collabnet", "multi-user"],
                preset_id="builtin.collaboration"
            )

    def save_preset(
        self,
        name: str,
        description: str,
        preset_type: PresetType,
        data: Dict[str, Any],
        tags: Optional[List[str]] = None,
        preset_id: Optional[str] = None,
        author: str = "user"
    ) -> Preset:
        """
        Save a new preset

        Args:
            name: Preset name
            description: Description
            preset_type: Type of preset
            data: Preset data
            tags: Optional tags
            preset_id: Optional custom ID (auto-generated if not provided)
            author: Preset author

        Returns:
            Created preset
        """
        if preset_id is None:
            # Generate ID from name
            preset_id = self._generate_preset_id(name)

        now = datetime.now()

        # Create or update preset
        if preset_id in self.presets:
            # Update existing
            preset = self.presets[preset_id]
            preset.name = name
            preset.description = description
            preset.preset_type = preset_type
            preset.data = data
            preset.tags = tags or []
            preset.modified_at = now
        else:
            # Create new
            preset = Preset(
                id=preset_id,
                name=name,
                description=description,
                preset_type=preset_type,
                data=data,
                tags=tags or [],
                created_at=now,
                modified_at=now,
                author=author
            )
            self.presets[preset_id] = preset

        # Save to disk
        self._save_preset_to_disk(preset)

        return preset

    def _generate_preset_id(self, name: str) -> str:
        """Generate unique preset ID from name"""
        import re
        # Convert to lowercase and replace spaces/special chars with underscores
        base_id = re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')

        # Ensure uniqueness
        preset_id = base_id
        counter = 1
        while preset_id in self.presets:
            preset_id = f"{base_id}_{counter}"
            counter += 1

        return preset_id

    def _save_preset_to_disk(self, preset: Preset) -> None:
        """Save preset to disk"""
        preset_file = self.presets_dir / f"{preset.id}.json"
        try:
            with open(preset_file, 'w') as f:
                json.dump(preset.to_dict(), f, indent=2)
        except Exception as e:
            print(f"[PresetManager] Error saving preset {preset.id}: {e}")

    def load_preset(self, preset_id: str) -> Optional[Preset]:
        """
        Load a preset by ID

        Args:
            preset_id: Preset identifier

        Returns:
            Preset if found
        """
        return self.presets.get(preset_id)

    def get_preset(self, preset_id: str) -> Optional[Preset]:
        """Alias for load_preset"""
        return self.load_preset(preset_id)

    def delete_preset(self, preset_id: str) -> bool:
        """
        Delete a preset

        Args:
            preset_id: Preset identifier

        Returns:
            True if deleted
        """
        if preset_id not in self.presets:
            return False

        # Don't allow deleting built-in presets
        if preset_id.startswith("builtin."):
            print(f"[PresetManager] Cannot delete built-in preset: {preset_id}")
            return False

        # Remove from memory
        del self.presets[preset_id]

        # Remove from disk
        preset_file = self.presets_dir / f"{preset_id}.json"
        if preset_file.exists():
            preset_file.unlink()

        return True

    def list_presets(
        self,
        preset_type: Optional[PresetType] = None,
        tags: Optional[List[str]] = None,
        favorites_only: bool = False
    ) -> List[Preset]:
        """
        List presets with optional filters

        Args:
            preset_type: Filter by type
            tags: Filter by tags (any match)
            favorites_only: Only show favorites

        Returns:
            List of matching presets
        """
        results = []

        for preset in self.presets.values():
            # Type filter
            if preset_type and preset.preset_type != preset_type:
                continue

            # Tags filter
            if tags and not any(tag in preset.tags for tag in tags):
                continue

            # Favorites filter
            if favorites_only and not preset.favorite:
                continue

            results.append(preset)

        # Sort by modified date (most recent first)
        results.sort(key=lambda p: p.modified_at, reverse=True)

        return results

    def search_presets(self, query: str) -> List[Preset]:
        """
        Search presets by name, description, or tags

        Args:
            query: Search query

        Returns:
            List of matching presets
        """
        query = query.lower()
        results = []

        for preset in self.presets.values():
            # Search in name
            if query in preset.name.lower():
                results.append(preset)
                continue

            # Search in description
            if query in preset.description.lower():
                results.append(preset)
                continue

            # Search in tags
            if any(query in tag.lower() for tag in preset.tags):
                results.append(preset)
                continue

        return results

    def toggle_favorite(self, preset_id: str) -> bool:
        """
        Toggle preset favorite status

        Args:
            preset_id: Preset identifier

        Returns:
            New favorite status
        """
        preset = self.get_preset(preset_id)
        if not preset:
            return False

        preset.favorite = not preset.favorite
        preset.modified_at = datetime.now()
        self._save_preset_to_disk(preset)

        return preset.favorite

    def add_tag(self, preset_id: str, tag: str) -> bool:
        """Add tag to preset"""
        preset = self.get_preset(preset_id)
        if not preset:
            return False

        if tag not in preset.tags:
            preset.tags.append(tag)
            preset.modified_at = datetime.now()
            self._save_preset_to_disk(preset)

        return True

    def remove_tag(self, preset_id: str, tag: str) -> bool:
        """Remove tag from preset"""
        preset = self.get_preset(preset_id)
        if not preset:
            return False

        if tag in preset.tags:
            preset.tags.remove(tag)
            preset.modified_at = datetime.now()
            self._save_preset_to_disk(preset)

        return True

    def export_preset(self, preset_id: str, export_path: Path) -> bool:
        """
        Export preset to file

        Args:
            preset_id: Preset to export
            export_path: Destination file path

        Returns:
            True if successful
        """
        preset = self.get_preset(preset_id)
        if not preset:
            return False

        try:
            with open(export_path, 'w') as f:
                json.dump(preset.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"[PresetManager] Error exporting preset: {e}")
            return False

    def import_preset(self, import_path: Path) -> Optional[Preset]:
        """
        Import preset from file

        Args:
            import_path: Source file path

        Returns:
            Imported preset
        """
        try:
            with open(import_path, 'r') as f:
                data = json.load(f)
                preset = Preset.from_dict(data)

                # Ensure unique ID
                if preset.id in self.presets:
                    preset.id = self._generate_preset_id(preset.name)

                self.presets[preset.id] = preset
                self._save_preset_to_disk(preset)

                return preset
        except Exception as e:
            print(f"[PresetManager] Error importing preset: {e}")
            return None

    def duplicate_preset(self, preset_id: str, new_name: Optional[str] = None) -> Optional[Preset]:
        """
        Duplicate an existing preset

        Args:
            preset_id: Preset to duplicate
            new_name: Name for duplicate (auto-generated if not provided)

        Returns:
            Duplicated preset
        """
        original = self.get_preset(preset_id)
        if not original:
            return None

        if new_name is None:
            new_name = f"{original.name} (Copy)"

        return self.save_preset(
            name=new_name,
            description=original.description,
            preset_type=original.preset_type,
            data=original.data.copy(),
            tags=original.tags.copy(),
            author=original.author
        )

    def get_all_tags(self) -> List[str]:
        """Get all unique tags used in presets"""
        tags = set()
        for preset in self.presets.values():
            tags.update(preset.tags)
        return sorted(list(tags))

    def get_preset_types(self) -> List[PresetType]:
        """Get all preset types that have presets"""
        types = set()
        for preset in self.presets.values():
            types.add(preset.preset_type)
        return sorted(list(types), key=lambda t: t.value)
