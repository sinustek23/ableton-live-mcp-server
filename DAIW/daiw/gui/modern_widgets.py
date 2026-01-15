"""
Modern Widgets - Glassmorphism and custom styled components

Provides modern UI components with glassmorphism effects, animated buttons,
custom cards, and other eye-candy widgets.
"""

from typing import Optional
from PyQt6.QtWidgets import (
    QPushButton,
    QLabel,
    QFrame,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGraphicsBlurEffect,
    QProgressBar
)
from PyQt6.QtCore import Qt, QRectF, QPropertyAnimation, QEasingCurve, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import (
    QPainter,
    QPainterPath,
    QColor,
    QLinearGradient,
    QRadialGradient,
    QBrush,
    QPen,
    QFont,
    QMouseEvent
)
import math


class GlassButton(QPushButton):
    """Glassmorphism styled button with hover effects"""

    def __init__(self, text: str = "", parent: Optional[QWidget] = None):
        super().__init__(text, parent)

        self.base_color = QColor(255, 255, 255, 40)
        self.hover_color = QColor(255, 255, 255, 80)
        self.press_color = QColor(255, 255, 255, 100)
        self.border_color = QColor(255, 255, 255, 120)

        self._is_hovered = False
        self._is_pressed = False

        # Set minimum size
        self.setMinimumHeight(40)
        self.setMinimumWidth(100)

        # Font styling
        font = QFont("Segoe UI", 11, QFont.Weight.Bold)
        self.setFont(font)

        # Enable mouse tracking
        self.setAttribute(Qt.WidgetAttribute.WA_Hover)
        self.setMouseTracking(True)

    def paintEvent(self, event):
        """Custom paint with glassmorphism effect"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        path = QPainterPath()
        path.addRoundedRect(QRectF(rect), 12, 12)

        # Choose color based on state
        if self._is_pressed:
            bg_color = self.press_color
        elif self._is_hovered:
            bg_color = self.hover_color
        else:
            bg_color = self.base_color

        # Background with gradient
        gradient = QLinearGradient(0, 0, 0, rect.height())
        gradient.setColorAt(0, bg_color.lighter(110))
        gradient.setColorAt(1, bg_color)

        painter.fillPath(path, QBrush(gradient))

        # Border
        painter.setPen(QPen(self.border_color, 2))
        painter.drawPath(path)

        # Shine effect on top
        shine_gradient = QLinearGradient(0, 0, 0, rect.height() / 3)
        shine_color = QColor(255, 255, 255, 50)
        shine_gradient.setColorAt(0, shine_color)
        shine_gradient.setColorAt(1, QColor(255, 255, 255, 0))

        shine_path = QPainterPath()
        shine_path.addRoundedRect(QRectF(2, 2, rect.width() - 4, rect.height() / 3), 10, 10)
        painter.fillPath(shine_path, QBrush(shine_gradient))

        # Text
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.text())

    def enterEvent(self, event):
        """Mouse enter"""
        self._is_hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Mouse leave"""
        self._is_hovered = False
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        """Mouse press"""
        self._is_pressed = True
        self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Mouse release"""
        self._is_pressed = False
        self.update()
        super().mouseReleaseEvent(event)


class GlassCard(QFrame):
    """Glassmorphism card container"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.bg_color = QColor(30, 30, 40, 180)
        self.border_color = QColor(255, 255, 255, 80)

        # Setup layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)

        self.setMinimumSize(200, 150)

    def paintEvent(self, event):
        """Custom paint with glass effect"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        path = QPainterPath()
        path.addRoundedRect(QRectF(rect), 15, 15)

        # Background
        painter.fillPath(path, QBrush(self.bg_color))

        # Border
        painter.setPen(QPen(self.border_color, 2))
        painter.drawPath(path)

        # Subtle shine
        shine_gradient = QLinearGradient(0, 0, 0, rect.height() / 4)
        shine_gradient.setColorAt(0, QColor(255, 255, 255, 30))
        shine_gradient.setColorAt(1, QColor(255, 255, 255, 0))

        painter.fillPath(path, QBrush(shine_gradient))


class AnimatedProgressBar(QProgressBar):
    """Animated progress bar with gradient"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.setMinimumHeight(25)
        self.setTextVisible(True)

        # Animation
        self.gradient_offset = 0.0
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_gradient)
        self.timer.start(30)  # ~33 FPS for smooth animation

        # Colors
        self.color1 = QColor(100, 150, 255)
        self.color2 = QColor(255, 100, 150)

    def _update_gradient(self):
        """Update gradient animation"""
        self.gradient_offset = (self.gradient_offset + 0.01) % 1.0
        self.update()

    def paintEvent(self, event):
        """Custom paint with animated gradient"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()

        # Background
        bg_path = QPainterPath()
        bg_path.addRoundedRect(QRectF(rect), 12, 12)
        painter.fillPath(bg_path, QBrush(QColor(40, 40, 50)))

        # Progress
        if self.value() > 0:
            progress_width = int((rect.width() - 4) * self.value() / self.maximum())
            progress_rect = QRectF(2, 2, progress_width, rect.height() - 4)

            progress_path = QPainterPath()
            progress_path.addRoundedRect(progress_rect, 10, 10)

            # Animated gradient
            gradient = QLinearGradient(
                self.gradient_offset * rect.width(),
                0,
                (self.gradient_offset + 0.5) * rect.width(),
                0
            )
            gradient.setColorAt(0, self.color1)
            gradient.setColorAt(0.5, self.color2)
            gradient.setColorAt(1, self.color1)
            gradient.setSpread(QLinearGradient.Spread.RepeatSpread)

            painter.fillPath(progress_path, QBrush(gradient))

        # Text
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        text = f"{self.value()}%"
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)


class NeonLabel(QLabel):
    """Label with neon glow effect"""

    def __init__(self, text: str = "", color: QColor = QColor(0, 255, 255), parent: Optional[QWidget] = None):
        super().__init__(text, parent)

        self.glow_color = color
        self.glow_intensity = 1.0

        font = QFont("Segoe UI", 16, QFont.Weight.Bold)
        self.setFont(font)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def paintEvent(self, event):
        """Custom paint with glow"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()

        # Draw glow layers
        for i in range(3):
            blur_radius = (3 - i) * 3
            alpha = int(100 * self.glow_intensity / (i + 1))

            glow_color = QColor(self.glow_color)
            glow_color.setAlpha(alpha)

            painter.setPen(QPen(glow_color, blur_radius))
            painter.drawText(rect, int(self.alignment()), self.text())

        # Draw main text
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(rect, int(self.alignment()), self.text())


