# Quick Start Guide - Visual Effects ✨

Get DAIW's stunning visual effects running in 5 minutes!

---

## Option 1: Try the Demo (Fastest!)

See all the visual effects in action immediately:

```bash
cd /home/user/ableton-live-mcp-server/DAIW
python demo_visual_effects.py
```

This launches an interactive demo showing:
- All 5 avatar states with effects
- 6 theme options
- Particle systems, glows, trails
- Modern glassmorphism widgets
- Animated progress bars & spinners
- Toast notifications

**Controls:**
- Click state buttons to change avatar mode
- Switch themes from dropdown
- Toggle effects on/off
- Start auto demo to cycle through all states
- Click "Particle Burst" for fireworks!

---

## Option 2: Integrate into DAIW (3 Easy Steps)

### Step 1: Replace the Avatar Widget

In `/home/user/ableton-live-mcp-server/DAIW/daiw/gui/transparent_window.py`:

**Change this:**
```python
from daiw.gui.bass_clef_widget import BassClefWidget, AvatarState
```

**To this:**
```python
from daiw.gui.bass_clef_widget_enhanced import BassClefWidget, AvatarState
```

That's it! The enhanced widget is a drop-in replacement with all effects! ✅

### Step 2: Add Trail Effects (Optional)

In the same file, add trail support when dragging:

**In `mouseMoveEvent`:**
```python
def mouseMoveEvent(self, event: QMouseEvent) -> None:
    if self._dragging and event.buttons() == Qt.MouseButton.LeftButton:
        self.move(event.globalPosition().toPoint() - self._drag_position)

        # Add this line:
        self.avatar.add_trail_point(event.globalPosition())

        event.accept()
```

**In `mouseReleaseEvent`:**
```python
def mouseReleaseEvent(self, event: QMouseEvent) -> None:
    if event.button() == Qt.MouseButton.LeftButton:
        self._dragging = False

        # Add this line:
        self.avatar.clear_trail()

        event.accept()
```

Now the avatar leaves a beautiful trail when you drag it! ✨

### Step 3: Add Visual Settings (Optional)

Add a menu item to access visual settings:

**In `_create_context_menu`:**
```python
from daiw.gui.visual_settings_dialog import VisualSettingsDialog

# Add after other menu items:
self.visual_settings_action = QAction("🎨 Visual Settings", self)
self.visual_settings_action.triggered.connect(self._show_visual_settings)
self.context_menu.addAction(self.visual_settings_action)
```

**Add the method:**
```python
def _show_visual_settings(self) -> None:
    """Show visual settings dialog"""
    dialog = VisualSettingsDialog(self)

    # Connect signals to avatar
    dialog.effects_enabled_changed.connect(
        lambda enabled: self.avatar.toggle_effects(enabled)
    )
    dialog.theme_changed.connect(
        lambda theme: self.avatar.set_theme(theme)
    )

    dialog.exec()
```

Now users can customize everything! 🎨

---

## What You Get

### 🎨 Visual Effects by Mode

**💤 Idle:**
- Subtle blue glow
- Gentle pulse (0.5 speed)
- Minimal particles

**🎸 Jam/Playing:**
- Musical notes (♪ ♫) floating upward
- Intense pink/red glow
- Fast pulse (2.0 speed)
- High energy!

**👁️ Learn/Listening:**
- Swirling spiral particles (30 particles)
- Sound wave rings
- Green glow
- Hypnotic effect

**🔒 Lock:**
- Matrix-style code rain
- Gold glow
- Slow pulse
- Secure feeling

**🧠 Thinking:**
- Rainbow color cycling
- Floating particles
- Color-shifting glow
- Creative vibe

### 🎨 Available Themes

1. **Dark** - Classic professional (default)
2. **Light** - Clean daytime theme
3. **Cyberpunk** - Neon cyan/magenta
4. **Sunset** - Warm oranges/reds
5. **Ocean** - Cool blues/turquoise
6. **Forest** - Natural greens

### 💫 Smooth Animations

- 60 FPS rendering
- Smooth state transitions (600ms)
- Color morphing
- Scale animations
- Fade in/out effects
- Micro-interactions on buttons

### 🔘 Modern Widgets

All dialogs get automatic glassmorphism styling:
- Frosted glass effect
- Rounded corners (6-12px)
- Smooth gradients
- Animated progress bars
- Custom scrollbars
- Neon labels for titles

---

## Customization

### Change Theme Programmatically

```python
from daiw.gui.themes import get_theme_manager

# Switch theme
get_theme_manager().set_theme("cyberpunk")

# Get theme colors
theme = get_theme_manager().current_theme
color = theme.get_mode_color("jam")  # Get jam mode color
```

### Control Effects

```python
# Enable/disable effects
avatar.toggle_effects(True)   # On
avatar.toggle_effects(False)  # Off

# Access effects manager
avatar.effects_manager.performance_mode = True  # Low-end mode
avatar.effects_manager.effects_enabled = False  # Disable all

# Manual particle emission
from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QColor

center = QPointF(100, 100)
color = QColor(255, 100, 150)
avatar.effects_manager.emit_burst(center, color, count=50)
```

### Create Custom Widgets

