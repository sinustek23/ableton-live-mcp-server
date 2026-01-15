"""
System Tray Icon - Quick access to DAIW from anywhere

Provides system tray icon with menu for quick access to features.
"""

from typing import Optional
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction, QPixmap, QPainter, QColor
from PyQt6.QtCore import pyqtSignal, QObject, Qt


class SystemTrayManager(QObject):
    """
    Manages system tray icon and menu

    Features:
    - Always-visible system tray icon
    - Quick access menu
    - Notifications
    - Status indicators
    - Global access to main features
    """

    # Signals
    show_window_requested = pyqtSignal()
    hide_window_requested = pyqtSignal()
    mode_change_requested = pyqtSignal(str)
    feature_requested = pyqtSignal(str)
    exit_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.tray_icon: Optional[QSystemTrayIcon] = None
        self.menu: Optional[QMenu] = None
        self.current_mode = "idle"

        # Initialize tray icon
        self._create_tray_icon()
        self._create_menu()

    def _create_tray_icon(self) -> None:
        """Create the system tray icon"""
        # Create icon (bass clef symbol)
        icon = self._create_bass_clef_icon()

        self.tray_icon = QSystemTrayIcon(icon, self.parent())
        self.tray_icon.setToolTip("DAIW - Digital AI Workspace")

        # Connect signals
        self.tray_icon.activated.connect(self._on_tray_activated)

    def _create_bass_clef_icon(self) -> QIcon:
        """Create a simple bass clef icon for system tray"""
        # Create a 64x64 pixmap
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw bass clef-inspired icon
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(0, 122, 255))  # Blue color

        # Simple circle with musical note
        painter.drawEllipse(8, 8, 48, 48)

        # Draw simplified bass clef shape
        painter.setBrush(QColor(255, 255, 255))
        painter.drawEllipse(20, 20, 10, 10)
        painter.drawEllipse(34, 20, 10, 10)

        painter.end()

        return QIcon(pixmap)

    def _create_menu(self) -> None:
        """Create the system tray menu"""
        self.menu = QMenu()

        # Show/Hide window
        self.show_action = QAction("Show Window", self)
        self.show_action.triggered.connect(lambda: self.show_window_requested.emit())
        self.menu.addAction(self.show_action)

        self.hide_action = QAction("Hide Window", self)
        self.hide_action.triggered.connect(lambda: self.hide_window_requested.emit())
        self.menu.addAction(self.hide_action)

        self.menu.addSeparator()

        # Modes submenu
        modes_menu = QMenu("Switch Mode", self.menu)

        self.idle_action = QAction("💤 Idle", self)
        self.idle_action.triggered.connect(lambda: self._request_mode("idle"))
        modes_menu.addAction(self.idle_action)

        self.jam_action = QAction("🎸 Jam", self)
        self.jam_action.triggered.connect(lambda: self._request_mode("jam"))
        modes_menu.addAction(self.jam_action)

        self.learn_action = QAction("👁️ Learn", self)
        self.learn_action.triggered.connect(lambda: self._request_mode("learn"))
        modes_menu.addAction(self.learn_action)

        self.lock_action = QAction("🔒 Lock", self)
        self.lock_action.triggered.connect(lambda: self._request_mode("lock"))
        modes_menu.addAction(self.lock_action)

        self.menu.addMenu(modes_menu)

        self.menu.addSeparator()

        # Features
        self.youtube_action = QAction("🎥 YouTube Analyzer", self)
        self.youtube_action.triggered.connect(lambda: self._request_feature("youtube"))
        self.menu.addAction(self.youtube_action)

        self.stem_action = QAction("✂️ STEM Separator", self)
        self.stem_action.triggered.connect(lambda: self._request_feature("stem"))
        self.menu.addAction(self.stem_action)

        self.humming_action = QAction("🎤 Humming Recorder", self)
        self.humming_action.triggered.connect(lambda: self._request_feature("humming"))
        self.menu.addAction(self.humming_action)

        self.menu.addSeparator()

        # Assistant features
        assistant_menu = QMenu("AI Assistant", self.menu)

        self.voice_action = QAction("💬 Voice Chat", self)
        self.voice_action.triggered.connect(lambda: self._request_feature("voice_chat"))
        assistant_menu.addAction(self.voice_action)

        self.code_action = QAction("💻 Code Helper", self)
        self.code_action.triggered.connect(lambda: self._request_feature("code_helper"))
        assistant_menu.addAction(self.code_action)

        self.writing_action = QAction("✍️ Writing Assistant", self)
        self.writing_action.triggered.connect(lambda: self._request_feature("writing"))
        assistant_menu.addAction(self.writing_action)

        self.menu.addMenu(assistant_menu)

        self.menu.addSeparator()

        # Quick actions
        self.command_palette_action = QAction("⌘ Command Palette", self)
        self.command_palette_action.triggered.connect(lambda: self._request_feature("command_palette"))
        self.menu.addAction(self.command_palette_action)

        self.presets_action = QAction("📋 Presets", self)
        self.presets_action.triggered.connect(lambda: self._request_feature("presets"))
        self.menu.addAction(self.presets_action)

        self.menu.addSeparator()

        # Settings and exit
        self.settings_action = QAction("⚙️ Settings", self)
        self.settings_action.triggered.connect(lambda: self._request_feature("settings"))
        self.menu.addAction(self.settings_action)

        self.exit_action = QAction("❌ Exit DAIW", self)
        self.exit_action.triggered.connect(lambda: self.exit_requested.emit())
        self.menu.addAction(self.exit_action)

        # Set menu for tray icon
        if self.tray_icon:
            self.tray_icon.setContextMenu(self.menu)

    def _request_mode(self, mode: str) -> None:
        """Request mode change"""
        self.current_mode = mode
        self.mode_change_requested.emit(mode)
        self.update_tooltip()

    def _request_feature(self, feature: str) -> None:
        """Request feature activation"""
        self.feature_requested.emit(feature)

    def _on_tray_activated(self, reason) -> None:
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            # Single click - show window
            self.show_window_requested.emit()
        elif reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            # Double click - show command palette
            self._request_feature("command_palette")

    def show(self) -> None:
        """Show system tray icon"""
        if self.tray_icon:
            self.tray_icon.show()

    def hide(self) -> None:
        """Hide system tray icon"""
        if self.tray_icon:
            self.tray_icon.hide()

    def is_visible(self) -> bool:
        """Check if tray icon is visible"""
        return self.tray_icon.isVisible() if self.tray_icon else False

    def update_tooltip(self) -> None:
        """Update tray icon tooltip with current status"""
        if self.tray_icon:
            tooltip = f"DAIW - Mode: {self.current_mode.capitalize()}"
            self.tray_icon.setToolTip(tooltip)

    def show_message(
        self,
        title: str,
        message: str,
        icon: QSystemTrayIcon.MessageIcon = QSystemTrayIcon.MessageIcon.Information,
        duration: int = 3000
    ) -> None:
        """
        Show notification message

        Args:
            title: Notification title
            message: Notification message
            icon: Icon type
            duration: Duration in milliseconds
        """
        if self.tray_icon and self.tray_icon.isVisible():
            self.tray_icon.showMessage(title, message, icon, duration)

    def show_info(self, title: str, message: str) -> None:
        """Show info notification"""
        self.show_message(title, message, QSystemTrayIcon.MessageIcon.Information)

    def show_warning(self, title: str, message: str) -> None:
        """Show warning notification"""
        self.show_message(title, message, QSystemTrayIcon.MessageIcon.Warning)

    def show_error(self, title: str, message: str) -> None:
        """Show error notification"""
        self.show_message(title, message, QSystemTrayIcon.MessageIcon.Critical)

    def update_mode_status(self, mode: str) -> None:
        """Update current mode status"""
        self.current_mode = mode
        self.update_tooltip()

    def set_icon_color(self, color: str) -> None:
        """
        Change tray icon color

        Args:
            color: Color name or hex code
        """
        # This would create a new icon with different color
        # For now, just update the tooltip
        self.update_tooltip()
