"""
Drag & Drop Handler - Universal file drop handling for DAIW

Supports dragging audio files, YouTube URLs, images, PDFs, and more onto the avatar.
"""

from typing import List, Optional, Callable, Dict, Any
from pathlib import Path
from enum import Enum
import mimetypes
import re


class DropType(Enum):
    """Types of dropped content"""
    AUDIO_FILE = "audio_file"
    VIDEO_FILE = "video_file"
    IMAGE_FILE = "image_file"
    PDF_FILE = "pdf_file"
    TEXT_FILE = "text_file"
    URL = "url"
    YOUTUBE_URL = "youtube_url"
    MIDI_FILE = "midi_file"
    PROJECT_FILE = "project_file"
    UNKNOWN = "unknown"


class DroppedItem:
    """Represents a dropped item"""

    def __init__(self, content: str, drop_type: DropType):
        self.content = content
        self.drop_type = drop_type
        self.metadata: Dict[str, Any] = {}

    def is_file(self) -> bool:
        """Check if item is a file"""
        return self.drop_type not in [DropType.URL, DropType.YOUTUBE_URL]

    def get_path(self) -> Optional[Path]:
        """Get file path if item is a file"""
        if self.is_file():
            return Path(self.content)
        return None

    def get_url(self) -> Optional[str]:
        """Get URL if item is a URL"""
        if not self.is_file():
            return self.content
        return None


