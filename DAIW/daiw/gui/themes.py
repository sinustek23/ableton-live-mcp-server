"""
Theme System - Color schemes and visual styling

Provides dark/light themes, custom color palettes, and consistent styling
across the entire DAIW interface.
"""

from typing import Dict, Optional
from PyQt6.QtGui import QColor, QPalette, QFont
from PyQt6.QtCore import QObject, pyqtSignal
from dataclasses import dataclass
import json
from pathlib import Path


@dataclass
class ColorScheme:
    """Color scheme for a specific mode/theme"""
    primary: QColor
    secondary: QColor
    accent: QColor
    background: QColor
    surface: QColor
    text: QColor
    text_secondary: QColor
    success: QColor
    warning: QColor
    error: QColor
    glow: QColor


class Theme:
    """Complete theme with colors and styling"""

    def __init__(self, name: str, is_dark: bool = True):
        self.name = name
        self.is_dark = is_dark

        # Mode-specific colors
        self.idle_color = QColor(100, 150, 255, 200)  # Blue
        self.jam_color = QColor(255, 100, 150, 200)  # Pink/Red
        self.learn_color = QColor(100, 255, 150, 200)  # Green
        self.lock_color = QColor(255, 200, 50, 200)  # Gold
        self.thinking_color = QColor(200, 100, 255, 200)  # Purple

        # UI color scheme
        if is_dark:
            self.color_scheme = ColorScheme(
                primary=QColor(100, 150, 255),
                secondary=QColor(80, 120, 200),
                accent=QColor(255, 100, 150),
                background=QColor(20, 20, 25),
                surface=QColor(30, 30, 35),
                text=QColor(240, 240, 245),
                text_secondary=QColor(160, 160, 170),
                success=QColor(100, 255, 150),
                warning=QColor(255, 200, 50),
                error=QColor(255, 80, 80),
                glow=QColor(100, 150, 255, 100)
            )
        else:
            self.color_scheme = ColorScheme(
                primary=QColor(60, 100, 200),
                secondary=QColor(80, 120, 220),
                accent=QColor(220, 60, 100),
                background=QColor(245, 245, 250),
                surface=QColor(255, 255, 255),
                text=QColor(20, 20, 30),
                text_secondary=QColor(100, 100, 120),
                success=QColor(50, 200, 100),
                warning=QColor(220, 160, 40),
                error=QColor(220, 60, 60),
                glow=QColor(100, 150, 255, 80)
            )

    def get_mode_color(self, mode: str) -> QColor:
        """Get color for specific avatar mode"""
        mode_colors = {
            "idle": self.idle_color,
            "jam": self.jam_color,
            "playing": self.jam_color,
            "learn": self.learn_color,
            "listening": self.learn_color,
            "lock": self.lock_color,
            "locked": self.lock_color,
            "thinking": self.thinking_color,
        }
        return mode_colors.get(mode, self.idle_color)

    def get_stylesheet(self) -> str:
        """Get Qt stylesheet for this theme"""
        if self.is_dark:
            return self._get_dark_stylesheet()
        else:
            return self._get_light_stylesheet()

    def _get_dark_stylesheet(self) -> str:
        """Dark theme stylesheet"""
        return f"""
            /* Global Styles */
            QWidget {{
                background-color: {self.color_scheme.background.name()};
                color: {self.color_scheme.text.name()};
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
            }}

            /* Dialogs */
            QDialog {{
                background-color: {self.color_scheme.background.name()};
                border: 1px solid {self.color_scheme.primary.name()};
                border-radius: 10px;
            }}

            /* Labels */
            QLabel {{
                background-color: transparent;
                color: {self.color_scheme.text.name()};
            }}

            /* Buttons */
            QPushButton {{
                background-color: {self.color_scheme.surface.name()};
                color: {self.color_scheme.text.name()};
                border: 2px solid {self.color_scheme.primary.name()};
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
            }}

            QPushButton:hover {{
                background-color: {self.color_scheme.primary.darker(150).name()};
                border-color: {self.color_scheme.primary.lighter(120).name()};
            }}

            QPushButton:pressed {{
                background-color: {self.color_scheme.primary.darker(130).name()};
            }}

            QPushButton:disabled {{
                background-color: {self.color_scheme.surface.darker(120).name()};
                color: {self.color_scheme.text_secondary.name()};
                border-color: {self.color_scheme.text_secondary.darker(150).name()};
            }}

            /* Input Fields */
            QLineEdit, QTextEdit {{
                background-color: {self.color_scheme.surface.name()};
                color: {self.color_scheme.text.name()};
                border: 2px solid {self.color_scheme.secondary.name()};
                border-radius: 6px;
                padding: 6px 10px;
                selection-background-color: {self.color_scheme.primary.name()};
            }}

            QLineEdit:focus, QTextEdit:focus {{
                border-color: {self.color_scheme.primary.name()};
            }}

            /* Combo Boxes */
            QComboBox {{
                background-color: {self.color_scheme.surface.name()};
                color: {self.color_scheme.text.name()};
                border: 2px solid {self.color_scheme.secondary.name()};
                border-radius: 6px;
                padding: 6px 10px;
            }}

            QComboBox:hover {{
                border-color: {self.color_scheme.primary.name()};
            }}

            QComboBox::drop-down {{
                border: none;
            }}

            QComboBox QAbstractItemView {{
                background-color: {self.color_scheme.surface.name()};
                color: {self.color_scheme.text.name()};
                selection-background-color: {self.color_scheme.primary.name()};
                border: 1px solid {self.color_scheme.primary.name()};
            }}

            /* Spin Boxes */
            QSpinBox, QDoubleSpinBox {{
                background-color: {self.color_scheme.surface.name()};
                color: {self.color_scheme.text.name()};
                border: 2px solid {self.color_scheme.secondary.name()};
                border-radius: 6px;
                padding: 6px;
            }}

            /* Progress Bars */
            QProgressBar {{
                background-color: {self.color_scheme.surface.name()};
                border: 2px solid {self.color_scheme.secondary.name()};
                border-radius: 8px;
                text-align: center;
                color: {self.color_scheme.text.name()};
                font-weight: bold;
            }}

            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.color_scheme.primary.name()},
                    stop:1 {self.color_scheme.accent.name()});
                border-radius: 6px;
            }}

            /* Group Boxes */
            QGroupBox {{
                color: {self.color_scheme.text.name()};
                border: 2px solid {self.color_scheme.primary.name()};
                border-radius: 8px;
                margin-top: 12px;
                font-weight: bold;
                padding-top: 10px;
            }}

            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 8px;
                background-color: {self.color_scheme.background.name()};
            }}

            /* Check Boxes */
            QCheckBox {{
                color: {self.color_scheme.text.name()};
                spacing: 8px;
            }}

            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border: 2px solid {self.color_scheme.secondary.name()};
                border-radius: 4px;
                background-color: {self.color_scheme.surface.name()};
            }}

            QCheckBox::indicator:checked {{
                background-color: {self.color_scheme.primary.name()};
                border-color: {self.color_scheme.primary.name()};
            }}

            /* Lists */
            QListWidget {{
                background-color: {self.color_scheme.surface.name()};
                color: {self.color_scheme.text.name()};
                border: 2px solid {self.color_scheme.secondary.name()};
                border-radius: 6px;
                padding: 4px;
            }}

            QListWidget::item {{
                padding: 8px;
                border-radius: 4px;
            }}

            QListWidget::item:selected {{
                background-color: {self.color_scheme.primary.name()};
            }}

            QListWidget::item:hover {{
                background-color: {self.color_scheme.primary.darker(150).name()};
            }}

            /* Tab Widget */
            QTabWidget::pane {{
                border: 2px solid {self.color_scheme.secondary.name()};
                border-radius: 6px;
                background-color: {self.color_scheme.background.name()};
            }}

            QTabBar::tab {{
                background-color: {self.color_scheme.surface.name()};
                color: {self.color_scheme.text_secondary.name()};
                border: 2px solid {self.color_scheme.secondary.name()};
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 8px 16px;
                margin-right: 2px;
            }}

            QTabBar::tab:selected {{
                background-color: {self.color_scheme.background.name()};
                color: {self.color_scheme.text.name()};
                border-color: {self.color_scheme.primary.name()};
                font-weight: bold;
            }}

            QTabBar::tab:hover {{
                background-color: {self.color_scheme.primary.darker(150).name()};
            }}

            /* Scrollbars */
            QScrollBar:vertical {{
                background-color: {self.color_scheme.surface.name()};
                width: 12px;
                border-radius: 6px;
            }}

            QScrollBar::handle:vertical {{
                background-color: {self.color_scheme.primary.name()};
                border-radius: 6px;
                min-height: 20px;
            }}

            QScrollBar::handle:vertical:hover {{
                background-color: {self.color_scheme.primary.lighter(120).name()};
            }}

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}

            QScrollBar:horizontal {{
                background-color: {self.color_scheme.surface.name()};
                height: 12px;
                border-radius: 6px;
            }}

            QScrollBar::handle:horizontal {{
                background-color: {self.color_scheme.primary.name()};
                border-radius: 6px;
                min-width: 20px;
            }}

            QScrollBar::handle:horizontal:hover {{
                background-color: {self.color_scheme.primary.lighter(120).name()};
            }}

            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}

            /* Menu */
            QMenu {{
                background-color: {self.color_scheme.surface.name()};
                color: {self.color_scheme.text.name()};
                border: 2px solid {self.color_scheme.primary.name()};
                border-radius: 6px;
                padding: 4px;
            }}

            QMenu::item {{
                padding: 8px 24px 8px 8px;
                border-radius: 4px;
            }}

            QMenu::item:selected {{
                background-color: {self.color_scheme.primary.name()};
            }}

            QMenu::separator {{
                height: 2px;
                background-color: {self.color_scheme.secondary.name()};
                margin: 4px 8px;
            }}
        """

    def _get_light_stylesheet(self) -> str:
        """Light theme stylesheet"""
        return f"""
            /* Global Styles */
            QWidget {{
                background-color: {self.color_scheme.background.name()};
                color: {self.color_scheme.text.name()};
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
            }}

            /* Dialogs */
            QDialog {{
                background-color: {self.color_scheme.background.name()};
                border: 1px solid {self.color_scheme.primary.name()};
                border-radius: 10px;
            }}

            /* Buttons */
            QPushButton {{
                background-color: {self.color_scheme.surface.name()};
                color: {self.color_scheme.text.name()};
                border: 2px solid {self.color_scheme.primary.name()};
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
            }}

            QPushButton:hover {{
                background-color: {self.color_scheme.primary.lighter(180).name()};
                border-color: {self.color_scheme.primary.darker(120).name()};
            }}

            QPushButton:pressed {{
                background-color: {self.color_scheme.primary.lighter(160).name()};
            }}

            /* Similar styles for other widgets... */
            /* (abbreviated for brevity - same structure as dark theme) */
        """


