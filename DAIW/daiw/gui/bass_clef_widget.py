"""
Bass Clef Widget - Exact match to user's design
Based on the uploaded bass clef face image
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QPointF, QRectF, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QPainterPath, QRadialGradient
from enum import Enum
import math
import random


class AvatarState(Enum):
    """Avatar states with different expressions"""
    IDLE = "idle"
    THINKING = "thinking"
    JAMMING = "jamming"
    LEARNING = "learning"
    LOCKED = "locked"
    HAPPY = "happy"
    ERROR = "error"
    SLEEPING = "sleeping"


class BassClefWidget(QWidget):
    """
    Bass clef avatar matching the exact uploaded design
    - Two curved eyebrows
    - Two circular eyes (bass clef dots)
    - Large bass clef curve body
    """

    state_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(200, 200)

        # Avatar state
        self.state = AvatarState.IDLE
        self.color = QColor(60, 60, 60)  # Dark gray like image

        # Eye animation
        self.blink_timer = 0
        self.next_blink = random.randint(120, 240)
        self.eyes_closed = False

        # Eyebrow animation
        self.left_brow_offset = 0
        self.right_brow_offset = 0
        self.brow_angle = 0

        # Pupil tracking
        self.pupil_x = 0
        self.pupil_y = 0
        self.target_pupil_x = 0
        self.target_pupil_y = 0

        # Animation timer (60 FPS)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._animate)
        self.timer.start(16)

        # Expression configs
        self.expressions = {
            AvatarState.IDLE: {'brow_y': 0, 'brow_angle': 0, 'eye_open': 1.0},
            AvatarState.THINKING: {'brow_y': -8, 'brow_angle': 5, 'eye_open': 1.1},
            AvatarState.JAMMING: {'brow_y': -15, 'brow_angle': 10, 'eye_open': 1.3},
            AvatarState.LEARNING: {'brow_y': 3, 'brow_angle': -3, 'eye_open': 0.9},
            AvatarState.LOCKED: {'brow_y': 8, 'brow_angle': -8, 'eye_open': 0.85},
            AvatarState.HAPPY: {'brow_y': -12, 'brow_angle': 8, 'eye_open': 1.2},
            AvatarState.ERROR: {'brow_y': 0, 'brow_angle': 0, 'eye_open': 1.0},  # Asymmetric
            AvatarState.SLEEPING: {'brow_y': 5, 'brow_angle': 0, 'eye_open': 0.0},
        }

        self.current_eye_open = 1.0
        self.setMouseTracking(True)

    def set_state(self, state: AvatarState):
        """Change avatar expression"""
        if self.state != state:
            self.state = state
            self.state_changed.emit(state.value)

    def set_color(self, color: QColor):
        """Change avatar color"""
        self.color = color
        self.update()

    def _animate(self):
        """Animation loop"""
        # Blink
        self.blink_timer += 1
        if self.blink_timer >= self.next_blink:
            self.eyes_closed = True
            self.blink_timer = 0
            self.next_blink = random.randint(120, 240)
        elif self.eyes_closed and self.blink_timer > 5:
            self.eyes_closed = False

        # Smooth pupil tracking
        self.pupil_x += (self.target_pupil_x - self.pupil_x) * 0.15
        self.pupil_y += (self.target_pupil_y - self.pupil_y) * 0.15

        # State-based expression
        expr = self.expressions.get(self.state, self.expressions[AvatarState.IDLE])

        if self.state == AvatarState.THINKING:
            # Wave eyebrows
            wave = math.sin(self.blink_timer * 0.05) * 3
            self.left_brow_offset = expr['brow_y'] + wave
            self.right_brow_offset = expr['brow_y'] - wave
        elif self.state == AvatarState.JAMMING:
            # Bounce eyebrows
            bounce = abs(math.sin(self.blink_timer * 0.12)) * 8
            self.left_brow_offset = expr['brow_y'] - bounce
            self.right_brow_offset = expr['brow_y'] - bounce
        elif self.state == AvatarState.ERROR:
            # Asymmetric confusion
            self.left_brow_offset = -10
            self.right_brow_offset = 5
        else:
            self.left_brow_offset = expr['brow_y']
            self.right_brow_offset = expr['brow_y']

        self.brow_angle = expr['brow_angle']
        self.current_eye_open = expr['eye_open'] if not self.eyes_closed else 0.0

        self.update()

    def mouseMoveEvent(self, event):
        """Track mouse for pupil movement"""
        center = self.rect().center()
        dx = event.pos().x() - center.x()
        dy = event.pos().y() - center.y()

        # Limit range
        distance = math.sqrt(dx*dx + dy*dy)
        max_offset = 4
        if distance > 80:
            self.target_pupil_x = (dx / distance) * max_offset
            self.target_pupil_y = (dy / distance) * max_offset
        else:
            self.target_pupil_x = (dx / 80) * max_offset
            self.target_pupil_y = (dy / 80) * max_offset

    def paintEvent(self, event):
        """Draw the bass clef avatar exactly as in the image"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Get dimensions
        width = self.width()
        height = self.height()
        size = min(width, height)

        # Center
        painter.translate(width / 2, height / 2)

        # Scale to fit
        scale = size / 300
        painter.scale(scale, scale)

        # Draw bass clef body (main curve) - matching image
        self._draw_bass_clef_body(painter)

        # Draw eyebrows
        self._draw_eyebrow(painter, -50, -80 + self.left_brow_offset, "left")
        self._draw_eyebrow(painter, 30, -80 + self.right_brow_offset, "right")

        # Draw eyes
        self._draw_eye(painter, -50, -45)  # Left eye
        self._draw_eye(painter, 30, -45)   # Right eye

    def _draw_bass_clef_body(self, painter):
        """Draw the main bass clef curve matching the uploaded image"""
        path = QPainterPath()

        # Start at top
        path.moveTo(10, -60)

        # Upper curve (going left and down)
        path.cubicTo(
            -15, -55,   # Control 1
            -35, -35,   # Control 2
            -30, 0      # End
        )

        # Middle section (going down and right)
        path.cubicTo(
            -25, 35,    # Control 1
            -10, 70,    # Control 2
            15, 90      # End
        )

        # Lower curve (the swirl)
        path.cubicTo(
            40, 110,    # Control 1
            75, 100,    # Control 2
            85, 70      # End
        )

        # Curve back
        path.cubicTo(
            95, 40,     # Control 1
            85, 10,     # Control 2
            60, 0       # End
        )

        # Inner swirl
        path.cubicTo(
            35, -10,    # Control 1
            20, 0,      # Control 2
            15, 20      # End
        )

        path.cubicTo(
            10, 40,     # Control 1
            20, 55,     # Control 2
            40, 55      # End
        )

        path.cubicTo(
            60, 55,     # Control 1
            68, 40,     # Control 2
            62, 25      # End
        )

        # Draw with thick pen
        pen = QPen(self.color, 12)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)

    def _draw_eyebrow(self, painter, x, y, side):
        """Draw curved eyebrow matching image"""
        painter.save()
        painter.translate(x, y)
        painter.rotate(self.brow_angle if side == "left" else -self.brow_angle)

        path = QPainterPath()

        if side == "left":
            # Left eyebrow - curves down on left
            path.moveTo(-20, 5)
            path.cubicTo(
                -12, -5,
                -4, -8,
                4, -6
            )
            path.cubicTo(
                12, -4,
                20, 0,
                25, 5
            )
        else:
            # Right eyebrow - curves down on right
            path.moveTo(-25, 5)
            path.cubicTo(
                -20, 0,
                -12, -4,
                -4, -6
            )
            path.cubicTo(
                4, -8,
                12, -5,
                20, 5
            )

        pen = QPen(self.color, 6)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawPath(path)

        painter.restore()

    def _draw_eye(self, painter, x, y):
        """Draw eye (bass clef dot) with pupil"""
        painter.save()
        painter.translate(x, y)

        if self.current_eye_open < 0.1:
            # Draw closed eye
            pen = QPen(self.color, 4)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawLine(-15, 0, 15, 0)
        else:
            # Eye size based on expression
            eye_radius = 18 * self.current_eye_open

            # White of eye
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(255, 255, 255))
            painter.drawEllipse(QPointF(0, 0), eye_radius, eye_radius)

            # Pupil (dark)
            pupil_radius = eye_radius * 0.6
            gradient = QRadialGradient(self.pupil_x, self.pupil_y, pupil_radius)
            gradient.setColorAt(0, QColor(40, 40, 40))
            gradient.setColorAt(1, QColor(20, 20, 20))

            painter.setBrush(gradient)
            painter.drawEllipse(
                QPointF(self.pupil_x, self.pupil_y),
                pupil_radius,
                pupil_radius
            )

            # Highlight
            painter.setBrush(QColor(255, 255, 255, 200))
            highlight_size = pupil_radius * 0.35
            painter.drawEllipse(
                QPointF(self.pupil_x - pupil_radius*0.3, self.pupil_y - pupil_radius*0.3),
                highlight_size,
                highlight_size
            )

        painter.restore()


# Test
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton

    app = QApplication(sys.argv)

    window = QWidget()
    window.setWindowTitle("Bass Clef Avatar - Exact Design")
    window.resize(500, 600)

    layout = QVBoxLayout()

    avatar = BassClefWidget()
    layout.addWidget(avatar, stretch=1)

    # State buttons
    for name, state in [
        ("Idle", AvatarState.IDLE),
        ("Thinking", AvatarState.THINKING),
        ("Jamming", AvatarState.JAMMING),
        ("Learning", AvatarState.LEARNING),
        ("Locked", AvatarState.LOCKED),
        ("Happy", AvatarState.HAPPY),
        ("Error", AvatarState.ERROR),
        ("Sleeping", AvatarState.SLEEPING),
    ]:
        btn = QPushButton(name)
        btn.clicked.connect(lambda checked, s=state: avatar.set_state(s))
        layout.addWidget(btn)

    window.setLayout(layout)
    window.show()

    sys.exit(app.exec())
