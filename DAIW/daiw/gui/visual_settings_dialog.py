"""
Visual Settings Dialog - Customize visual effects and themes

Allows users to:
- Enable/disable effects
- Choose themes
- Adjust particle density
- Control glow intensity
- Toggle performance mode
- Preview effects in real-time
"""

from typing import Optional
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QCheckBox,
    QComboBox,
    QSlider,
    QGroupBox,
    QTabWidget,
    QWidget,
    QSpinBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from daiw.gui.themes import get_theme_manager
from daiw.gui.modern_widgets import GlassCard, GlassButton, NeonLabel


class VisualSettingsDialog(QDialog):
    """Dialog for customizing visual effects and appearance"""

    # Signals
    effects_enabled_changed = pyqtSignal(bool)
    theme_changed = pyqtSignal(str)
    performance_mode_changed = pyqtSignal(bool)
    particle_density_changed = pyqtSignal(int)
    glow_intensity_changed = pyqtSignal(float)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.setWindowTitle("⚙️ Visual Settings")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)

        # Get theme manager
        self.theme_manager = get_theme_manager()

        # Current settings (defaults)
        self.effects_enabled = True
        self.performance_mode = False
        self.particle_density = 2  # 0=Low, 1=Medium, 2=High
        self.glow_intensity = 1.0  # 0.0-2.0

        self._setup_ui()

        # Apply current theme stylesheet
        self.setStyleSheet(self.theme_manager.current_theme.get_stylesheet())

    def _setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout()

        # Title
        title = NeonLabel("Visual Settings", self.theme_manager.current_theme.color_scheme.primary)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("Customize DAIW's stunning visual appearance")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setFont(QFont("Segoe UI", 10))
        layout.addWidget(subtitle)

        # Tabs
        tabs = QTabWidget()
        tabs.addTab(self._create_effects_tab(), "✨ Effects")
        tabs.addTab(self._create_theme_tab(), "🎨 Themes")
        tabs.addTab(self._create_performance_tab(), "⚡ Performance")
        tabs.addTab(self._create_preview_tab(), "👁️ Preview")

        layout.addWidget(tabs)

        # Buttons
        button_layout = QHBoxLayout()

        reset_btn = QPushButton("🔄 Reset to Defaults")
        reset_btn.clicked.connect(self._reset_defaults)
        button_layout.addWidget(reset_btn)

        button_layout.addStretch()

        apply_btn = QPushButton("✅ Apply")
        apply_btn.clicked.connect(self._apply_settings)
        button_layout.addWidget(apply_btn)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _create_effects_tab(self) -> QWidget:
        """Create effects configuration tab"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Enable/Disable Effects
        effects_group = QGroupBox("Effect Controls")
        effects_layout = QVBoxLayout()

        self.effects_check = QCheckBox("Enable Visual Effects")
        self.effects_check.setChecked(self.effects_enabled)
        self.effects_check.setToolTip("Enable particle effects, glows, and animations")
        self.effects_check.stateChanged.connect(self._on_effects_toggled)
        effects_layout.addWidget(self.effects_check)

        info_label = QLabel("Disable this to improve performance or if you prefer minimal visuals")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #888; font-size: 10px;")
        effects_layout.addWidget(info_label)

        effects_group.setLayout(effects_layout)
        layout.addWidget(effects_group)

        # Particle Settings
        particle_group = QGroupBox("Particle Effects")
        particle_layout = QVBoxLayout()

        density_label = QLabel("Particle Density:")
        particle_layout.addWidget(density_label)

        density_layout = QHBoxLayout()
        self.density_slider = QSlider(Qt.Orientation.Horizontal)
        self.density_slider.setRange(0, 2)  # Low, Medium, High
        self.density_slider.setValue(self.particle_density)
        self.density_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.density_slider.setTickInterval(1)
        self.density_slider.valueChanged.connect(self._on_density_changed)
        density_layout.addWidget(self.density_slider)

        self.density_label = QLabel(self._get_density_text(self.particle_density))
        self.density_label.setMinimumWidth(80)
        density_layout.addWidget(self.density_label)

        particle_layout.addLayout(density_layout)

        particle_desc = QLabel("Higher density = more particles = more eye candy (but lower FPS)")
        particle_desc.setWordWrap(True)
        particle_desc.setStyleSheet("color: #888; font-size: 10px;")
        particle_layout.addWidget(particle_desc)

        particle_group.setLayout(particle_layout)
        layout.addWidget(particle_group)

        # Glow Settings
        glow_group = QGroupBox("Glow Effects")
        glow_layout = QVBoxLayout()

        glow_label = QLabel("Glow Intensity:")
        glow_layout.addWidget(glow_label)

        glow_slider_layout = QHBoxLayout()
        self.glow_slider = QSlider(Qt.Orientation.Horizontal)
        self.glow_slider.setRange(0, 200)  # 0% - 200%
        self.glow_slider.setValue(int(self.glow_intensity * 100))
        self.glow_slider.valueChanged.connect(self._on_glow_changed)
        glow_slider_layout.addWidget(self.glow_slider)

        self.glow_label = QLabel(f"{self.glow_intensity * 100:.0f}%")
        self.glow_label.setMinimumWidth(60)
        glow_slider_layout.addWidget(self.glow_label)

        glow_layout.addLayout(glow_slider_layout)

        glow_desc = QLabel("Control the intensity of avatar glow effects")
        glow_desc.setWordWrap(True)
        glow_desc.setStyleSheet("color: #888; font-size: 10px;")
        glow_layout.addWidget(glow_desc)

        glow_group.setLayout(glow_layout)
        layout.addWidget(glow_group)

        layout.addStretch()
        tab.setLayout(layout)
        return tab

    def _create_theme_tab(self) -> QWidget:
        """Create theme selection tab"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Theme selector
        theme_group = QGroupBox("Theme Selection")
        theme_layout = QVBoxLayout()

        theme_label = QLabel("Choose a theme:")
        theme_layout.addWidget(theme_label)

        self.theme_combo = QComboBox()
        for theme_name in self.theme_manager.get_available_themes():
            self.theme_combo.addItem(theme_name.title(), theme_name)
        self.theme_combo.setCurrentText(self.theme_manager.current_theme.name.title())
        self.theme_combo.currentTextChanged.connect(self._on_theme_selected)
        theme_layout.addWidget(self.theme_combo)

        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)

        # Theme previews
        preview_group = QGroupBox("Theme Colors")
        preview_layout = QVBoxLayout()

        self.theme_info = QLabel()
        self.theme_info.setWordWrap(True)
        self._update_theme_info()
        preview_layout.addWidget(self.theme_info)

        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)

        # Theme descriptions
        descriptions = {
            "dark": "Classic dark theme with blue and pink accents. Professional and easy on the eyes.",
            "light": "Clean light theme for daytime use. Soft colors with high readability.",
            "cyberpunk": "Neon cyan and magenta. High-tech futuristic aesthetic.",
            "sunset": "Warm oranges and reds. Cozy and inviting atmosphere.",
            "ocean": "Cool blues and turquoise. Calm and refreshing.",
            "forest": "Natural greens and earth tones. Organic and peaceful."
        }

        desc_group = QGroupBox("Theme Descriptions")
        desc_layout = QVBoxLayout()

        for theme_name, description in descriptions.items():
            theme_desc = QLabel(f"<b>{theme_name.title()}:</b> {description}")
            theme_desc.setWordWrap(True)
            desc_layout.addWidget(theme_desc)

        desc_group.setLayout(desc_layout)
        layout.addWidget(desc_group)

        layout.addStretch()
        tab.setLayout(layout)
        return tab

    def _create_performance_tab(self) -> QWidget:
        """Create performance settings tab"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Performance mode
        perf_group = QGroupBox("Performance Optimization")
        perf_layout = QVBoxLayout()

        self.performance_check = QCheckBox("Enable Performance Mode")
        self.performance_check.setChecked(self.performance_mode)
        self.performance_check.setToolTip("Reduces effects for better FPS on slower systems")
        self.performance_check.stateChanged.connect(self._on_performance_toggled)
        perf_layout.addWidget(self.performance_check)

        perf_desc = QLabel(
            "Performance mode automatically reduces particle counts, "
            "disables some animations, and simplifies effects to maintain 60 FPS. "
            "Enable this on older/slower computers."
        )
        perf_desc.setWordWrap(True)
        perf_desc.setStyleSheet("color: #888;")
        perf_layout.addWidget(perf_desc)

        perf_group.setLayout(perf_layout)
        layout.addWidget(perf_group)

        # Auto Performance
        auto_group = QGroupBox("Automatic Performance Scaling")
        auto_layout = QVBoxLayout()

        auto_check = QCheckBox("Auto-Enable Performance Mode if FPS < 30")
        auto_check.setChecked(True)
        auto_check.setToolTip("Automatically enable performance mode when frame rate drops")
        auto_layout.addWidget(auto_check)

        auto_desc = QLabel(
            "DAIW monitors frame rate and automatically enables performance mode "
            "if FPS drops below 30, ensuring smooth operation."
        )
        auto_desc.setWordWrap(True)
        auto_desc.setStyleSheet("color: #888;")
        auto_layout.addWidget(auto_desc)

        auto_group.setLayout(auto_layout)
        layout.addWidget(auto_group)

        # FPS Target
        fps_group = QGroupBox("Target Frame Rate")
        fps_layout = QVBoxLayout()

        fps_label = QLabel("Target FPS: 60")
        fps_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        fps_layout.addWidget(fps_label)

        fps_desc = QLabel(
            "DAIW targets 60 FPS for buttery-smooth animations. "
            "All effects are optimized to maintain this frame rate."
        )
        fps_desc.setWordWrap(True)
        fps_desc.setStyleSheet("color: #888;")
        fps_layout.addWidget(fps_desc)

        fps_group.setLayout(fps_layout)
        layout.addWidget(fps_group)

        # System recommendations
        rec_group = QGroupBox("Recommended Settings")
        rec_layout = QVBoxLayout()

        rec_text = """
        <b>High-Performance PC:</b><br>
        • All effects enabled<br>
        • High particle density<br>
        • 150-200% glow intensity<br>
        • Any theme<br>
        <br>
        <b>Mid-Range PC:</b><br>
        • Effects enabled<br>
        • Medium particle density<br>
        • 100% glow intensity<br>
        • Dark or Light theme<br>
        <br>
        <b>Low-End PC / Battery Saving:</b><br>
        • Performance mode enabled<br>
        • Low particle density or effects disabled<br>
        • 50% glow intensity<br>
        • Dark or Light theme (less GPU usage)
        """

        rec_label = QLabel(rec_text)
        rec_label.setWordWrap(True)
        rec_layout.addWidget(rec_label)

        rec_group.setLayout(rec_layout)
        layout.addWidget(rec_group)

        layout.addStretch()
        tab.setLayout(layout)
        return tab

    def _create_preview_tab(self) -> QWidget:
        """Create live preview tab"""
        tab = QWidget()
        layout = QVBoxLayout()

        preview_label = QLabel("Live Preview")
        preview_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(preview_label)

        info = QLabel("Changes are applied in real-time to the avatar. "
                     "Close this dialog to see the effects.")
        info.setWordWrap(True)
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setStyleSheet("color: #888;")
        layout.addWidget(info)

        # TODO: Could add a mini avatar preview here
        preview_placeholder = QLabel("🎵\n\nAvatar Preview\n\n(Feature coming soon)")
        preview_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_placeholder.setFont(QFont("Segoe UI", 20))
        preview_placeholder.setMinimumHeight(200)
        preview_placeholder.setStyleSheet("border: 2px dashed #666; border-radius: 10px;")
        layout.addWidget(preview_placeholder)

        layout.addStretch()
        tab.setLayout(layout)
        return tab

    def _get_density_text(self, value: int) -> str:
        """Get density level text"""
        levels = ["Low", "Medium", "High"]
        return levels[value] if 0 <= value < len(levels) else "Medium"

    def _on_effects_toggled(self, state):
        """Handle effects toggle"""
        self.effects_enabled = bool(state)
        # Enable/disable related controls
        self.density_slider.setEnabled(self.effects_enabled)
        self.glow_slider.setEnabled(self.effects_enabled)

    def _on_density_changed(self, value):
        """Handle particle density change"""
        self.particle_density = value
        self.density_label.setText(self._get_density_text(value))

    def _on_glow_changed(self, value):
        """Handle glow intensity change"""
        self.glow_intensity = value / 100.0
        self.glow_label.setText(f"{value}%")

    def _on_performance_toggled(self, state):
        """Handle performance mode toggle"""
        self.performance_mode = bool(state)

    def _on_theme_selected(self, theme_name):
        """Handle theme selection"""
        theme_key = theme_name.lower()
        self._update_theme_info()

    def _update_theme_info(self):
        """Update theme information display"""
        theme = self.theme_manager.current_theme

        info_text = f"""
        <b>Current Theme:</b> {theme.name}<br>
        <b>Type:</b> {"Dark" if theme.is_dark else "Light"}<br>
        <br>
        <b>Mode Colors:</b><br>
        • Idle: {theme.idle_color.name()}<br>
        • Jam: {theme.jam_color.name()}<br>
        • Learn: {theme.learn_color.name()}<br>
        • Lock: {theme.lock_color.name()}<br>
        • Thinking: {theme.thinking_color.name()}
        """

        self.theme_info.setText(info_text)

    def _reset_defaults(self):
        """Reset all settings to defaults"""
        self.effects_check.setChecked(True)
        self.performance_check.setChecked(False)
        self.density_slider.setValue(2)
        self.glow_slider.setValue(100)
        self.theme_combo.setCurrentText("Dark")

    def _apply_settings(self):
        """Apply all settings"""
        # Emit signals
        self.effects_enabled_changed.emit(self.effects_enabled)
        self.performance_mode_changed.emit(self.performance_mode)
        self.particle_density_changed.emit(self.particle_density)
        self.glow_intensity_changed.emit(self.glow_intensity)

        # Apply theme
        theme_name = self.theme_combo.currentText().lower()
        self.theme_manager.set_theme(theme_name)
        self.theme_changed.emit(theme_name)

        # Update stylesheet
        self.setStyleSheet(self.theme_manager.current_theme.get_stylesheet())

    def get_settings(self) -> dict:
        """Get current settings as dictionary"""
        return {
            "effects_enabled": self.effects_enabled,
            "performance_mode": self.performance_mode,
            "particle_density": self.particle_density,
            "glow_intensity": self.glow_intensity,
            "theme": self.theme_combo.currentText().lower()
        }