```python
from daiw.gui.modern_widgets import (
    GlassButton,
    GlassCard,
    AnimatedProgressBar,
    NotificationToastWidget
)

# Glass button
button = GlassButton("Click Me!")
button.clicked.connect(my_function)

# Glass card container
card = GlassCard()
card.layout.addWidget(QLabel("Content here"))

# Animated progress
progress = AnimatedProgressBar()
progress.setValue(75)

# Toast notification
toast = NotificationToastWidget(
    "Success!",
    "Operation completed",
    "success",  # or "info", "warning", "error"
    parent_widget
)
```

### Animations

```python
from daiw.gui.animations import (
    FadeAnimation,
    ScaleAnimation,
    SlideAnimation
)

# Fade in a widget
fade = FadeAnimation(widget, duration=300)
fade.fade_in()

# Scale animation
scale = ScaleAnimation(widget, duration=200)
scale.pulse()  # Quick pulse effect

# Slide in notification
slide = SlideAnimation(toast, direction="bottom")
slide.slide_in((x, y))
```

---

## Performance Tips

### High-Performance PC
✅ All effects enabled
✅ High particle density
✅ 150-200% glow intensity
✅ Any theme you like

### Mid-Range PC
✅ Effects enabled
⚠️ Medium particle density
✅ 100% glow intensity
✅ Dark or Light theme

### Low-End PC
⚠️ Performance mode enabled
⚠️ Low particle density
⚠️ 50% glow intensity
✅ Dark or Light theme (simpler rendering)

### Battery Saving
❌ Effects disabled
✅ Minimal animations
✅ Light theme (less GPU)

**Note:** DAIW automatically enables performance mode if FPS drops below 30!

---

## Troubleshooting

### Effects not showing?
1. Check if effects are enabled: `avatar.effects_enabled`
2. Try toggling: `avatar.toggle_effects(True)`
3. Check FPS - may be in performance mode

### Low FPS?
1. Enable performance mode
2. Reduce particle density
3. Lower glow intensity
4. Use simpler theme (Dark/Light)

### Colors not changing?
1. Ensure you're using the enhanced widget
2. Check theme is applied: `get_theme_manager().set_theme("dark")`
3. Call `avatar.update()` to force refresh

### Trails not appearing?
1. Ensure you added the trail code to mouse events
2. Check effects are enabled
3. Verify `add_trail_point()` is being called

---

## File Reference

| File | Purpose |
|------|---------|
| `effects.py` | Particle systems, glows, trails |
| `themes.py` | Color schemes, 6 themes |
| `animations.py` | Smooth transitions, fades, scales |
| `modern_widgets.py` | Glass buttons, cards, progress bars |
| `bass_clef_widget_enhanced.py` | Enhanced avatar with all effects |
| `visual_settings_dialog.py` | User settings UI |
| `demo_visual_effects.py` | Interactive demo |

---

## Full Documentation

For complete API reference, see:
- **`DAIW/docs/VISUAL_ENHANCEMENTS.md`** - Complete guide (30+ pages)
- **`DAIW/TEAM1_EYE_CANDY_SUMMARY.md`** - Feature summary

---

## Examples

### Example 1: Custom Theme Dialog

```python
from daiw.gui.themes import get_theme_manager
from daiw.gui.modern_widgets import GlassButton, GlassCard

class MyDialog(QDialog):
    def __init__(self):
        super().__init__()

        # Apply theme
        theme = get_theme_manager().current_theme
        self.setStyleSheet(theme.get_stylesheet())

        # Use glass card
        card = GlassCard()
        layout = card.layout

        # Add glass buttons
        btn = GlassButton("Awesome!")
        layout.addWidget(btn)
```

### Example 2: Animated Notification

```python
from daiw.gui.modern_widgets import NotificationToastWidget
from daiw.gui.animations import SlideAnimation

def show_notification(parent, message):
    toast = NotificationToastWidget(
        "Notification",
        message,
        "info",
        parent
    )

    # Position bottom-right
    x = parent.width() - toast.width() - 20
    y = parent.height() - toast.height() - 20

    # Slide in
    slide = SlideAnimation(toast, "bottom")
    slide.slide_in((x, y))

    # Auto-close
    toast.closed.connect(lambda: slide.slide_out(hide=True))
```

### Example 3: State-Based Effects

```python
# Change state with automatic effects
avatar.set_state(AvatarState.PLAYING)
# → Automatically switches to pink glow, emits musical notes

# Manual burst
center = QPointF(avatar.width() / 2, avatar.height() / 2)
color = QColor(255, 100, 150)
avatar.effects_manager.emit_burst(center, color, count=30)
```

---

## Next Steps

1. **Run the demo:** `python demo_visual_effects.py`
2. **Read the docs:** `DAIW/docs/VISUAL_ENHANCEMENTS.md`
3. **Integrate:** Follow 3-step integration above
4. **Customize:** Adjust settings to your preference
5. **Share:** Show off your beautiful DAIW! ✨

---

## Support

For issues or questions:
1. Check `VISUAL_ENHANCEMENTS.md` for detailed info
2. Review `TEAM1_EYE_CANDY_SUMMARY.md` for features
3. Run demo to verify effects work

---

**Enjoy your stunningly beautiful DAIW!** 🎉✨

*"Making music production gorgeous, one particle at a time."*
