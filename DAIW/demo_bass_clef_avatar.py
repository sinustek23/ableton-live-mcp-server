#!/usr/bin/env python3
"""
Demo: Animated Bass Clef Avatar
Shows the expressive bass clef face with animated eyes and eyebrows
"""

import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                              QHBoxLayout, QPushButton, QLabel, QSlider,
                              QComboBox, QGroupBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor

sys.path.insert(0, '/home/user/ableton-live-mcp-server/DAIW')
from daiw.gui.bass_clef_widget_v3 import BassClefWidget, AvatarState


class AvatarDemo(QMainWindow):
    """Demo application for the bass clef avatar"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎵 Bass Clef Avatar - Expression Demo")
        self.resize(800, 700)

        # Main widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        # Title
        title = QLabel("🎵 Bass Clef Avatar Expression Demo")
        title.setStyleSheet("font-size: 24px; font-weight: bold; padding: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        # Avatar display
        self.avatar = BassClefWidget()
        self.avatar.setMinimumSize(400, 400)
        self.avatar.setStyleSheet("background: #f0f0f0; border-radius: 10px;")
        main_layout.addWidget(self.avatar, stretch=1)

        # State info
        self.state_label = QLabel("State: IDLE")
        self.state_label.setStyleSheet("font-size: 18px; padding: 10px;")
        self.state_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.state_label)

        # Controls
        controls_layout = QHBoxLayout()

        # State buttons
        states_group = QGroupBox("Expression States")
        states_layout = QVBoxLayout()

        states = [
            ("💤 Idle", AvatarState.IDLE, "#64C8FF"),
            ("🤔 Thinking", AvatarState.THINKING, "#FFD700"),
            ("🎸 Jamming", AvatarState.JAMMING, "#FF69B4"),
            ("👁️ Learning", AvatarState.LEARNING, "#9370DB"),
            ("🔒 Locked", AvatarState.LOCKED, "#FF6347"),
            ("😊 Happy", AvatarState.HAPPY, "#00FF00"),
            ("❌ Error", AvatarState.ERROR, "#FF0000"),
            ("😴 Sleeping", AvatarState.SLEEPING, "#708090"),
        ]

        for name, state, color in states:
            btn = QPushButton(name)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    padding: 10px;
                    border-radius: 5px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {color}aa;
                }}
            """)
            btn.clicked.connect(lambda checked, s=state, n=name, c=color:
                               self._change_state(s, n, c))
            states_layout.addWidget(btn)

        states_group.setLayout(states_layout)
        controls_layout.addWidget(states_group)

        # Color control
        color_group = QGroupBox("Avatar Color")
        color_layout = QVBoxLayout()

        colors = [
            ("Blue", QColor(100, 200, 255)),
            ("Purple", QColor(147, 112, 219)),
            ("Pink", QColor(255, 105, 180)),
            ("Green", QColor(50, 205, 50)),
            ("Orange", QColor(255, 140, 0)),
            ("Cyan", QColor(0, 255, 255)),
        ]

        for name, color in colors:
            btn = QPushButton(name)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color.name()};
                    color: white;
                    border: none;
                    padding: 8px;
                    border-radius: 5px;
                }}
            """)
            btn.clicked.connect(lambda checked, c=color: self.avatar.set_color(c))
            color_layout.addWidget(btn)

        color_group.setLayout(color_layout)
        controls_layout.addWidget(color_group)

        # Animation info
        info_group = QGroupBox("Features")
        info_layout = QVBoxLayout()
        info_text = """
        <b>Animated Features:</b><br>
        • Eyes blink automatically<br>
        • Pupils follow mouse<br>
        • Eyebrows show emotion<br>
        • Each state has unique animation<br><br>

        <b>Try this:</b><br>
        • Move mouse over avatar<br>
        • Watch the pupils track!<br>
        • See different expressions<br>
        • Notice eyebrow movements
        """
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        info_layout.addWidget(info_label)

        # Auto-cycle button
        self.auto_btn = QPushButton("▶️ Auto-Cycle States")
        self.auto_btn.setCheckable(True)
        self.auto_btn.toggled.connect(self._toggle_auto_cycle)
        info_layout.addWidget(self.auto_btn)

        info_group.setLayout(info_layout)
        controls_layout.addWidget(info_group)

        main_layout.addLayout(controls_layout)

        # Auto-cycle timer
        self.cycle_timer = QTimer()
        self.cycle_timer.timeout.connect(self._cycle_state)
        self.current_state_index = 0
        self.states_list = [s[1] for s in states]

    def _change_state(self, state: AvatarState, name: str, color: str):
        """Change avatar state"""
        self.avatar.set_state(state)
        self.state_label.setText(f"State: {name}")
        self.state_label.setStyleSheet(f"""
            font-size: 18px;
            padding: 10px;
            background-color: {color}40;
            border-radius: 5px;
        """)

    def _toggle_auto_cycle(self, checked: bool):
        """Toggle automatic state cycling"""
        if checked:
            self.auto_btn.setText("⏸️ Stop Auto-Cycle")
            self.cycle_timer.start(2000)  # Change every 2 seconds
        else:
            self.auto_btn.setText("▶️ Auto-Cycle States")
            self.cycle_timer.stop()

    def _cycle_state(self):
        """Cycle to next state"""
        self.current_state_index = (self.current_state_index + 1) % len(self.states_list)
        state = self.states_list[self.current_state_index]
        self.avatar.set_state(state)
        self.state_label.setText(f"State: {state.value.upper()} (Auto-cycling...)")


def main():
    app = QApplication(sys.argv)

    # Set application style
    app.setStyle("Fusion")

    window = AvatarDemo()
    window.show()

    print("🎵 Bass Clef Avatar Demo")
    print("=" * 50)
    print("Features:")
    print("  • Animated eyes that blink")
    print("  • Pupils that follow your mouse")
    print("  • Expressive eyebrows")
    print("  • 8 different emotional states")
    print("  • Customizable colors")
    print()
    print("Try:")
    print("  1. Move mouse over the avatar")
    print("  2. Click different expression states")
    print("  3. Change the avatar color")
    print("  4. Enable auto-cycle to see all states")
    print("=" * 50)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