class PulseWidget(QWidget):
    """Widget with pulsing animation"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.pulse_phase = 0.0
        self.pulse_speed = 1.0
        self.min_opacity = 0.3
        self.max_opacity = 1.0

        self.timer = QTimer()
        self.timer.timeout.connect(self._update_pulse)
        self.timer.start(16)  # ~60 FPS

    def _update_pulse(self):
        """Update pulse animation"""
        self.pulse_phase += 0.05 * self.pulse_speed
        opacity = self.min_opacity + (self.max_opacity - self.min_opacity) * (math.sin(self.pulse_phase) * 0.5 + 0.5)

        # Update opacity
        if hasattr(self, '_opacity_effect'):
            self._opacity_effect.setOpacity(opacity)
        else:
            self._opacity_effect = QGraphicsBlurEffect()
            self.setGraphicsEffect(self._opacity_effect)
            self._opacity_effect.setOpacity(opacity)

        self.update()

    def set_pulse_speed(self, speed: float):
        """Set pulse animation speed"""
        self.pulse_speed = speed


class RoundedIconButton(QPushButton):
    """Circular button with icon"""

    def __init__(self, icon_text: str = "▶", size: int = 50, parent: Optional[QWidget] = None):
        super().__init__(icon_text, parent)

        self.button_size = size
        self.base_color = QColor(100, 150, 255, 200)
        self.hover_color = QColor(120, 170, 255, 255)
        self.press_color = QColor(80, 130, 235, 255)

        self._is_hovered = False
        self._is_pressed = False

        self.setFixedSize(size, size)
        self.setFont(QFont("Segoe UI", int(size * 0.4), QFont.Weight.Bold))

        self.setAttribute(Qt.WidgetAttribute.WA_Hover)
        self.setMouseTracking(True)

    def paintEvent(self, event):
        """Custom circular paint"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        center = self.rect().center()
        radius = self.button_size / 2 - 2

        # Choose color
        if self._is_pressed:
            color = self.press_color
        elif self._is_hovered:
            color = self.hover_color
        else:
            color = self.base_color

        # Gradient background
        gradient = QRadialGradient(center, radius)
        gradient.setColorAt(0, color.lighter(120))
        gradient.setColorAt(1, color)

        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor(255, 255, 255, 150), 2))
        painter.drawEllipse(center, radius, radius)

        # Icon/text
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())

    def enterEvent(self, event):
        """Mouse enter"""
        self._is_hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Mouse leave"""
        self._is_hovered = False
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        """Mouse press"""
        self._is_pressed = True
        self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Mouse release"""
        self._is_pressed = False
        self.update()
        super().mouseReleaseEvent(event)