class ThemeManager(QObject):
    """Manages themes and provides theme switching"""

    theme_changed = pyqtSignal(Theme)

    def __init__(self):
        super().__init__()

        # Available themes
        self.themes: Dict[str, Theme] = {
            "dark": Theme("Dark", is_dark=True),
            "light": Theme("Light", is_dark=False),
            "cyberpunk": self._create_cyberpunk_theme(),
            "sunset": self._create_sunset_theme(),
            "ocean": self._create_ocean_theme(),
            "forest": self._create_forest_theme(),
        }

        self.current_theme = self.themes["dark"]

    def _create_cyberpunk_theme(self) -> Theme:
        """Create cyberpunk neon theme"""
        theme = Theme("Cyberpunk", is_dark=True)
        theme.idle_color = QColor(0, 255, 255, 200)  # Cyan
        theme.jam_color = QColor(255, 0, 255, 200)  # Magenta
        theme.learn_color = QColor(0, 255, 100, 200)  # Neon green
        theme.lock_color = QColor(255, 255, 0, 200)  # Yellow
        theme.thinking_color = QColor(255, 100, 255, 200)  # Pink

        theme.color_scheme.primary = QColor(0, 255, 255)
        theme.color_scheme.accent = QColor(255, 0, 255)
        theme.color_scheme.background = QColor(10, 0, 20)
        theme.color_scheme.surface = QColor(20, 0, 40)

        return theme

    def _create_sunset_theme(self) -> Theme:
        """Create warm sunset theme"""
        theme = Theme("Sunset", is_dark=True)
        theme.idle_color = QColor(255, 150, 100, 200)  # Warm orange
        theme.jam_color = QColor(255, 100, 100, 200)  # Red
        theme.learn_color = QColor(255, 200, 100, 200)  # Gold
        theme.lock_color = QColor(200, 100, 200, 200)  # Purple
        theme.thinking_color = QColor(255, 150, 150, 200)  # Pink

        theme.color_scheme.primary = QColor(255, 150, 100)
        theme.color_scheme.accent = QColor(255, 100, 100)
        theme.color_scheme.background = QColor(30, 20, 25)
        theme.color_scheme.surface = QColor(40, 30, 35)

        return theme

    def _create_ocean_theme(self) -> Theme:
        """Create cool ocean theme"""
        theme = Theme("Ocean", is_dark=True)
        theme.idle_color = QColor(100, 150, 255, 200)  # Ocean blue
        theme.jam_color = QColor(100, 200, 255, 200)  # Sky blue
        theme.learn_color = QColor(100, 255, 200, 200)  # Turquoise
        theme.lock_color = QColor(150, 100, 255, 200)  # Deep purple
        theme.thinking_color = QColor(150, 200, 255, 200)  # Light blue

        theme.color_scheme.primary = QColor(100, 200, 255)
        theme.color_scheme.accent = QColor(100, 255, 200)
        theme.color_scheme.background = QColor(10, 20, 30)
        theme.color_scheme.surface = QColor(20, 30, 40)

        return theme

    def _create_forest_theme(self) -> Theme:
        """Create natural forest theme"""
        theme = Theme("Forest", is_dark=True)
        theme.idle_color = QColor(100, 200, 100, 200)  # Green
        theme.jam_color = QColor(150, 255, 100, 200)  # Bright green
        theme.learn_color = QColor(100, 255, 150, 200)  # Mint
        theme.lock_color = QColor(200, 200, 100, 200)  # Yellow-green
        theme.thinking_color = QColor(150, 200, 150, 200)  # Light green

        theme.color_scheme.primary = QColor(100, 200, 100)
        theme.color_scheme.accent = QColor(150, 255, 100)
        theme.color_scheme.background = QColor(15, 25, 15)
        theme.color_scheme.surface = QColor(25, 35, 25)

        return theme

    def set_theme(self, theme_name: str):
        """Switch to a different theme"""
        if theme_name in self.themes:
            self.current_theme = self.themes[theme_name]
            self.theme_changed.emit(self.current_theme)

    def get_current_theme(self) -> Theme:
        """Get currently active theme"""
        return self.current_theme

    def get_available_themes(self) -> list:
        """Get list of available theme names"""
        return list(self.themes.keys())


# Global theme manager instance
_theme_manager = ThemeManager()


def get_theme_manager() -> ThemeManager:
    """Get the global theme manager instance"""
    return _theme_manager
