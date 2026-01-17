"""
Transparent Window - Always-on-top, frameless, click-through window

Das Fenster ist transparent, rahmenlos und ermöglicht click-through
(außer auf den Avatar selbst).
"""

from typing import Optional
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QMenu
)
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtGui import QAction, QMouseEvent, QCursor

from daiw.gui.bass_clef_widget import BassClefWidget, AvatarState


class TransparentAvatarWindow(QMainWindow):
    """
    Main window for the avatar - transparent and always on top
    """

    # Signals
    mode_changed = pyqtSignal(str)  # "jam", "learn", "lock"
    exit_requested = pyqtSignal()

    # Interactive feature signals
    youtube_analyze_requested = pyqtSignal()
    stem_separate_requested = pyqtSignal()
    humming_record_requested = pyqtSignal()
    interactive_features_requested = pyqtSignal()

    def __init__(self):
        super().__init__()

        # Current mode
        self._current_mode = "idle"

        # Window flags for transparency and always on top
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )

        # Make window transparent
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)

        # Window properties
        self.setWindowTitle("Music Copilot Avatar")
        self.setGeometry(100, 100, 250, 200)

        # Central widget
        central_widget = QWidget()
        central_widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCentralWidget(central_widget)

        # Layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Avatar widget
        self.avatar = BassClefWidget()
        layout.addWidget(self.avatar)

        # Dragging state
        self._dragging = False
        self._drag_position = QPoint()

        # Create context menu
        self._create_context_menu()

    def _create_context_menu(self) -> None:
        """Create the context menu for mode switching"""
        self.context_menu = QMenu(self)

        # Mode actions
        self.jam_action = QAction("🎸 Freestyle Jam", self)
        self.jam_action.triggered.connect(lambda: self._switch_mode("jam"))

        self.learn_action = QAction("👁️ Learn by Watching", self)
        self.learn_action.triggered.connect(lambda: self._switch_mode("learn"))

        self.lock_action = QAction("🔒 Lock Mode (Meta-Programming)", self)
        self.lock_action.triggered.connect(lambda: self._switch_mode("lock"))

        self.idle_action = QAction("💤 Idle", self)
        self.idle_action.triggered.connect(lambda: self._switch_mode("idle"))

        # Separator
        separator1 = self.context_menu.addSeparator()

        # Add actions to menu
        self.context_menu.addAction(self.jam_action)
        self.context_menu.addAction(self.learn_action)
        self.context_menu.addAction(self.lock_action)
        self.context_menu.addAction(self.idle_action)

        # Interactive Features
        self.context_menu.addSeparator()

        self.features_action = QAction("✨ Interactive Features...", self)
        self.features_action.triggered.connect(lambda: self.interactive_features_requested.emit())
        self.context_menu.addAction(self.features_action)

        # Quick access to features
        self.youtube_action = QAction("🎥 Analyze YouTube Song", self)
        self.youtube_action.triggered.connect(lambda: self.youtube_analyze_requested.emit())
        self.context_menu.addAction(self.youtube_action)

        self.stem_action = QAction("✂️ Separate STEM", self)
        self.stem_action.triggered.connect(lambda: self.stem_separate_requested.emit())
        self.context_menu.addAction(self.stem_action)

        self.humming_action = QAction("🎤 Hum → MIDI", self)
        self.humming_action.triggered.connect(lambda: self.humming_record_requested.emit())
        self.context_menu.addAction(self.humming_action)

        # Settings
        self.context_menu.addSeparator()

        self.settings_action = QAction("⚙️ Settings", self)
        self.settings_action.triggered.connect(self._show_settings)
        self.context_menu.addAction(self.settings_action)

        # Exit
        self.context_menu.addSeparator()

        self.exit_action = QAction("❌ Exit", self)
        self.exit_action.triggered.connect(self._request_exit)
        self.context_menu.addAction(self.exit_action)

    def _switch_mode(self, mode: str) -> None:
        """Switch to a different mode"""
        self._current_mode = mode

        # Update avatar state
        state_map = {
            "idle": AvatarState.IDLE,
            "jam": AvatarState.JAMMING,
            "learn": AvatarState.LEARNING,
            "lock": AvatarState.LOCKED,
        }

        if mode in state_map:
            self.avatar.set_state(state_map[mode])

        # Emit signal
        self.mode_changed.emit(mode)

        # Update menu checkmarks
        self._update_menu_checkmarks()

    def _update_menu_checkmarks(self) -> None:
        """Update checkmarks in context menu"""
        # Clear all checkmarks
        self.jam_action.setCheckable(True)
        self.learn_action.setCheckable(True)
        self.lock_action.setCheckable(True)
        self.idle_action.setCheckable(True)

        # Set checkmark for current mode
        if self._current_mode == "jam":
            self.jam_action.setChecked(True)
        elif self._current_mode == "learn":
            self.learn_action.setChecked(True)
        elif self._current_mode == "lock":
            self.lock_action.setChecked(True)
        else:
            self.idle_action.setChecked(True)

    def _show_settings(self) -> None:
        """Show settings dialog (placeholder)"""
        # TODO: Implement settings dialog
        print("Settings dialog - TODO")

    def _request_exit(self) -> None:
        """Request to exit the application"""
        self.exit_requested.emit()
        self.close()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press for dragging and context menu"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Start dragging
            self._dragging = True
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

        elif event.button() == Qt.MouseButton.RightButton:
            # Show context menu
            self.context_menu.exec(QCursor.pos())
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Handle mouse move for dragging"""
        if self._dragging and event.buttons() == Qt.MouseButton.LeftButton:
            # Move window
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Handle mouse release to stop dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False
            event.accept()

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        """Handle double click to cycle through modes"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Cycle through modes
            modes = ["idle", "jam", "learn", "lock"]
            current_index = modes.index(self._current_mode)
            next_mode = modes[(current_index + 1) % len(modes)]
            self._switch_mode(next_mode)
            event.accept()

    def set_thinking_state(self, thinking: bool) -> None:
        """Set the avatar to thinking state"""
        if thinking:
            self.avatar.set_state(AvatarState.THINKING)
        else:
            # Restore state based on current mode
            self._switch_mode(self._current_mode)

    def get_current_mode(self) -> str:
        """Get the current mode"""
        return self._current_mode