class NotificationToastWidget(QFrame):
    """Modern notification toast"""

    closed = pyqtSignal()

    def __init__(self, title: str, message: str, toast_type: str = "info", parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.setMinimumWidth(300)
        self.setMaximumWidth(400)

        # Colors based on type
        type_colors = {
            "info": QColor(100, 150, 255, 230),
            "success": QColor(100, 255, 150, 230),
            "warning": QColor(255, 200, 50, 230),
            "error": QColor(255, 100, 100, 230),
        }
        self.bg_color = type_colors.get(toast_type, type_colors["info"])

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white;")
        layout.addWidget(title_label)

        # Message
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setFont(QFont("Segoe UI", 10))
        message_label.setStyleSheet("color: white;")
        layout.addWidget(message_label)

        # Auto-close timer
        self.close_timer = QTimer()
        self.close_timer.timeout.connect(self.closed.emit)
        self.close_timer.setSingleShot(True)
        self.close_timer.start(3000)  # 3 seconds

    def paintEvent(self, event):
        """Custom paint"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        path = QPainterPath()
        path.addRoundedRect(QRectF(rect), 10, 10)

        # Background
        painter.fillPath(path, QBrush(self.bg_color))

        # Border
        painter.setPen(QPen(QColor(255, 255, 255, 150), 2))
        painter.drawPath(path)

    def mousePressEvent(self, event: QMouseEvent):
        """Close on click"""
        self.closed.emit()
        super().mousePressEvent(event)


class LoadingSpinnerWidget(QWidget):
    """Animated loading spinner"""

    def __init__(self, size: int = 40, color: QColor = QColor(100, 150, 255), parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.spinner_size = size
        self.color = color
        self.rotation = 0.0

        self.setFixedSize(size, size)

        # Animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_rotation)

    def start(self):
        """Start spinning"""
        self.timer.start(16)  # ~60 FPS

    def stop(self):
        """Stop spinning"""
        self.timer.stop()

    def _update_rotation(self):
        """Update rotation"""
        self.rotation = (self.rotation + 6) % 360
        self.update()

    def paintEvent(self, event):
        """Paint spinner"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.translate(self.spinner_size / 2, self.spinner_size / 2)
        painter.rotate(self.rotation)

        # Draw spinner arcs
        radius = self.spinner_size / 2 - 4
        for i in range(8):
            angle = i * 45
            alpha = int(255 * (i + 1) / 8)
            color = QColor(self.color)
            color.setAlpha(alpha)

            painter.save()
            painter.rotate(angle)
            painter.setPen(QPen(color, 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(int(radius * 0.6), 0, int(radius), 0)
            painter.restore()


class GradientCard(GlassCard):
    """Card with animated gradient background"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.gradient_offset = 0.0
        self.color1 = QColor(100, 150, 255, 180)
        self.color2 = QColor(255, 100, 150, 180)

        # Animation
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_gradient)
        self.timer.start(30)

    def _update_gradient(self):
        """Update gradient animation"""
        self.gradient_offset = (self.gradient_offset + 0.005) % 1.0
        self.update()

    def paintEvent(self, event):
        """Paint with animated gradient"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        path = QPainterPath()
        path.addRoundedRect(QRectF(rect), 15, 15)

        # Animated gradient
        gradient = QLinearGradient(
            self.gradient_offset * rect.width(),
            0,
            (self.gradient_offset + 1.0) * rect.width(),
            rect.height()
        )
        gradient.setColorAt(0, self.color1)
        gradient.setColorAt(0.5, self.color2)
        gradient.setColorAt(1, self.color1)

        painter.fillPath(path, QBrush(gradient))

        # Border
        painter.setPen(QPen(QColor(255, 255, 255, 120), 2))
        painter.drawPath(path)


class ConnectionStatusIndicator(QWidget):
    """Animated connection status indicator"""

    def __init__(self, size: int = 20, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.indicator_size = size
        self.setFixedSize(size, size)

        self.connected = False
        self.pulse_phase = 0.0

        # Animation
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_pulse)
        self.timer.start(50)

    def set_connected(self, connected: bool):
        """Set connection status"""
        self.connected = connected
        self.update()

    def _update_pulse(self):
        """Update pulse animation"""
        if self.connected:
            self.pulse_phase += 0.1
        self.update()

    def paintEvent(self, event):
        """Paint status indicator"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        center = self.rect().center()
        radius = self.indicator_size / 2 - 2

        if self.connected:
            # Green with pulse
            pulse = math.sin(self.pulse_phase) * 0.2 + 0.8
            color = QColor(100, 255, 150, int(255 * pulse))

            # Glow
            gradient = QRadialGradient(center, radius * 1.5)
            gradient.setColorAt(0, color)
            color.setAlpha(0)
            gradient.setColorAt(1, color)

            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(center, radius * 1.5, radius * 1.5)

            # Core
            painter.setBrush(QBrush(QColor(100, 255, 150)))
            painter.drawEllipse(center, radius, radius)
        else:
            # Red, no pulse
            painter.setBrush(QBrush(QColor(255, 100, 100)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(center, radius, radius)
