"""
Animation System - Smooth transitions and property animations

Provides animation controllers for smooth transitions between states,
fade effects, scale animations, and micro-interactions.
"""

from typing import Optional, Callable, Any
from PyQt6.QtCore import (
    QPropertyAnimation,
    QEasingCurve,
    QObject,
    pyqtProperty,
    QSequentialAnimationGroup,
    QParallelAnimationGroup,
    QTimer,
    pyqtSignal,
    QAbstractAnimation
)
from PyQt6.QtWidgets import QWidget, QGraphicsOpacityEffect
from PyQt6.QtGui import QColor
import math


class AnimatedProperty(QObject):
    """Animatable property wrapper"""

    value_changed = pyqtSignal(float)

    def __init__(self, initial_value: float = 0.0):
        super().__init__()
        self._value = initial_value

    @pyqtProperty(float)
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, val: float):
        if self._value != val:
            self._value = val
            self.value_changed.emit(val)


class ColorProperty(QObject):
    """Animatable color property"""

    color_changed = pyqtSignal(QColor)

    def __init__(self, initial_color: QColor):
        super().__init__()
        self._red = initial_color.red()
        self._green = initial_color.green()
        self._blue = initial_color.blue()
        self._alpha = initial_color.alpha()

    @pyqtProperty(int)
    def red(self) -> int:
        return self._red

    @red.setter
    def red(self, val: int):
        self._red = val
        self._emit_color()

    @pyqtProperty(int)
    def green(self) -> int:
        return self._green

    @green.setter
    def green(self, val: int):
        self._green = val
        self._emit_color()

    @pyqtProperty(int)
    def blue(self) -> int:
        return self._blue

    @blue.setter
    def blue(self, val: int):
        self._blue = val
        self._emit_color()

    @pyqtProperty(int)
    def alpha(self) -> int:
        return self._alpha

    @alpha.setter
    def alpha(self, val: int):
        self._alpha = val
        self._emit_color()

    def _emit_color(self):
        self.color_changed.emit(QColor(self._red, self._green, self._blue, self._alpha))

    def get_color(self) -> QColor:
        return QColor(self._red, self._green, self._blue, self._alpha)


class FadeAnimation:
    """Fade in/out animation for widgets"""

    def __init__(self, widget: QWidget, duration: int = 300):
        self.widget = widget
        self.duration = duration

        # Create opacity effect
        self.opacity_effect = QGraphicsOpacityEffect()
        self.widget.setGraphicsEffect(self.opacity_effect)

        # Create animation
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(duration)

    def fade_in(self, callback: Optional[Callable] = None):
        """Fade widget in"""
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutCubic)

        if callback:
            self.animation.finished.connect(callback)

        self.widget.show()
        self.animation.start()

    def fade_out(self, hide: bool = True, callback: Optional[Callable] = None):
        """Fade widget out"""
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutCubic)

        if hide:
            self.animation.finished.connect(self.widget.hide)

        if callback:
            self.animation.finished.connect(callback)

        self.animation.start()


class ScaleAnimation:
    """Scale animation for widgets"""

    def __init__(self, widget: QWidget, duration: int = 200):
        self.widget = widget
        self.duration = duration
        self.scale_property = AnimatedProperty(1.0)
        self.scale_property.value_changed.connect(self._update_scale)

        self.animation = QPropertyAnimation(self.scale_property, b"value")
        self.animation.setDuration(duration)

    def _update_scale(self, scale: float):
        """Update widget scale"""
        # Store original size if not stored
        if not hasattr(self, 'original_size'):
            self.original_size = self.widget.size()

        # Apply scale transformation
        new_width = int(self.original_size.width() * scale)
        new_height = int(self.original_size.height() * scale)
        self.widget.resize(new_width, new_height)

    def scale_to(self, target_scale: float, easing: QEasingCurve.Type = QEasingCurve.Type.OutBack):
        """Animate to target scale"""
        self.animation.setStartValue(self.scale_property.value)
        self.animation.setEndValue(target_scale)
        self.animation.setEasingCurve(easing)
        self.animation.start()

    def pulse(self, scale: float = 1.2):
        """Quick pulse animation"""
        self.scale_to(scale, QEasingCurve.Type.OutCubic)
        QTimer.singleShot(self.duration, lambda: self.scale_to(1.0, QEasingCurve.Type.InCubic))