class DragDropHandler:
    """
    Handles drag & drop operations for DAIW

    Features:
    - Auto-detect dropped content type
    - Route to appropriate handler
    - Support multiple files
    - Clipboard paste detection
    - Smart suggestions based on content
    """

    def __init__(self):
        # Content type handlers
        self.handlers: Dict[DropType, List[Callable]] = {
            drop_type: [] for drop_type in DropType
        }

        # Supported audio formats
        self.audio_formats = {
            '.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a',
            '.wma', '.aiff', '.aif', '.opus'
        }

        # Supported video formats
        self.video_formats = {
            '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv',
            '.webm', '.m4v', '.mpeg', '.mpg'
        }

        # Supported image formats
        self.image_formats = {
            '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg',
            '.webp', '.tiff', '.ico'
        }

        # Supported text formats
        self.text_formats = {
            '.txt', '.md', '.json', '.xml', '.html', '.css',
            '.js', '.py', '.java', '.cpp', '.c', '.h'
        }

        # MIDI formats
        self.midi_formats = {'.mid', '.midi'}

        # Project formats
        self.project_formats = {'.als', '.flp', '.logic', '.ptx'}

    def register_handler(self, drop_type: DropType, handler: Callable) -> None:
        """
        Register a handler for a drop type

        Args:
            drop_type: Type of dropped content
            handler: Function to handle the drop (receives DroppedItem)
        """
        if handler not in self.handlers[drop_type]:
            self.handlers[drop_type].append(handler)

    def unregister_handler(self, drop_type: DropType, handler: Callable) -> None:
        """Unregister a handler"""
        if handler in self.handlers[drop_type]:
            self.handlers[drop_type].remove(handler)

    def detect_type(self, content: str) -> DropType:
        """
        Detect the type of dropped content

        Args:
            content: File path or URL

        Returns:
            Detected drop type
        """
        # Check if it's a URL
        if self._is_url(content):
            if self._is_youtube_url(content):
                return DropType.YOUTUBE_URL
            return DropType.URL

        # Check if it's a file
        path = Path(content)
        if not path.exists():
            return DropType.UNKNOWN

        suffix = path.suffix.lower()

        # Check file extension
        if suffix in self.audio_formats:
            return DropType.AUDIO_FILE
        elif suffix in self.video_formats:
            return DropType.VIDEO_FILE
        elif suffix in self.image_formats:
            return DropType.IMAGE_FILE
        elif suffix == '.pdf':
            return DropType.PDF_FILE
        elif suffix in self.text_formats:
            return DropType.TEXT_FILE
        elif suffix in self.midi_formats:
            return DropType.MIDI_FILE
        elif suffix in self.project_formats:
            return DropType.PROJECT_FILE

        # Try MIME type detection
        mime_type, _ = mimetypes.guess_type(content)
        if mime_type:
            if mime_type.startswith('audio/'):
                return DropType.AUDIO_FILE
            elif mime_type.startswith('video/'):
                return DropType.VIDEO_FILE
            elif mime_type.startswith('image/'):
                return DropType.IMAGE_FILE
            elif mime_type == 'application/pdf':
                return DropType.PDF_FILE
            elif mime_type.startswith('text/'):
                return DropType.TEXT_FILE

        return DropType.UNKNOWN

    def _is_url(self, content: str) -> bool:
        """Check if content is a URL"""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or IP
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return bool(url_pattern.match(content))

    def _is_youtube_url(self, content: str) -> bool:
        """Check if URL is a YouTube URL"""
        youtube_patterns = [
            r'youtube\.com/watch\?v=',
            r'youtube\.com/embed/',
            r'youtu\.be/',
            r'youtube\.com/v/',
            r'youtube\.com/shorts/'
        ]
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in youtube_patterns)

    def handle_drop(self, content: str) -> bool:
        """
        Handle a single dropped item

        Args:
            content: File path or URL

        Returns:
            True if handled successfully
        """
        drop_type = self.detect_type(content)
        item = DroppedItem(content, drop_type)

        # Add metadata
        if item.is_file():
            path = item.get_path()
            if path:
                item.metadata['filename'] = path.name
                item.metadata['size'] = path.stat().st_size
                item.metadata['extension'] = path.suffix

        # Execute handlers
        handlers = self.handlers.get(drop_type, [])
        if not handlers:
            print(f"[DragDrop] No handler for type: {drop_type.value}")
            return False

        success = False
        for handler in handlers:
            try:
                handler(item)
                success = True
            except Exception as e:
                print(f"[DragDrop] Handler error: {e}")

        return success

    def handle_multiple_drops(self, items: List[str]) -> Dict[DropType, List[str]]:
        """
        Handle multiple dropped items

        Args:
            items: List of file paths or URLs

        Returns:
            Dict grouping items by type
        """
        grouped: Dict[DropType, List[str]] = {}

        for item in items:
            drop_type = self.detect_type(item)
            if drop_type not in grouped:
                grouped[drop_type] = []
            grouped[drop_type].append(item)

        # Process each group
        for drop_type, group_items in grouped.items():
            print(f"[DragDrop] Processing {len(group_items)} items of type {drop_type.value}")
            for item in group_items:
                self.handle_drop(item)

        return grouped

    def get_drop_action_name(self, drop_type: DropType) -> str:
        """
        Get human-readable action name for drop type

        Args:
            drop_type: Type of drop

        Returns:
            Action description
        """
        actions = {
            DropType.AUDIO_FILE: "Analyze Audio",
            DropType.VIDEO_FILE: "Extract Audio",
            DropType.IMAGE_FILE: "Analyze Image",
            DropType.PDF_FILE: "Read PDF",
            DropType.TEXT_FILE: "Read Text",
            DropType.URL: "Fetch URL",
            DropType.YOUTUBE_URL: "Analyze YouTube",
            DropType.MIDI_FILE: "Load MIDI",
            DropType.PROJECT_FILE: "Open Project",
            DropType.UNKNOWN: "Unknown"
        }
        return actions.get(drop_type, "Process")

    def get_suggested_actions(self, drop_type: DropType) -> List[str]:
        """
        Get suggested actions for dropped content

        Args:
            drop_type: Type of dropped content

        Returns:
            List of suggested action descriptions
        """
        suggestions = {
            DropType.AUDIO_FILE: [
                "Analyze tempo and key",
                "Separate into stems",
                "Extract melody",
                "Generate harmonies",
                "Create similar style"
            ],
            DropType.VIDEO_FILE: [
                "Extract audio track",
                "Analyze soundtrack",
                "Separate audio stems"
            ],
            DropType.IMAGE_FILE: [
                "Analyze with AI",
                "Extract text (OCR)",
                "Generate description",
                "Use as inspiration"
            ],
            DropType.PDF_FILE: [
                "Read and summarize",
                "Extract key points",
                "Answer questions about content",
                "Convert to audio (TTS)"
            ],
            DropType.TEXT_FILE: [
                "Read content",
                "Analyze and summarize",
                "Extract information",
                "Generate based on content"
            ],
            DropType.YOUTUBE_URL: [
                "Analyze music",
                "Download audio",
                "Separate stems",
                "Learn style"
            ],
            DropType.MIDI_FILE: [
                "Load as reference",
                "Analyze patterns",
                "Generate variations",
                "Harmonize"
            ],
            DropType.PROJECT_FILE: [
                "Open in DAW",
                "Analyze structure",
                "Extract MIDI"
            ]
        }
        return suggestions.get(drop_type, ["Process file"])

    def is_supported(self, content: str) -> bool:
        """Check if content type is supported"""
        drop_type = self.detect_type(content)
        return drop_type != DropType.UNKNOWN

    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get detailed information about a file

        Args:
            file_path: Path to file

        Returns:
            File information dict
        """
        path = Path(file_path)
        if not path.exists():
            return {}

        info = {
            "name": path.name,
            "stem": path.stem,
            "extension": path.suffix,
            "size": path.stat().st_size,
            "size_mb": path.stat().st_size / (1024 * 1024),
            "modified": path.stat().st_mtime,
            "type": self.detect_type(file_path).value
        }

        # Audio-specific info
        if info["type"] == "audio_file":
            try:
                import librosa
                duration = librosa.get_duration(path=str(path))
                info["duration_seconds"] = duration
                info["duration_formatted"] = self._format_duration(duration)
            except:
                pass

        return info

    def _format_duration(self, seconds: float) -> str:
        """Format duration in human-readable form"""
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins}:{secs:02d}"

    def create_drop_message(self, item: DroppedItem) -> str:
        """
        Create a user-friendly message about dropped item

        Args:
            item: Dropped item

        Returns:
            Message string
        """
        action = self.get_drop_action_name(item.drop_type)

        if item.is_file():
            filename = item.metadata.get('filename', 'file')
            return f"Ready to {action}: {filename}"
        else:
            return f"Ready to {action}"

    def validate_drop(self, content: str) -> tuple[bool, str]:
        """
        Validate dropped content

        Args:
            content: File path or URL

        Returns:
            Tuple of (valid, error_message)
        """
        drop_type = self.detect_type(content)

        if drop_type == DropType.UNKNOWN:
            return False, "Unsupported file type"

        if self._is_url(content):
            return True, ""

        # Check if file exists
        path = Path(content)
        if not path.exists():
            return False, "File not found"

        if not path.is_file():
            return False, "Not a file (may be a directory)"

        # Check file size (warn if > 100MB)
        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > 100:
            return True, f"Warning: Large file ({size_mb:.1f}MB)"

        return True, ""
