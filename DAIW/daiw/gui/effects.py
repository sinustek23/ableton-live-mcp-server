"""
Visual Effects System - Particle effects, glows, and eye candy

Provides particle systems, glow effects, trails, and other visual enhancements
for making DAIW stunningly beautiful while maintaining 60 FPS performance.
"""

from typing import List, Tuple, Optional
from PyQt6.QtCore import QPointF, QTimer, QRectF, Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import (
    QPainter,
    QColor,
    QRadialGradient,
    QLinearGradient,
    QPainterPath,
    QBrush,
    QPen
)
from PyQt6.QtWidgets import QGraphicsBlurEffect, QWidget
import math
import random


class Particle:
    """Single particle in a particle system"""

    def __init__(self, x: float, y: float, vx: float, vy: float,
                 life: float, color: QColor, size: float = 3.0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.color = color
        self.size = size
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-5, 5)

    def update(self, dt: float) -> bool:
        """Update particle, return False if dead"""
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt
        self.rotation += self.rotation_speed * dt

        # Apply gravity/drift
        self.vy += 0.5 * dt

        return self.life > 0

    def draw(self, painter: QPainter):
        """Draw the particle"""
        alpha = int(255 * (self.life / self.max_life))
        color = QColor(self.color)
        color.setAlpha(alpha)

        # Create gradient for soft particle
        gradient = QRadialGradient(self.x, self.y, self.size)
        gradient.setColorAt(0, color)
        color.setAlpha(0)
        gradient.setColorAt(1, color)

        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(self.x, self.y), self.size, self.size)


class MusicalNote:
    """Animated musical note particle"""

    def __init__(self, x: float, y: float, vx: float, vy: float, life: float, color: QColor):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.color = color
        self.rotation = random.uniform(-30, 30)
        self.rotation_speed = random.uniform(-20, 20)
        self.size = random.uniform(8, 15)

    def update(self, dt: float) -> bool:
        """Update note, return False if dead"""
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt
        self.rotation += self.rotation_speed * dt

        # Float upward with slight wave
        self.vy -= 0.3 * dt
        self.x += math.sin(self.y * 0.1) * 0.5

        return self.life > 0

    def draw(self, painter: QPainter):
        """Draw the musical note"""
        alpha = int(255 * (self.life / self.max_life))
        color = QColor(self.color)
        color.setAlpha(alpha)

        painter.save()
        painter.translate(self.x, self.y)
        painter.rotate(self.rotation)
        painter.scale(self.size / 10, self.size / 10)

        # Draw note head (filled circle)
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(0, 0), 5, 4)

        # Draw note stem
        painter.setPen(QPen(color, 1.5))
        painter.drawLine(5, 0, 5, -15)

        painter.restore()


class MatrixRain:
    """Matrix-style code rain effect for Lock mode"""

    def __init__(self, x: float, speed: float, color: QColor):
        self.x = x
        self.y = random.uniform(-100, 0)
        self.speed = speed
        self.color = color
        self.length = random.randint(5, 15)
        self.characters = [chr(random.randint(33, 126)) for _ in range(self.length)]

    def update(self, dt: float, height: float) -> bool:
        """Update rain drop"""
        self.y += self.speed * dt

        # Randomize characters occasionally
        if random.random() < 0.1:
            idx = random.randint(0, self.length - 1)
            self.characters[idx] = chr(random.randint(33, 126))

        return self.y < height + 20

    def draw(self, painter: QPainter):
        """Draw the matrix rain"""
        for i, char in enumerate(self.characters):
            y = self.y + i * 10
            alpha = int(255 * (1 - i / self.length))
            color = QColor(self.color)
            color.setAlpha(alpha)

            painter.setPen(color)
            painter.drawText(int(self.x), int(y), char)


class ParticleSystem:
    """Manages multiple particles with emission"""

    def __init__(self):
        self.particles: List[Particle] = []
        self.notes: List[MusicalNote] = []
        self.matrix_rain: List[MatrixRain] = []
        self.emission_point = QPointF(0, 0)
        self.enabled = True

    def emit_particles(self, x: float, y: float, count: int, color: QColor,
                      spread: float = 50.0, life: float = 2.0):
        """Emit particles from a point"""
        if not self.enabled:
            return

        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(10, spread)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            particle_life = life * random.uniform(0.5, 1.5)
            size = random.uniform(2, 5)

            self.particles.append(Particle(x, y, vx, vy, particle_life, color, size))

    def emit_musical_notes(self, x: float, y: float, count: int, color: QColor):
        """Emit musical note particles"""
        if not self.enabled:
            return

        for _ in range(count):
            vx = random.uniform(-20, 20)
            vy = random.uniform(-30, -10)
            life = random.uniform(2, 4)

            self.notes.append(MusicalNote(x, y, vx, vy, life, color))

    def emit_matrix_rain(self, width: float, height: float, color: QColor, density: int = 5):
        """Emit matrix rain drops"""
        if not self.enabled:
            return

        for _ in range(density):
            x = random.uniform(0, width)
            speed = random.uniform(50, 150)
            self.matrix_rain.append(MatrixRain(x, speed, color))

    def update(self, dt: float, width: float = 0, height: float = 0):
        """Update all particles"""
        # Update regular particles
        self.particles = [p for p in self.particles if p.update(dt)]

        # Update musical notes
        self.notes = [n for n in self.notes if n.update(dt)]

        # Update matrix rain
        self.matrix_rain = [m for m in self.matrix_rain if m.update(dt, height)]

    def draw(self, painter: QPainter):
        """Draw all particles"""
        for particle in self.particles:
            particle.draw(painter)

        for note in self.notes:
            note.draw(painter)

        for rain in self.matrix_rain:
            rain.draw(painter)

    def clear(self):
        """Clear all particles"""
        self.particles.clear()
        self.notes.clear()
        self.matrix_rain.clear()