class ColorTransition:
    """Smooth color transition animation"""

    def __init__(self, duration: int = 500):
        self.duration = duration
        self.color_property = ColorProperty(QColor(0, 0, 0))
        self.current_color = QColor(0, 0, 0)

        # Animations for each color component
        self.red_anim = QPropertyAnimation(self.color_property, b"red")
        self.green_anim = QPropertyAnimation(self.color_property, b"green")
        self.blue_anim = QPropertyAnimation(self.color_property, b"blue")
        self.alpha_anim = QPropertyAnimation(self.color_property, b"alpha")

        # Group animations
        self.animation_group = QParallelAnimationGroup()
        self.animation_group.addAnimation(self.red_anim)
        self.animation_group.addAnimation(self.green_anim)
        self.animation_group.addAnimation(self.blue_anim)
        self.animation_group.addAnimation(self.alpha_anim)

        for anim in [self.red_anim, self.green_anim, self.blue_anim, self.alpha_anim]:
            anim.setDuration(duration)
            anim.setEasingCurve(QEasingCurve.Type.InOutCubic)

    def transition_to(self, target_color: QColor, callback: Optional[Callable] = None):
        """Transition from current color to target color"""
        # Set start values
        current = self.color_property.get_color()
        self.red_anim.setStartValue(current.red())
        self.green_anim.setStartValue(current.green())
        self.blue_anim.setStartValue(current.blue())
        self.alpha_anim.setStartValue(current.alpha())

        # Set end values
        self.red_anim.setEndValue(target_color.red())
        self.green_anim.setEndValue(target_color.green())
        self.blue_anim.setEndValue(target_color.blue())
        self.alpha_anim.setEndValue(target_color.alpha())

        if callback:
            self.animation_group.finished.connect(callback)

        self.animation_group.start()

    def get_current_color(self) -> QColor:
        """Get current color during animation"""
        return self.color_property.get_color()


class SlideAnimation:
    """Slide in/out animation for notifications and toasts"""

    def __init__(self, widget: QWidget, direction: str = "bottom", duration: int = 400):
        """
        direction: "top", "bottom", "left", "right"
        """
        self.widget = widget
        self.direction = direction
        self.duration = duration

        self.animation = QPropertyAnimation(widget, b"pos")
        self.animation.setDuration(duration)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def slide_in(self, end_pos: tuple):
        """Slide widget into view"""
        # Calculate start position based on direction
        if self.direction == "bottom":
            start_pos = (end_pos[0], end_pos[1] + self.widget.height())
        elif self.direction == "top":
            start_pos = (end_pos[0], end_pos[1] - self.widget.height())
        elif self.direction == "right":
            start_pos = (end_pos[0] + self.widget.width(), end_pos[1])
        else:  # left
            start_pos = (end_pos[0] - self.widget.width(), end_pos[1])

        from PyQt6.QtCore import QPoint
        self.widget.move(*start_pos)
        self.widget.show()

        self.animation.setStartValue(QPoint(*start_pos))
        self.animation.setEndValue(QPoint(*end_pos))
        self.animation.start()

    def slide_out(self, hide: bool = True):
        """Slide widget out of view"""
        current_pos = self.widget.pos()

        # Calculate end position based on direction
        if self.direction == "bottom":
            end_pos = (current_pos.x(), current_pos.y() + self.widget.height())
        elif self.direction == "top":
            end_pos = (current_pos.x(), current_pos.y() - self.widget.height())
        elif self.direction == "right":
            end_pos = (current_pos.x() + self.widget.width(), current_pos.y())
        else:  # left
            end_pos = (current_pos.x() - self.widget.width(), current_pos.y())

        from PyQt6.QtCore import QPoint
        self.animation.setStartValue(current_pos)
        self.animation.setEndValue(QPoint(*end_pos))

        if hide:
            self.animation.finished.connect(self.widget.hide)

        self.animation.start()


class RotationAnimation:
    """3D-like rotation animation"""

    def __init__(self, widget: QWidget, duration: int = 1000):
        self.widget = widget
        self.duration = duration
        self.angle_property = AnimatedProperty(0.0)
        self.angle_property.value_changed.connect(self._update_rotation)

        self.animation = QPropertyAnimation(self.angle_property, b"value")
        self.animation.setDuration(duration)

    def _update_rotation(self, angle: float):
        """Update rotation (triggers repaint)"""
        self.widget.update()

    def rotate_to(self, target_angle: float):
        """Rotate to target angle"""
        self.animation.setStartValue(self.angle_property.value)
        self.animation.setEndValue(target_angle)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.animation.start()

    def spin(self, loops: int = 1):
        """Spin the widget"""
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(360.0 * loops)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.animation.start()

    def get_angle(self) -> float:
        """Get current rotation angle"""
        return self.angle_property.value


class MicroInteractions:
    """Collection of micro-interactions for UI elements"""

    @staticmethod
    def button_hover_grow(widget: QWidget, scale: float = 1.05):
        """Grow button slightly on hover"""
        scale_anim = ScaleAnimation(widget, duration=100)
        scale_anim.scale_to(scale, QEasingCurve.Type.OutCubic)

    @staticmethod
    def button_hover_reset(widget: QWidget):
        """Reset button size after hover"""
        scale_anim = ScaleAnimation(widget, duration=100)
        scale_anim.scale_to(1.0, QEasingCurve.Type.InCubic)

    @staticmethod
    def button_press_shrink(widget: QWidget):
        """Shrink button on press"""
        scale_anim = ScaleAnimation(widget, duration=50)
        scale_anim.scale_to(0.95, QEasingCurve.Type.OutCubic)

    @staticmethod
    def button_release_bounce(widget: QWidget):
        """Bounce button on release"""
        scale_anim = ScaleAnimation(widget, duration=150)
        scale_anim.scale_to(1.0, QEasingCurve.Type.OutBack)


