"""
Enhanced Bass Clef Widget - Avatar with stunning visual effects

This is an enhanced version of bass_clef_widget.py that integrates:
- Particle effects (musical notes, glows, trails)
- Smooth state transitions
- Theme support
- 60 FPS animations
- Performance optimization

To use this version, replace imports in transparent_window.py:
  from daiw.gui.bass_clef_widget_enhanced import BassClefWidget, AvatarState
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
import time

# Import our new visual enhancement systems
from daiw.gui.effects import EffectsManager
from daiw.gui.animations import StateTransitionAnimator
from daiw.gui.themes import get_theme_manager


class AvatarState(Enum):
    """Avatar states with different visual representations"""
    IDLE = "idle"
    LISTENING = "listening"
    PLAYING = "playing"
    THINKING = "thinking"
    LOCKED = "locked"


class BassClefWidget(QWidget):
    """
    Enhanced bass clef avatar with stunning visual effects:
    - Particle systems (musical notes, matrix rain, spirals)
    - Glowing effects with pulsing
    - Smooth state transitions
    - Trail effects when dragging
    - Theme support
    - 60 FPS performance
    """

    # Signals
    state_changed = pyqtSignal(AvatarState)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        # State
        self._state = AvatarState.IDLE
        self._animation_phase = 0.0
        self._blink_timer = 0

        # Visual enhancement systems
        self.effects_manager = EffectsManager()
        self.state_animator = StateTransitionAnimator()
        self.theme_manager = get_theme_manager()

        # Current theme
        self.theme = self.theme_manager.get_current_theme()

        # Listen for theme changes
        self.theme_manager.theme_changed.connect(self._on_theme_changed)

        # Colors from theme
        self._current_color = self.theme.get_mode_color(self._state.value)

        # Performance monitoring
        self.last_frame_time = time.time()
        self.frame_times = []
        self.fps = 60.0

        # Settings
        self.effects_enabled = True
        self.show_fps = False  # Debug: show FPS counter

        # Animation timer - 60 FPS
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_animation)
        self._timer.start(16)  # ~60 FPS (16ms)

        # Widget properties
        self.setMinimumSize(200, 150)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Initialize effects for current state
        center = QPointF(self.width() / 2, self.height() / 2)
        self.effects_manager.set_mode(self._state.value, self._current_color, center)

    def set_state(self, state: AvatarState) -> None:
        """Set the avatar state with smooth transition"""
        if self._state != state:
            old_state = self._state
            self._state = state

            # Get new color from theme
            new_color = self.theme.get_mode_color(state.value)

            # Smooth color transition
            self.state_animator.transition_to_state(
                state.value,
                new_color,
                callback=self._on_state_transition_complete
            )

            # Configure effects for new mode
            center = QPointF(self.width() / 2, self.height() / 2)
            self.effects_manager.set_mode(state.value, new_color, center)

            # Emit particle burst on state change
            if self.effects_enabled:
                self.effects_manager.emit_burst(center, new_color, count=30)

            # Emit signal
            self.state_changed.emit(state)

    def get_state(self) -> AvatarState:
        """Get current avatar state"""
        return self._state

    def toggle_effects(self, enabled: bool):
        """Enable or disable visual effects"""
        self.effects_enabled = enabled
        self.effects_manager.effects_enabled = enabled

    def set_theme(self, theme_name: str):
        """Change visual theme"""
        self.theme_manager.set_theme(theme_name)

    def _on_theme_changed(self, new_theme):
        """Handle theme change"""
        self.theme = new_theme
        self._current_color = self.theme.get_mode_color(self._state.value)

        # Update effects with new color
        center = QPointF(self.width() / 2, self.height() / 2)
        self.effects_manager.set_mode(self._state.value, self._current_color, center)

        self.update()

    def _on_state_transition_complete(self):
        """Called when state transition animation completes"""
        # Update current color from animator
        self._current_color = self.state_animator.get_current_color()

    def _update_animation(self) -> None:
        """Update animation at 60 FPS"""
        # Calculate delta time
        current_time = time.time()
        dt = current_time - self.last_frame_time
        self.last_frame_time = current_time

        # Track FPS
        self.frame_times.append(dt)
        if len(self.frame_times) > 60:
            self.frame_times.pop(0)
        self.fps = 1.0 / (sum(self.frame_times) / len(self.frame_times)) if self.frame_times else 60.0

        # Enable performance mode if FPS drops
        if self.fps < 30:
            self.effects_manager.performance_mode = True
        elif self.fps > 50:
            self.effects_manager.performance_mode = False

        # Update animation phase
        self._animation_phase += dt * 6.28  # 2π per second

        # Periodic blink
        self._blink_timer += 1
        if self._blink_timer > 180:  # Blink every ~3 seconds at 60fps
            self._blink_timer = 0

        # Update effects
        width = self.width()
        height = self.height()
        center = QPointF(width / 2, height / 2)

        if self.effects_enabled:
            self.effects_manager.update(dt, width, height, center, self._state.value)

        # Update current color from transition
        self._current_color = self.state_animator.get_current_color()

        self.update()

    def paintEvent(self, event) -> None:
        """Paint the enhanced bass clef avatar"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Get widget dimensions
        width = self.width()
        height = self.height()
        center_x = width / 2
        center_y = height / 2
        center = QPointF(center_x, center_y)

        # Scale factor
        scale = min(width / 200, height / 150)

        # Draw effects BEHIND avatar (glow, trails, etc.)
        if self.effects_enabled:
            self.effects_manager.draw(painter, center, radius=80 * scale)

        # Save painter state
        painter.save()

        # Translate to center and apply scale
        painter.translate(center_x, center_y)
        painter.scale(scale, scale)

        # Draw bass clef with current transition color
        self._draw_bass_clef(painter)

        # Draw eyes
        self._draw_eyes(painter)

        # Draw lock icon if locked
        if self._state == AvatarState.LOCKED:
            self._draw_lock_icon(painter)

        # Restore painter state
        painter.restore()

        # Draw FPS counter (debug)
        if self.show_fps:
            painter.setPen(QColor(255, 255, 255))
            painter.drawText(10, 20, f"FPS: {self.fps:.1f}")
            if self.effects_manager.performance_mode:
                painter.drawText(10, 40, "PERF MODE")

    def _draw_bass_clef(self, painter: QPainter) -> None:
        """Draw the bass clef symbol with smooth color transitions"""
        # Use current transition color
        color = self._current_color

        # Animation effects based on state
        if self._state == AvatarState.PLAYING:
            # Vibrate to the beat
            offset = math.sin(self._animation_phase * 3) * 2
            painter.translate(offset, 0)
        elif self._state == AvatarState.THINKING:
            # Gentle pulsing
            pulse = 1.0 + math.sin(self._animation_phase) * 0.05
            painter.scale(pulse, pulse)
        elif self._state == AvatarState.LOCKED:
            # Subtle rotation
            rotation = math.sin(self._animation_phase * 0.5) * 2
            painter.rotate(rotation)

        # Draw the curved body of the bass clef
        path = QPainterPath()

        # Start point
        path.moveTo(-80, -30)

        # Create the characteristic bass clef curve
        path.cubicTo(-80, -50, -40, -60, 0, -50)
        path.cubicTo(40, -40, 60, -20, 60, 0)
        path.cubicTo(60, 20, 40, 35, 0, 35)
        path.cubicTo(-20, 35, -35, 30, -45, 20)
        path.cubicTo(-55, 10, -55, -5, -45, -15)
        path.cubicTo(-35, -25, -15, -25, 0, -20)
        path.cubicTo(-10, -20, -20, -15, -25, -5)
        path.cubicTo(-28, 0, -28, 5, -25, 10)
        path.cubicTo(-20, 18, -10, 20, 0, 18)

        # Enhanced gradient with current color
        gradient = QRadialGradient(0, 0, 80)
        gradient.setColorAt(0, color.lighter(130))
        gradient.setColorAt(0.5, color)
        gradient.setColorAt(1, color.darker(110))

        # Draw with enhanced styling
        painter.setPen(QPen(color.darker(140), 3, Qt.PenStyle.SolidLine,
                           Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        painter.setBrush(QBrush(gradient))
        painter.drawPath(path)

    def _draw_eyes(self, painter: QPainter) -> None:
        """Draw the two dots of the bass clef as eyes"""
        color = self._current_color

        # The two dots
        dot_y_offset = 5
        dot_x = 70

        # Blinking animation
        is_blinking = self._blink_timer < 5

        if not is_blinking:
            # Upper dot
            self._draw_eye(painter, dot_x, -15 + dot_y_offset, color)

            # Lower dot
            self._draw_eye(painter, dot_x, 15 + dot_y_offset, color)

            # State-specific effects
            if self._state == AvatarState.LISTENING:
                # Listening waves already drawn by effects system
                pass
        else:
            # Closed eyes
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

    def _draw_lock_icon(self, painter: QPainter) -> None:
        """Draw a lock icon with glow"""
        lock_color = self._current_color

        # Lock body with glow
        glow_gradient = QRadialGradient(0, 52, 20)
        glow_gradient.setColorAt(0, lock_color.lighter(120))
        glow_gradient.setColorAt(1, QColor(lock_color.red(), lock_color.green(), lock_color.blue(), 0))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(glow_gradient))
        painter.drawEllipse(QPointF(0, 52), 20, 20)

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

    def add_trail_point(self, point: QPointF):
        """Add point to motion trail (called when dragging)"""
        if self.effects_enabled:
            self.effects_manager.trail_effect.add_point(point)

    def clear_trail(self):
        """Clear motion trail"""
        if self.effects_enabled:
            self.effects_manager.trail_effect.clear()