class GlowEffect:
    """Smooth glow effect with pulsing"""

    def __init__(self, color: QColor, intensity: float = 1.0):
        self.color = color
        self.base_intensity = intensity
        self.intensity = intensity
        self.pulse_phase = 0.0
        self.pulse_speed = 1.0
        self.pulse_amount = 0.3

    def update(self, dt: float):
        """Update pulsing animation"""
        self.pulse_phase += dt * self.pulse_speed
        pulse = math.sin(self.pulse_phase) * self.pulse_amount
        self.intensity = self.base_intensity * (1.0 + pulse)

    def draw(self, painter: QPainter, center: QPointF, radius: float):
        """Draw glow effect"""
        # Create multiple gradient layers for smooth glow
        for i in range(3):
            layer_radius = radius * (1.5 + i * 0.5)
            gradient = QRadialGradient(center, layer_radius)

            alpha = int(100 * self.intensity / (i + 1))
            glow_color = QColor(self.color)
            glow_color.setAlpha(alpha)

            gradient.setColorAt(0, glow_color)
            glow_color.setAlpha(0)
            gradient.setColorAt(1, glow_color)

            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(center, layer_radius, layer_radius)


class TrailEffect:
    """Motion trail effect for dragging"""

    def __init__(self, max_points: int = 20):
        self.points: List[Tuple[QPointF, float]] = []  # (point, age)
        self.max_points = max_points
        self.color = QColor(100, 150, 255, 150)

    def add_point(self, point: QPointF):
        """Add a new trail point"""
        self.points.append((point, 0.0))
        if len(self.points) > self.max_points:
            self.points.pop(0)

    def update(self, dt: float):
        """Age trail points"""
        self.points = [(p, age + dt) for p, age in self.points if age < 1.0]

    def draw(self, painter: QPainter):
        """Draw the trail"""
        if len(self.points) < 2:
            return

        for i in range(len(self.points) - 1):
            p1, age1 = self.points[i]
            p2, age2 = self.points[i + 1]

            alpha = int(150 * (1 - age1))
            color = QColor(self.color)
            color.setAlpha(alpha)

            width = 10 * (1 - age1)
            painter.setPen(QPen(color, width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(p1, p2)

    def clear(self):
        """Clear trail"""
        self.points.clear()


class SpiralParticles:
    """Swirling particles for Learn mode"""

    def __init__(self, center: QPointF, color: QColor):
        self.center = center
        self.color = color
        self.particles: List[Tuple[float, float, float]] = []  # angle, radius, speed
        self.angle_offset = 0.0

        # Create spiral particles
        for i in range(30):
            angle = (i / 30) * math.pi * 2
            radius = 40 + i * 3
            speed = 0.5 + i * 0.05
            self.particles.append([angle, radius, speed])

    def update(self, dt: float, center: QPointF):
        """Update spiral animation"""
        self.center = center
        self.angle_offset += dt * 0.5

        for particle in self.particles:
            particle[0] += dt * particle[2]

    def draw(self, painter: QPainter):
        """Draw swirling particles"""
        for i, (angle, radius, speed) in enumerate(self.particles):
            x = self.center.x() + math.cos(angle + self.angle_offset) * radius
            y = self.center.y() + math.sin(angle + self.angle_offset) * radius

            alpha = int(200 * (1 - i / len(self.particles)))
            color = QColor(self.color)
            color.setAlpha(alpha)

            size = 4 - i * 0.1

            gradient = QRadialGradient(x, y, size)
            gradient.setColorAt(0, color)
            color.setAlpha(0)
            gradient.setColorAt(1, color)

            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(x, y), size, size)


class RainbowCycle:
    """Rainbow color cycling effect"""

    def __init__(self, speed: float = 1.0):
        self.hue = 0.0
        self.speed = speed

    def update(self, dt: float):
        """Update color cycle"""
        self.hue += dt * self.speed * 60
        if self.hue >= 360:
            self.hue -= 360

    def get_color(self, alpha: int = 200) -> QColor:
        """Get current rainbow color"""
        color = QColor.fromHsv(int(self.hue), 255, 255, alpha)
        return color


class WaveEffect:
    """Sound wave visualization effect"""

    def __init__(self, color: QColor):
        self.color = color
        self.waves: List[Tuple[float, float]] = []  # (radius, alpha)
        self.emit_timer = 0.0

    def update(self, dt: float):
        """Update waves"""
        self.emit_timer += dt

        # Emit new wave
        if self.emit_timer > 0.3:
            self.waves.append([20.0, 1.0])
            self.emit_timer = 0.0

        # Update existing waves
        new_waves = []
        for radius, alpha in self.waves:
            radius += dt * 100
            alpha -= dt * 0.7
            if alpha > 0:
                new_waves.append([radius, alpha])
        self.waves = new_waves

    def draw(self, painter: QPainter, center: QPointF):
        """Draw sound waves"""
        for radius, alpha in self.waves:
            color = QColor(self.color)
            color.setAlpha(int(255 * alpha))

            painter.setPen(QPen(color, 2))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(center, radius, radius)


class EffectsManager:
    """Central manager for all visual effects"""

    def __init__(self):
        self.particle_system = ParticleSystem()
        self.glow_effect: Optional[GlowEffect] = None
        self.trail_effect = TrailEffect()
        self.spiral_particles: Optional[SpiralParticles] = None
        self.rainbow_cycle = RainbowCycle()
        self.wave_effect: Optional[WaveEffect] = None

        self.effects_enabled = True
        self.performance_mode = False  # Reduce effects if FPS drops

        # Timer for 60 FPS updates
        self.last_update = 0.0

    def set_mode(self, mode: str, color: QColor, center: QPointF):
        """Configure effects for avatar mode"""
        if not self.effects_enabled:
            return

        # Clear previous effects
        self.particle_system.clear()
        self.spiral_particles = None
        self.wave_effect = None

        if mode == "idle":
            # Subtle pulsing glow
            self.glow_effect = GlowEffect(color, intensity=0.5)
            self.glow_effect.pulse_speed = 0.5
            self.glow_effect.pulse_amount = 0.2

        elif mode == "jam" or mode == "playing":
            # Intense glow + musical notes
            self.glow_effect = GlowEffect(color, intensity=1.5)
            self.glow_effect.pulse_speed = 2.0
            self.glow_effect.pulse_amount = 0.5

        elif mode == "learn" or mode == "listening":
            # Swirling particles + sound waves
            self.glow_effect = GlowEffect(color, intensity=0.8)
            self.spiral_particles = SpiralParticles(center, color)
            self.wave_effect = WaveEffect(color)

        elif mode == "lock" or mode == "locked":
            # Matrix rain
            self.glow_effect = GlowEffect(color, intensity=1.0)
            self.glow_effect.pulse_speed = 0.3

        elif mode == "thinking":
            # Rainbow cycling + particles
            self.glow_effect = GlowEffect(self.rainbow_cycle.get_color(), intensity=1.0)
            self.glow_effect.pulse_speed = 1.5

    def update(self, dt: float, width: float, height: float, center: QPointF, mode: str):
        """Update all effects"""
        if not self.effects_enabled:
            return

        # Update particle system
        self.particle_system.update(dt, width, height)

        # Update glow
        if self.glow_effect:
            self.glow_effect.update(dt)

        # Update trail
        self.trail_effect.update(dt)

        # Update spiral particles
        if self.spiral_particles:
            self.spiral_particles.update(dt, center)

        # Update rainbow
        self.rainbow_cycle.update(dt)

        # Update waves
        if self.wave_effect:
            self.wave_effect.update(dt)

        # Mode-specific effects
        if mode == "playing" or mode == "jam":
            # Emit musical notes periodically
            if random.random() < 0.1 and not self.performance_mode:
                color = self.glow_effect.color if self.glow_effect else QColor(255, 100, 150)
                self.particle_system.emit_musical_notes(
                    center.x() + random.uniform(-30, 30),
                    center.y() + random.uniform(-30, 30),
                    1, color
                )

        elif mode == "locked" or mode == "lock":
            # Matrix rain
            if random.random() < 0.3 and not self.performance_mode:
                color = self.glow_effect.color if self.glow_effect else QColor(255, 200, 50)
                self.particle_system.emit_matrix_rain(width, height, color, density=1)

        elif mode == "thinking":
            # Rainbow particles
            if random.random() < 0.2 and not self.performance_mode:
                self.particle_system.emit_particles(
                    center.x(), center.y(), 2,
                    self.rainbow_cycle.get_color(), spread=30, life=1.5
                )

    def draw(self, painter: QPainter, center: QPointF, radius: float):
        """Draw all effects"""
        if not self.effects_enabled:
            return

        # Draw glow (behind avatar)
        if self.glow_effect:
            self.glow_effect.draw(painter, center, radius)

        # Draw trail (behind avatar)
        self.trail_effect.draw(painter)

        # Draw spiral particles (behind avatar)
        if self.spiral_particles:
            self.spiral_particles.draw(painter)

        # Draw waves (behind avatar)
        if self.wave_effect:
            self.wave_effect.draw(painter, center)

        # Draw particle system (in front of avatar)
        self.particle_system.draw(painter)

    def emit_burst(self, center: QPointF, color: QColor, count: int = 20):
        """Emit particle burst (for interactions)"""
        self.particle_system.emit_particles(center.x(), center.y(), count, color, spread=100, life=2.0)