class AnimationSequence:
    """Chain multiple animations in sequence"""

    def __init__(self):
        self.group = QSequentialAnimationGroup()
        self.animations = []

    def add_animation(self, animation: QPropertyAnimation):
        """Add animation to sequence"""
        self.group.addAnimation(animation)
        self.animations.append(animation)

    def add_pause(self, duration: int):
        """Add pause to sequence"""
        pause = QPropertyAnimation()
        pause.setDuration(duration)
        self.group.addPause(duration)

    def start(self, loop: bool = False):
        """Start animation sequence"""
        if loop:
            self.group.setLoopCount(-1)  # Infinite loop
        self.group.start()

    def stop(self):
        """Stop animation sequence"""
        self.group.stop()


class StateTransitionAnimator:
    """Manages smooth transitions between avatar states"""

    def __init__(self):
        self.color_transition = ColorTransition(duration=600)
        self.current_state = "idle"
        self.callbacks = {}

    def transition_to_state(self, new_state: str, color: QColor, callback: Optional[Callable] = None):
        """Transition to new state with color change"""
        if new_state != self.current_state:
            self.current_state = new_state

            # Transition color
            self.color_transition.transition_to(color, callback)

    def get_current_color(self) -> QColor:
        """Get current transition color"""
        return self.color_transition.get_current_color()

    def register_state_callback(self, state: str, callback: Callable):
        """Register callback for specific state transition"""
        self.callbacks[state] = callback


class NotificationToast:
    """Animated notification toast"""

    def __init__(self, widget: QWidget, duration: int = 3000):
        self.widget = widget
        self.display_duration = duration

        self.slide_anim = SlideAnimation(widget, direction="bottom", duration=300)
        self.fade_anim = FadeAnimation(widget, duration=200)

    def show_notification(self, position: tuple):
        """Show notification with slide + fade in"""
        # Slide in
        self.slide_anim.slide_in(position)

        # Auto-hide after duration
        QTimer.singleShot(self.display_duration, self.hide_notification)

    def hide_notification(self):
        """Hide notification with fade + slide out"""
        self.fade_anim.fade_out(hide=False)
        QTimer.singleShot(200, lambda: self.slide_anim.slide_out(hide=True))


class LoadingSpinner:
    """Animated loading spinner"""

    def __init__(self):
        self.rotation = 0.0
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_rotation)
        self.spinning = False

    def start(self):
        """Start spinning"""
        self.spinning = True
        self.timer.start(16)  # ~60 FPS

    def stop(self):
        """Stop spinning"""
        self.spinning = False
        self.timer.stop()

    def _update_rotation(self):
        """Update rotation angle"""
        self.rotation = (self.rotation + 6) % 360

    def get_rotation(self) -> float:
        """Get current rotation"""
        return self.rotation


class AnimationController:
    """Central animation controller for managing all animations"""

    def __init__(self):
        self.active_animations = []
        self.state_animator = StateTransitionAnimator()
        self.enabled = True

        # Performance monitoring
        self.fps_target = 60
        self.performance_mode = False

    def create_fade_animation(self, widget: QWidget, duration: int = 300) -> FadeAnimation:
        """Create and track fade animation"""
        anim = FadeAnimation(widget, duration)
        if not self.performance_mode:
            self.active_animations.append(anim)
        return anim

    def create_scale_animation(self, widget: QWidget, duration: int = 200) -> ScaleAnimation:
        """Create and track scale animation"""
        anim = ScaleAnimation(widget, duration)
        if not self.performance_mode:
            self.active_animations.append(anim)
        return anim

    def create_slide_animation(self, widget: QWidget, direction: str = "bottom",
                              duration: int = 400) -> SlideAnimation:
        """Create and track slide animation"""
        anim = SlideAnimation(widget, direction, duration)
        if not self.performance_mode:
            self.active_animations.append(anim)
        return anim

    def enable_performance_mode(self):
        """Reduce animations for better performance"""
        self.performance_mode = True

    def disable_performance_mode(self):
        """Enable full animations"""
        self.performance_mode = False

    def cleanup(self):
        """Clean up finished animations"""
        # Remove completed animations
        self.active_animations = [
            anim for anim in self.active_animations
            if hasattr(anim, 'animation') and anim.animation.state() == QAbstractAnimation.State.Running
        ]


# Global animation controller
_animation_controller = AnimationController()


def get_animation_controller() -> AnimationController:
    """Get global animation controller instance"""
    return _animation_controller
