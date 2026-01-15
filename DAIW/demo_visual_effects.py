#!/usr/bin/env python3
"""
Visual Effects Demo - Showcase DAIW's stunning visual enhancements

This demo shows off all the visual effects in action:
- Particle systems
- Glow effects
- Smooth animations
- Modern widgets
- Theme switching
- Glassmorphism UI

Run this to see the eye candy!
"""

import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QComboBox,
    QSlider
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

# Import our visual enhancement systems
from DAIW.daiw.gui.bass_clef_widget_enhanced import BassClefWidget, AvatarState
from DAIW.daiw.gui.themes import get_theme_manager
from DAIW.daiw.gui.modern_widgets import (
    GlassButton,
    GlassCard,
    AnimatedProgressBar,
    NeonLabel,
    RoundedIconButton,
    NotificationToastWidget,
    LoadingSpinnerWidget,
    ConnectionStatusIndicator
)
from DAIW.daiw.gui.animations import SlideAnimation


class VisualEffectsDemo(QMainWindow):
    """Demo window showcasing visual effects"""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("DAIW Visual Effects Demo ✨")
        self.setGeometry(100, 100, 1000, 700)

        # Theme manager
        self.theme_manager = get_theme_manager()

        # Setup UI
        self._setup_ui()

        # Apply theme
        self.setStyleSheet(self.theme_manager.current_theme.get_stylesheet())

        # Demo automation
        self.demo_timer = QTimer()
        self.demo_timer.timeout.connect(self._cycle_demo)
        self.demo_step = 0

    def _setup_ui(self):
        """Setup the demo UI"""
        central = QWidget()
        self.setCentralWidget(central)

        layout = QHBoxLayout(central)

        # Left side: Avatar demo
        left_panel = self._create_avatar_panel()
        layout.addWidget(left_panel, stretch=1)

        # Right side: Controls
        right_panel = self._create_control_panel()
        layout.addWidget(right_panel, stretch=1)

    def _create_avatar_panel(self) -> QWidget:
        """Create avatar demonstration panel"""
        panel = GlassCard()
        layout = QVBoxLayout(panel.layout)

        # Title
        title = NeonLabel("Enhanced Avatar", self.theme_manager.current_theme.color_scheme.primary)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Avatar
        self.avatar = BassClefWidget()
        self.avatar.setMinimumSize(400, 300)
        self.avatar.show_fps = True  # Show FPS counter
        layout.addWidget(self.avatar, stretch=1)

        # State controls
        state_layout = QHBoxLayout()

        self.idle_btn = GlassButton("💤 Idle")
        self.idle_btn.clicked.connect(lambda: self.avatar.set_state(AvatarState.IDLE))
        state_layout.addWidget(self.idle_btn)

        self.jam_btn = GlassButton("🎸 Jam")
        self.jam_btn.clicked.connect(lambda: self.avatar.set_state(AvatarState.PLAYING))
        state_layout.addWidget(self.jam_btn)

        self.learn_btn = GlassButton("👁️ Learn")
        self.learn_btn.clicked.connect(lambda: self.avatar.set_state(AvatarState.LISTENING))
        state_layout.addWidget(self.learn_btn)

        self.lock_btn = GlassButton("🔒 Lock")
        self.lock_btn.clicked.connect(lambda: self.avatar.set_state(AvatarState.LOCKED))
        state_layout.addWidget(self.lock_btn)

        self.think_btn = GlassButton("🧠 Think")
        self.think_btn.clicked.connect(lambda: self.avatar.set_state(AvatarState.THINKING))
        state_layout.addWidget(self.think_btn)

        layout.addLayout(state_layout)

        return panel

    def _create_control_panel(self) -> QWidget:
        """Create control panel"""
        panel = GlassCard()
        layout = QVBoxLayout(panel.layout)

        # Title
        title = QLabel("Visual Controls")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Theme selector
        theme_label = QLabel("Theme:")
        theme_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout.addWidget(theme_label)

        self.theme_combo = QComboBox()
        for theme in self.theme_manager.get_available_themes():
            self.theme_combo.addItem(theme.title(), theme)
        self.theme_combo.currentTextChanged.connect(self._on_theme_changed)
        layout.addWidget(self.theme_combo)

        # Effects toggle
        effects_label = QLabel("Effects:")
        effects_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout.addWidget(effects_label)

        effects_layout = QHBoxLayout()

        effects_on_btn = GlassButton("✅ On")
        effects_on_btn.clicked.connect(lambda: self.avatar.toggle_effects(True))
        effects_layout.addWidget(effects_on_btn)

        effects_off_btn = GlassButton("❌ Off")
        effects_off_btn.clicked.connect(lambda: self.avatar.toggle_effects(False))
        effects_layout.addWidget(effects_off_btn)

        layout.addLayout(effects_layout)

        # Progress bar demo
        progress_label = QLabel("Animated Progress:")
        progress_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout.addWidget(progress_label)

        self.progress = AnimatedProgressBar()
        self.progress.setValue(75)
        layout.addWidget(self.progress)

        # Spinner demo
        spinner_label = QLabel("Loading Spinner:")
        spinner_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout.addWidget(spinner_label)

        spinner_container = QWidget()
        spinner_layout = QHBoxLayout(spinner_container)
        spinner_layout.setContentsMargins(0, 0, 0, 0)

        self.spinner = LoadingSpinnerWidget(size=50, color=self.theme_manager.current_theme.color_scheme.primary)
        self.spinner.start()
        spinner_layout.addWidget(self.spinner)
        spinner_layout.addStretch()

        layout.addWidget(spinner_container)

        # Connection indicator demo
        conn_label = QLabel("Connection Status:")
        conn_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout.addWidget(conn_label)

        conn_layout = QHBoxLayout()

        self.conn_indicator = ConnectionStatusIndicator(size=25)
        self.conn_indicator.set_connected(True)
        conn_layout.addWidget(self.conn_indicator)

        conn_text = QLabel("Connected")
        conn_layout.addWidget(conn_text)
        conn_layout.addStretch()

        toggle_conn_btn = GlassButton("Toggle")
        toggle_conn_btn.clicked.connect(self._toggle_connection)
        conn_layout.addWidget(toggle_conn_btn)

        layout.addLayout(conn_layout)

        # Toast notification demo
        toast_btn = GlassButton("🔔 Show Toast")
        toast_btn.clicked.connect(self._show_toast)
        layout.addWidget(toast_btn)

        # Particle burst demo
        burst_btn = GlassButton("💥 Particle Burst")
        burst_btn.clicked.connect(self._emit_burst)
        layout.addWidget(burst_btn)

        # Auto demo
        layout.addWidget(QLabel(""))  # Spacer

        auto_demo_label = QLabel("Automated Demo:")
        auto_demo_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout.addWidget(auto_demo_label)

        auto_layout = QHBoxLayout()

        start_demo_btn = GlassButton("▶️ Start")
        start_demo_btn.clicked.connect(self._start_auto_demo)
        auto_layout.addWidget(start_demo_btn)

        stop_demo_btn = GlassButton("⏹️ Stop")
        stop_demo_btn.clicked.connect(self._stop_auto_demo)
        auto_layout.addWidget(stop_demo_btn)

        layout.addLayout(auto_layout)

        layout.addStretch()

        return panel

    def _on_theme_changed(self, theme_name):
        """Handle theme change"""
        theme_key = theme_name.lower()
        self.theme_manager.set_theme(theme_key)
        self.setStyleSheet(self.theme_manager.current_theme.get_stylesheet())

        # Update spinner color
        self.spinner.color = self.theme_manager.current_theme.color_scheme.primary

    def _toggle_connection(self):
        """Toggle connection indicator"""
        current = self.conn_indicator.connected
        self.conn_indicator.set_connected(not current)

    def _show_toast(self):
        """Show notification toast"""
        import random
        types = ["info", "success", "warning", "error"]
        messages = [
            ("Info", "This is an informational message"),
            ("Success", "Operation completed successfully!"),
            ("Warning", "Please review your settings"),
            ("Error", "Something went wrong!")
        ]

        toast_type = random.choice(types)
        title, message = random.choice(messages)

        toast = NotificationToastWidget(title, message, toast_type, self)

        # Position at bottom-right
        x = self.width() - toast.width() - 20
        y = self.height() - toast.height() - 20

        # Slide in
        slide = SlideAnimation(toast, direction="bottom")
        slide.slide_in((x, y))

        # Auto-close
        toast.closed.connect(lambda: slide.slide_out(hide=True))

    def _emit_burst(self):
        """Emit particle burst from avatar center"""
        from PyQt6.QtCore import QPointF

        center = QPointF(self.avatar.width() / 2, self.avatar.height() / 2)
        color = self.theme_manager.current_theme.get_mode_color(self.avatar.get_state().value)

        self.avatar.effects_manager.emit_burst(center, color, count=50)

    def _start_auto_demo(self):
        """Start automated demo cycle"""
        self.demo_step = 0
        self.demo_timer.start(3000)  # Change every 3 seconds
        self._show_toast_message("Auto Demo Started", "Watch the avatar cycle through states!", "info")

    def _stop_auto_demo(self):
        """Stop automated demo"""
        self.demo_timer.stop()
        self._show_toast_message("Auto Demo Stopped", "Manual control restored", "info")

    def _cycle_demo(self):
        """Cycle through demo states"""
        states = [
            (AvatarState.IDLE, "Idle Mode", "Subtle pulsing glow"),
            (AvatarState.PLAYING, "Jam Mode", "Musical notes + intense glow"),
            (AvatarState.LISTENING, "Learn Mode", "Spiral particles + waves"),
            (AvatarState.LOCKED, "Lock Mode", "Matrix rain effect"),
            (AvatarState.THINKING, "Thinking Mode", "Rainbow color cycle"),
        ]

        state, title, desc = states[self.demo_step % len(states)]
        self.avatar.set_state(state)

        # Show toast about current state
        self._show_toast_message(title, desc, "info")

        # Emit burst
        self._emit_burst()

        self.demo_step += 1

    def _show_toast_message(self, title: str, message: str, type: str):
        """Helper to show toast message"""
        toast = NotificationToastWidget(title, message, type, self)

        x = self.width() - toast.width() - 20
        y = self.height() - toast.height() - 20

        slide = SlideAnimation(toast, direction="bottom")
        slide.slide_in((x, y))

        toast.closed.connect(lambda: slide.slide_out(hide=True))


def main():
    """Run the visual effects demo"""
    app = QApplication(sys.argv)

    # Set application style
    app.setStyle("Fusion")

    # Create and show demo window
    demo = VisualEffectsDemo()
    demo.show()

    # Welcome message
    print("=" * 60)
    print("DAIW Visual Effects Demo")
    print("=" * 60)
    print()
    print("This demo showcases all visual enhancements:")
    print("  ✨ Particle effects (notes, matrix, spirals)")
    print("  🌟 Glow and pulsing effects")
    print("  🎨 6 beautiful themes")
    print("  💫 Smooth animations")
    print("  🔘 Modern glassmorphism widgets")
    print("  🚀 60 FPS performance")
    print()
    print("Try:")
    print("  • Click avatar state buttons to see different effects")
    print("  • Switch themes to see color changes")
    print("  • Toggle effects on/off")
    print("  • Start auto demo to see all states")
    print("  • Click 'Particle Burst' for fireworks!")
    print()
    print("FPS counter shown in top-left of avatar")
    print()
    print("=" * 60)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
