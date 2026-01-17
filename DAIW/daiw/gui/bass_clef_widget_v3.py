"""
Bass Clef Widget with Animated Eyes and Eyebrows
Uses the bass clef symbol as a face with expressive features
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QPointF, QRectF, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QPainterPath, QRadialGradient
from enum import Enum
import math
import random


class AvatarState(Enum):
    """Avatar states with different expressions"""
    IDLE = "idle"           # Calm, neutral
    THINKING = "thinking"   # Curious, eyebrows raised
    JAMMING = "jamming"     # Excited, wide eyes
    LEARNING = "learning"   # Focused, slight squint
    LOCKED = "locked"       # Intense, furrowed brows
    HAPPY = "happy"         # Joyful, raised brows
    ERROR = "error"         # Confused, asymmetric brows
    SLEEPING = "sleeping"   # Closed eyes


class EyeExpression:
    """Eye animation parameters"""
    def __init__(self, size=1.0, y_offset=0, blink_speed=1.0, pupil_size=0.6):
        self.size = size              # Eye size multiplier
        self.y_offset = y_offset      # Vertical offset
        self.blink_speed = blink_speed
        self.pupil_size = pupil_size  # Pupil size relative to eye
        self.is_closed = False


class BrowExpression:
    """Eyebrow animation parameters"""
    def __init__(self, angle=0, y_offset=0, curve=1.0):
        self.angle = angle        # Rotation angle in degrees
        self.y_offset = y_offset  # Vertical offset
        self.curve = curve        # Curvature amount


class BassClefWidget(QWidget):
    """
    Animated bass clef avatar with expressive eyes and eyebrows
    The bass clef symbol naturally forms a face:
    - Two dots = eyes
    - Curved lines above = eyebrows
    - Main curve = body
    """

    state_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(200, 200)

        # Avatar state
        self.state = AvatarState.IDLE
        self.color = QColor(100, 200, 255)  # Default blue

        # Eye animation
        self.left_eye = EyeExpression()
        self.right_eye = EyeExpression()
        self.blink_timer = 0
        self.next_blink = random.randint(120, 240)  # Random blink interval

        # Eyebrow animation
        self.left_brow = BrowExpression()
        self.right_brow = BrowExpression()

        # Pupil tracking (follows mouse)
        self.pupil_offset_x = 0
        self.pupil_offset_y = 0
        self.target_pupil_x = 0
        self.target_pupil_y = 0

        # Animation timer
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self._update_animation)
        self.animation_timer.start(16)  # ~60 FPS

        # Expression parameters by state
        self.state_expressions = {
            AvatarState.IDLE: {
                'eye_size': 1.0,
                'brow_angle': 0,
                'brow_y': 0,
                'pupil_size': 0.6,
                'blink_speed': 1.0
            },
            AvatarState.THINKING: {
                'eye_size': 1.1,
                'brow_angle': 15,  # Raised
                'brow_y': -5,
                'pupil_size': 0.7,
                'blink_speed': 0.8
            },
            AvatarState.JAMMING: {
                'eye_size': 1.3,   # Wide eyes
                'brow_angle': 20,
                'brow_y': -8,
                'pupil_size': 0.5,
                'blink_speed': 0.5  # Fast blinking
            },
            AvatarState.LEARNING: {
                'eye_size': 0.9,   # Slight squint
                'brow_angle': -5,  # Slightly furrowed
                'brow_y': 2,
                'pupil_size': 0.8,
                'blink_speed': 1.2
            },
            AvatarState.LOCKED: {
                'eye_size': 0.85,
                'brow_angle': -15,  # Furrowed
                'brow_y': 5,
                'pupil_size': 0.4,
                'blink_speed': 1.5
            },
            AvatarState.HAPPY: {
                'eye_size': 1.2,
                'brow_angle': 25,  # Very raised
                'brow_y': -10,
                'pupil_size': 0.7,
                'blink_speed': 0.7
            },
            AvatarState.ERROR: {
                'eye_size': 1.0,
                'brow_angle': 0,   # Will be asymmetric
                'brow_y': 0,
                'pupil_size': 0.6,
                'blink_speed': 0.3  # Rapid blinking
            },
            AvatarState.SLEEPING: {
                'eye_size': 0.1,   # Nearly closed
                'brow_angle': 0,
                'brow_y': 5,
                'pupil_size': 0.0,
                'blink_speed': 3.0  # Slow
            },
        }

    def set_state(self, state: AvatarState):
        """Change avatar state and expression"""
        if self.state != state:
            self.state = state
            self._apply_expression()
            self.state_changed.emit(state.value)
            self.update()

    def set_color(self, color: QColor):
        """Change avatar color"""
        self.color = color
        self.update()

    def _apply_expression(self):
        """Apply expression parameters based on current state"""
        expr = self.state_expressions.get(self.state, self.state_expressions[AvatarState.IDLE])

        # Apply to eyes
        self.left_eye.size = expr['eye_size']
        self.right_eye.size = expr['eye_size']
        self.left_eye.pupil_size = expr['pupil_size']
        self.right_eye.pupil_size = expr['pupil_size']
        self.left_eye.blink_speed = expr['blink_speed']
        self.right_eye.blink_speed = expr['blink_speed']

        # Apply to eyebrows
        if self.state == AvatarState.ERROR:
            # Asymmetric for confusion
            self.left_brow.angle = 15
            self.left_brow.y_offset = -5
            self.right_brow.angle = -10
            self.right_brow.y_offset = 3
        else:
            self.left_brow.angle = expr['brow_angle']
            self.left_brow.y_offset = expr['brow_y']
            self.right_brow.angle = expr['brow_angle']
            self.right_brow.y_offset = expr['brow_y']

    def _update_animation(self):
        """Update animation frame"""
        # Blink animation
        self.blink_timer += 1

        if self.blink_timer >= self.next_blink:
            # Trigger blink
            self.left_eye.is_closed = True
            self.right_eye.is_closed = True
            self.blink_timer = 0
            self.next_blink = random.randint(120, 240)
        elif self.left_eye.is_closed:
            # Open eyes after brief blink
            if self.blink_timer > 5:
                self.left_eye.is_closed = False
                self.right_eye.is_closed = False

        # Smooth pupil movement
        self.pupil_offset_x += (self.target_pupil_x - self.pupil_offset_x) * 0.1
        self.pupil_offset_y += (self.target_pupil_y - self.pupil_offset_y) * 0.1

        # State-specific animations
        if self.state == AvatarState.THINKING:
            # Slight eyebrow wave
            offset = math.sin(self.blink_timer * 0.05) * 2
            self.left_brow.y_offset = -5 + offset
            self.right_brow.y_offset = -5 - offset

        elif self.state == AvatarState.JAMMING:
            # Excited eyebrow bounce
            bounce = abs(math.sin(self.blink_timer * 0.15)) * 5
            self.left_brow.y_offset = -8 - bounce
            self.right_brow.y_offset = -8 - bounce

        elif self.state == AvatarState.SLEEPING:
            # Gentle breathing
            breath = math.sin(self.blink_timer * 0.03) * 1
            self.left_eye.y_offset = breath
            self.right_eye.y_offset = breath

        self.update()

    def mouseMoveEvent(self, event):
        """Track mouse for pupil following"""
        # Calculate pupil target based on mouse position
        center = self.rect().center()
        dx = event.pos().x() - center.x()
        dy = event.pos().y() - center.y()

        # Limit pupil movement
        max_offset = 3
        distance = math.sqrt(dx*dx + dy*dy)
        if distance > 100:
            scale = max_offset / 100
            self.target_pupil_x = dx * scale
            self.target_pupil_y = dy * scale
        else:
            self.target_pupil_x = dx * max_offset / 100
            self.target_pupil_y = dy * max_offset / 100

    def paintEvent(self, event):
        """Draw the bass clef avatar with animated features"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Center the drawing
        rect = self.rect()
        center_x = rect.width() / 2
        center_y = rect.height() / 2

        # Scale to fit widget
        scale = min(rect.width(), rect.height()) / 250

        painter.translate(center_x, center_y)
        painter.scale(scale, scale)

        # Draw bass clef body (main curve)
        self._draw_bass_clef_body(painter)

        # Draw eyebrows (curved lines above the dots)
        self._draw_eyebrow(painter, -35, -50, self.left_brow, "left")
        self._draw_eyebrow(painter, 15, -50, self.right_brow, "right")

        # Draw eyes (the two dots in bass clef)
        self._draw_eye(painter, -35, -25, self.left_eye)
        self._draw_eye(painter, 15, -25, self.right_eye)

    def _draw_bass_clef_body(self, painter):
        """Draw the main bass clef curve"""
        path = QPainterPath()

        # Main bass clef curve (simplified, stylized)
        # Starting from top, curving down and around
        path.moveTo(0, -70)

        # Upper curve
        path.cubicTo(
            -20, -60,   # Control point 1
            -30, -40,   # Control point 2
            -25, -10    # End point
        )

        # Middle curve (going down)
        path.cubicTo(
            -20, 20,    # Control point 1
            -10, 50,    # Control point 2
            0, 65       # End point
        )

        # Lower curve (swirl)
        path.cubicTo(
            10, 80,     # Control point 1
            30, 75,     # Control point 2
            35, 60      # End point
        )

        path.cubicTo(
            40, 45,     # Control point 1
            35, 30,     # Control point 2
            20, 25      # End point
        )

        path.cubicTo(
            5, 20,      # Control point 1
            -5, 25,     # Control point 2
            -8, 35      # End point
        )

        # Inner spiral
        path.cubicTo(
            -10, 42,    # Control point 1
            -5, 48,     # Control point 2
            5, 48       # End point
        )

        path.cubicTo(
            15, 48,     # Control point 1
            20, 42,     # Control point 2
            18, 35      # End point
        )

        # Draw with gradient for depth
        gradient = QRadialGradient(0, 0, 80)
        gradient.setColorAt(0, self.color.lighter(120))
        gradient.setColorAt(1, self.color)

        pen = QPen(self.color.darker(150), 8)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)

    def _draw_eyebrow(self, painter, x, y, brow: BrowExpression, side: str):
        """Draw animated eyebrow"""
        painter.save()
        painter.translate(x, y + brow.y_offset)
        painter.rotate(brow.angle)

        path = QPainterPath()

        # Curved eyebrow shape
        if side == "left":
            # Curve down on the left
            path.moveTo(-15, 0)
            path.cubicTo(
                -10, -3 * brow.curve,
                -5, -4 * brow.curve,
                0, -3 * brow.curve
            )
            path.cubicTo(
                5, -2 * brow.curve,
                10, 0,
                15, 0
            )
        else:
            # Curve down on the right
            path.moveTo(-15, 0)
            path.cubicTo(
                -10, -2 * brow.curve,
                -5, -2 * brow.curve,
                0, -3 * brow.curve
            )
            path.cubicTo(
                5, -4 * brow.curve,
                10, -3 * brow.curve,
                15, 0
            )

        pen = QPen(self.color.darker(130), 4)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawPath(path)

        painter.restore()

    def _draw_eye(self, painter, x, y, eye: EyeExpression):
        """Draw animated eye (bass clef dot)"""
        painter.save()
        painter.translate(x, y + eye.y_offset)

        if eye.is_closed or self.state == AvatarState.SLEEPING:
            # Draw closed eye (horizontal line)
            pen = QPen(self.color.darker(130), 3)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawLine(-10, 0, 10, 0)
        else:
            # Draw open eye
            eye_radius = 12 * eye.size

            # White of eye
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(255, 255, 255))
            painter.drawEllipse(QPointF(0, 0), eye_radius, eye_radius)

            # Pupil (with tracking)
            pupil_radius = eye_radius * eye.pupil_size
            pupil_x = self.pupil_offset_x
            pupil_y = self.pupil_offset_y

            # Gradient for depth
            gradient = QRadialGradient(pupil_x, pupil_y, pupil_radius)
            gradient.setColorAt(0, QColor(50, 50, 50))
            gradient.setColorAt(0.7, QColor(30, 30, 30))
            gradient.setColorAt(1, QColor(0, 0, 0))

            painter.setBrush(gradient)
            painter.drawEllipse(
                QPointF(pupil_x, pupil_y),
                pupil_radius,
                pupil_radius
            )

            # Highlight for liveliness
            painter.setBrush(QColor(255, 255, 255, 180))
            highlight_size = pupil_radius * 0.3
            painter.drawEllipse(
                QPointF(pupil_x - pupil_radius * 0.3, pupil_y - pupil_radius * 0.3),
                highlight_size,
                highlight_size
            )

        painter.restore()


# Convenience function for testing
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication, QVBoxLayout, QPushButton, QWidget

    app = QApplication(sys.argv)

    window = QWidget()
    window.setWindowTitle("Bass Clef Avatar Test")
    window.resize(400, 500)

    layout = QVBoxLayout()

    # Avatar widget
    avatar = BassClefWidget()
    layout.addWidget(avatar, stretch=1)

    # State buttons
    states = [
        ("Idle", AvatarState.IDLE),
        ("Thinking", AvatarState.THINKING),
        ("Jamming", AvatarState.JAMMING),
        ("Learning", AvatarState.LEARNING),
        ("Locked", AvatarState.LOCKED),
        ("Happy", AvatarState.HAPPY),
        ("Error", AvatarState.ERROR),
        ("Sleeping", AvatarState.SLEEPING),
    ]

    for name, state in states:
        btn = QPushButton(name)
        btn.clicked.connect(lambda checked, s=state: avatar.set_state(s))
        layout.addWidget(btn)

    window.setLayout(layout)
    window.show()

    sys.exit(app.exec())
