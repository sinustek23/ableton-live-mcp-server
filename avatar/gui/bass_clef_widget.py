"""
Bass Clef Widget - Der Avatar als liegender Bassschlüssel

Der Bassschlüssel (F-Schlüssel) wird horizontal gedreht dargestellt.
Die zwei Punkte dienen als Augen, die Welle als Körper/Mund.
"""

from typing import Optional
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QPointF, QRectF, QTimer, pyqtSignal
from PyQt6.QtGui import (
    QPainter,
    QPainterPath,
    QColor,
    QPen,
    QBrush,
    QRadialGradient
)
from enum import Enum
import math


class AvatarState(Enum):
    """Avatar states with different visual representations"""
    IDLE = "idle"
    LISTENING = "listening"
    PLAYING = "playing"
    THINKING = "thinking"
    LOCKED = "locked"


class BassClefWidget(QWidget):
    """
    Custom widget displaying a bass clef symbol as an animated avatar
    """

    # Signals
    state_changed = pyqtSignal(AvatarState)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        # State
        self._state = AvatarState.IDLE
        self._animation_phase = 0.0
        self._blink_timer = 0

        # Colors for different states
        self._state_colors = {
            AvatarState.IDLE: QColor(100, 150, 255, 200),  # Blue
            AvatarState.LISTENING: QColor(100, 255, 150, 200),  # Green
            AvatarState.PLAYING: QColor(255, 100, 150, 200),  # Pink/Red
            AvatarState.THINKING: QColor(200, 100, 255, 200),  # Purple
            AvatarState.LOCKED: QColor(255, 200, 50, 200),  # Gold
        }

        # Animation timer
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_animation)
        self._timer.start(50)  # 20 FPS

        # Widget properties
        self.setMinimumSize(200, 150)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def set_state(self, state: AvatarState) -> None:
        """Set the avatar state"""
        if self._state != state:
            self._state = state
            self.state_changed.emit(state)
            self.update()

    def get_state(self) -> AvatarState:
        """Get current avatar state"""
        return self._state

    def _update_animation(self) -> None:
        """Update animation phase"""
        self._animation_phase += 0.1

        # Periodic blink
        self._blink_timer += 1
        if self._blink_timer > 60:  # Blink every ~3 seconds
            self._blink_timer = 0

        self.update()

    def paintEvent(self, event) -> None:
        """Paint the bass clef avatar"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Get widget dimensions
        width = self.width()
        height = self.height()
        center_x = width / 2
        center_y = height / 2

        # Scale factor
        scale = min(width / 200, height / 150)

        # Save painter state
        painter.save()

        # Translate to center and apply scale
        painter.translate(center_x, center_y)
        painter.scale(scale, scale)

        # Draw bass clef
        self._draw_bass_clef(painter)

        # Draw eyes (the two dots of the bass clef)
        self._draw_eyes(painter)

        # Draw lock icon if locked
        if self._state == AvatarState.LOCKED:
            self._draw_lock_icon(painter)

        # Restore painter state
        painter.restore()

    def _draw_bass_clef(self, painter: QPainter) -> None:
        """Draw the bass clef symbol (F-clef) rotated horizontally"""
        color = self._state_colors[self._state]

        # Animation effects based on state
        if self._state == AvatarState.PLAYING:
            # Vibrate to the beat
            offset = math.sin(self._animation_phase * 3) * 2
            painter.translate(offset, 0)
        elif self._state == AvatarState.THINKING:
            # Gentle pulsing
            pulse = 1.0 + math.sin(self._animation_phase) * 0.05
            painter.scale(pulse, pulse)

        # Draw the curved body of the bass clef
        path = QPainterPath()

        # Start point (top left of the curve)
        path.moveTo(-80, -30)

        # Create the characteristic bass clef curve
        # Upper curve (like a backward C)
        path.cubicTo(-80, -50, -40, -60, 0, -50)
        path.cubicTo(40, -40, 60, -20, 60, 0)

        # Middle part
        path.cubicTo(60, 20, 40, 35, 0, 35)
        path.cubicTo(-20, 35, -35, 30, -45, 20)

        # Lower spiral
        path.cubicTo(-55, 10, -55, -5, -45, -15)
        path.cubicTo(-35, -25, -15, -25, 0, -20)

        # Inner curve back
        path.cubicTo(-10, -20, -20, -15, -25, -5)
        path.cubicTo(-28, 0, -28, 5, -25, 10)
        path.cubicTo(-20, 18, -10, 20, 0, 18)

        # Gradient for depth
        gradient = QRadialGradient(0, 0, 80)
        gradient.setColorAt(0, color.lighter(120))
        gradient.setColorAt(1, color)

        # Draw the path
        painter.setPen(QPen(color.darker(120), 3, Qt.PenStyle.SolidLine,
                           Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        painter.setBrush(QBrush(gradient))
        painter.drawPath(path)

    def _draw_eyes(self, painter: QPainter) -> None:
        """Draw the two dots of the bass clef as eyes"""
        color = self._state_colors[self._state]

        # The two dots are positioned to the right of the bass clef curve
        dot_y_offset = 5
        dot_x = 70

        # Blinking animation
        is_blinking = self._blink_timer < 3

        if not is_blinking:
            # Upper dot (left eye)
            self._draw_eye(painter, dot_x, -15 + dot_y_offset, color)

            # Lower dot (right eye)
            self._draw_eye(painter, dot_x, 15 + dot_y_offset, color)

            # Animated effects
            if self._state == AvatarState.LISTENING:
                # Draw "listening waves" from the ear
                self._draw_listening_waves(painter, dot_x + 20, 0)
        else:
            # Draw closed eyes (horizontal lines)
            painter.setPen(QPen(color.darker(130), 2))
            painter.drawLine(int(dot_x - 5), int(-15 + dot_y_offset),
                           int(dot_x + 5), int(-15 + dot_y_offset))
            painter.drawLine(int(dot_x - 5), int(15 + dot_y_offset),
                           int(dot_x + 5), int(15 + dot_y_offset))

    def _draw_eye(self, painter: QPainter, x: float, y: float, color: QColor) -> None:
        """Draw a single eye with gradient"""
        gradient = QRadialGradient(x, y, 8)
        gradient.setColorAt(0, color.lighter(150))
        gradient.setColorAt(0.5, color)
        gradient.setColorAt(1, color.darker(120))

        painter.setPen(QPen(color.darker(140), 1))
        painter.setBrush(QBrush(gradient))
        painter.drawEllipse(QPointF(x, y), 8, 8)

        # Pupil
        painter.setBrush(QBrush(QColor(20, 20, 40, 200)))
        painter.drawEllipse(QPointF(x + 1, y), 3, 3)

        # Highlight
        painter.setBrush(QBrush(QColor(255, 255, 255, 150)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(x - 2, y - 2), 2, 2)

    def _draw_listening_waves(self, painter: QPainter, x: float, y: float) -> None:
        """Draw animated listening waves"""
        color = self._state_colors[AvatarState.LISTENING]

        for i in range(3):
            alpha = int(255 * (1 - (self._animation_phase % 1)))
            wave_color = QColor(color.red(), color.green(), color.blue(), alpha // (i + 1))

            painter.setPen(QPen(wave_color, 2))
            radius = 10 + i * 8 + (self._animation_phase % 1) * 10
            painter.drawArc(int(x - radius), int(y - radius),
                          int(radius * 2), int(radius * 2),
                          -30 * 16, 60 * 16)

    def _draw_lock_icon(self, painter: QPainter) -> None:
        """Draw a lock icon when in locked mode"""
        lock_color = QColor(255, 215, 0, 220)  # Gold

        # Lock body
        painter.setPen(QPen(lock_color.darker(120), 2))
        painter.setBrush(QBrush(lock_color))
        painter.drawRoundedRect(QRectF(-15, 40, 30, 25), 3, 3)

        # Lock shackle
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawArc(int(-12), int(30), 24, 20, 0, 180 * 16)

        # Keyhole
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(0, 0, 0, 150)))
        painter.drawEllipse(QPointF(0, 50), 3, 3)
        painter.drawRect(QRectF(-1, 52, 2, 6))
