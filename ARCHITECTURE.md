# Music Copilot Avatar - Architecture Overview

## 📁 Projektstruktur

```
ableton-live-mcp-server/
├── mcp_ableton_server.py       # Existing: MCP Server
├── osc_daemon.py               # Existing: OSC Daemon für Ableton
├── requirements.txt            # Updated: Alle Dependencies
├── setup_avatar.py             # NEW: Setup & Validation Script
├── AVATAR_README.md            # NEW: Avatar Dokumentation
├── ARCHITECTURE.md             # NEW: Diese Datei
│
└── avatar/                     # NEW: Avatar System
    ├── main.py                 # Entry Point
    │
    ├── gui/                    # GUI Layer (PyQt6)
    │   ├── bass_clef_widget.py     # Animierter Bassschlüssel-Avatar
    │   └── transparent_window.py   # Transparentes Hauptfenster
    │
    ├── brain/                  # AI & Logic Layer
    │   ├── ai_controller.py        # LangChain Integration
    │   └── mode_manager.py         # Modi-Koordination
    │
    ├── audio/                  # Audio/MIDI Layer
    │   ├── ableton_connector.py    # OSC Bridge (nutzt osc_daemon.py)
    │   └── midi_handler.py         # MIDI I/O via mido
    │
    ├── dynamic_tools/          # Music Library & Skills
    │   ├── music_theory.py         # Harmonie/Rhythmus Grundbausteine
    │   └── generated_skills/       # Auto-generierte Python Skills
    │       └── example_skill.py
    │
    └── utils/
        └── config.py               # Konfiguration (.env)
```

## 🔄 Datenfluss

### 1. User Input → Avatar

```
User (MIDI Keyboard)
    ↓
MIDI Port
    ↓
MIDIHandler (mido)
    ↓
ModeManager (learn mode)
    ↓
AIController (pattern analysis)
    ↓
Generated Skill (Lock Mode)
```

### 2. Avatar → Ableton

```
AIController (musical idea)
    ↓
MIDIHandler.send_note()
    ↓
Virtual MIDI Port
    ↓
Ableton Live
```

### 3. Avatar ↔ Ableton (OSC)

```
AbletonConnector
    ↓ (Socket)
OSC Daemon (osc_daemon.py)
    ↓ (OSC UDP)
AbletonOSC (Ableton Live)
```

## 🎭 Modi-Architektur

### Mode Manager State Machine

```
┌─────────────┐
│    IDLE     │ ←─────┐
└──────┬──────┘       │
       │              │
   User selects       │
       │              │
       ├──→ JAM ──────┤
       │              │
       ├──→ LEARN ────┤
       │              │
       └──→ LOCK ─────┘
```

### Jam Mode Flow

```
ModeManager.set_mode(JAM)
    ↓
Start background task
    ↓
Loop:
  1. AIController.generate_musical_idea()
  2. MIDIHandler.send_sequence()
  3. Wait 2 seconds
```

### Learn Mode Flow

```
ModeManager.set_mode(LEARN)
    ↓
Start MIDI listener
    ↓
Record MIDI events to session
    ↓
User plays...
    ↓
On mode change:
  Analyze pattern with AI
  Store analysis in session
```

### Lock Mode Flow

```
ModeManager.set_mode(LOCK)
    ↓
Get analysis from Learn session
    ↓
AIController.generate_skill_code()
    ↓
Save to generated_skills/skill_TIMESTAMP.py
    ↓
importlib.util.load_module()
    ↓
Execute skill in background
```

## 🧩 Komponenten-Interaktion

### Main Application Loop (PyQt6 + asyncio)

```python
QApplication
    ↓
qasync.QEventLoop  # Qt + asyncio zusammen
    ↓
TransparentAvatarWindow (GUI)
    ├── BassClefWidget (animated)
    ├── Context Menu (mode selection)
    └── Signals (mode_changed, exit_requested)

MusicCopilotAvatar
    ├── AIController
    ├── MIDIHandler
    ├── AbletonConnector
    └── ModeManager
        └── koordiniert alle
```

### Async Architecture

Alle I/O-intensive Operationen sind async:

```python
# AI Calls
await ai_controller.chat(message)
await ai_controller.generate_musical_idea()

# MIDI
await midi_handler.send_note_async(note)
await midi_handler.send_sequence(notes)

# OSC
await ableton_connector.send_osc_message(address, args)

# Mode Management
await mode_manager.set_mode(Mode.JAM)
await mode_manager.execute_skill(skill_name)
```

→ **UI friert niemals ein!**

## 🎨 GUI Layer Details

### Bass Clef Widget (SVG Rendering)

```python
QPainter
    ↓
QPainterPath (Bass Clef Kurve)
    ↓
QRadialGradient (Tiefe/Shading)
    ↓
Animated States:
  - PLAYING: vibrate to beat
  - LISTENING: ear waves
  - THINKING: pulsing
  - LOCKED: lock icon overlay
```

### Transparent Window

```python
Qt Flags:
  - FramelessWindowHint (kein Rahmen)
  - WindowStaysOnTopHint (always on top)
  - WA_TranslucentBackground (transparent)

Mouse Events:
  - mousePressEvent → start drag / context menu
  - mouseMoveEvent → window position
  - mouseDoubleClickEvent → cycle modes
```

## 🧠 AI Integration

### LangChain Architecture

```
User Request
    ↓
AIController.chat()
    ↓
Build message chain:
  - SystemMessage (music copilot identity)
  - Context (current mode, state)
  - History (last 10 messages)
  - HumanMessage (user request)
    ↓
ChatAnthropic / ChatOpenAI
    ↓
Response parsing (JSON extraction)
    ↓
Return structured data
```

### Skill Code Generation

```
AIController.generate_skill_code()
    ↓
Prompt with:
  - Task description
  - Pattern analysis
  - music_theory library API
  - Template structure
    ↓
LLM generates Python code
    ↓
Extract code block from markdown
    ↓
Return code string
    ↓
ModeManager saves to .py file
```

## 🎵 Music Theory Library

Basis-API für generierte Skills:

```python
# Chords
create_chord(root, ChordType.MAJOR) → [60, 64, 67]

# Scales
get_scale_notes(root, Scale.MAJOR, octaves=2) → [...]

# Arpeggios
create_arpeggio(chord, "up-down", octaves=2) → [...]

# Rhythm
generate_rhythm_pattern(16, density=0.6) → [True, False, ...]

# Progressions
apply_progression(60, Scale.MAJOR, "I-V-vi-IV") → [[...], [...]]
```

## 🔒 Meta-Programming (Lock Mode)

### Dynamic Skill Loading

```python
# 1. Generate code
code = await ai_controller.generate_skill_code(task, analysis)

# 2. Save to file
skill_path = skills_dir / f"skill_{timestamp}.py"
skill_path.write_text(code)

# 3. Import dynamically
spec = importlib.util.spec_from_file_location(name, skill_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

# 4. Store in registry
loaded_skills[skill_name] = {
    'module': module,
    'execute': module.execute_skill,
    'description': module.SKILL_DESCRIPTION
}

# 5. Execute
await execute_skill(midi_handler, ableton_connector, **kwargs)
```

### Skill Template

Jeder generierte Skill folgt diesem Template:

```python
from avatar.dynamic_tools.music_theory import *
from avatar.audio.midi_handler import MIDINote

async def execute_skill(midi_handler, ableton_connector, **kwargs):
    """
    Skill-spezifische Logik
    """
    # Nutze music_theory Funktionen
    # Sende MIDI via midi_handler
    # Kommuniziere mit Ableton via ableton_connector
    pass

# Metadata
SKILL_NAME = "unique_name"
SKILL_DESCRIPTION = "What it does"
SKILL_VERSION = "1.0.0"
```

## 🔌 Externe Abhängigkeiten

### Required Services

1. **OSC Daemon** (`osc_daemon.py`)
   - Läuft separat
   - Port 65432 (Socket Server)
   - Port 11000 (OSC → Ableton)
   - Port 11001 (OSC ← Ableton)

2. **Ableton Live + AbletonOSC**
   - AbletonOSC als Control Surface
   - Empfängt OSC auf 11000
   - Sendet OSC auf 11001

3. **Virtual MIDI Port**
   - Windows: loopMIDI
   - macOS: IAC Driver
   - Linux: ALSA virmidi

4. **AI API**
   - Anthropic (Claude) oder
   - OpenAI (GPT)

## 📊 Performance Considerations

### Async I/O

Alle langsamen Operationen sind non-blocking:
- AI API calls → `await`
- MIDI send → `await`
- OSC socket → `await`
- File I/O → `await`

### GUI Updates

```python
QTimer (50ms) → animate avatar
    ↓
BassClefWidget.update()
    ↓
paintEvent() → redraw
```

→ 20 FPS Animation ohne UI freeze

### Memory

- Conversation history: Limited to last 10 messages
- MIDI recording: Limited by session duration
- Loaded skills: Only metadata in memory, lazy execution

## 🔮 Future Extensions

### 1. Audio Analysis (librosa)

```
Audio Input
    ↓
librosa.onset_detect()
    ↓
Extract tempo, key, rhythm
    ↓
Feed to AIController
```

### 2. PyTorch Pattern Recognition

```
MIDI Data
    ↓
LSTM Model
    ↓
Predict next notes
    ↓
Generate complement
```

### 3. Docker Swarm (Raspi Worker)

```
Avatar (Windows)
    ↓ (HTTP/gRPC)
Raspi Worker (Docker Swarm)
    ↓
PyTorch Training
    ↓
Return weights
```

## 🧪 Testing

### Unit Tests (pytest)

```bash
pytest avatar/tests/test_music_theory.py
pytest avatar/tests/test_midi_handler.py
pytest avatar/tests/test_ai_controller.py
```

### Integration Tests

```bash
# Test OSC connection
pytest avatar/tests/integration/test_ableton_connection.py

# Test skill loading
pytest avatar/tests/integration/test_skill_loading.py
```

### Manual Testing

```bash
# Test MIDI
python avatar/audio/midi_handler.py

# Test music theory
python avatar/dynamic_tools/music_theory.py

# Test skill
python avatar/dynamic_tools/generated_skills/example_skill.py
```

## 📝 Configuration

### Environment Variables (.env)

```bash
# AI
ANTHROPIC_API_KEY=sk-ant-xxx
OPENAI_API_KEY=sk-xxx
AVATAR_AI_PROVIDER=anthropic

# OSC
OSC_DAEMON_HOST=127.0.0.1
OSC_DAEMON_PORT=65432

# MIDI
MIDI_OUTPUT_PORT=  # Auto-detect

# Avatar
AVATAR_MODE=idle
```

### Config Loading

```python
from avatar.utils.config import get_config

config = get_config()  # Loads from .env
```

## 🚀 Deployment

### Windows (Elitebook)

```bash
# 1. Install Python 3.10+
# 2. Clone repo
git clone https://github.com/your/repo.git

# 3. Setup
python setup_avatar.py

# 4. Start OSC Daemon
python osc_daemon.py

# 5. Start Avatar
python avatar/main.py
```

### Docker (Optional)

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY avatar/ avatar/
CMD ["python", "avatar/main.py"]
```

## 🔐 Security

- API Keys in `.env` (gitignored)
- No hardcoded credentials
- Generated skills sandboxed (only music_theory imports)
- Socket communication localhost-only

---

**Hinweis**: Dies ist ein kreatives Musik-Tool, kein Production-Ready System. Für Live-Performance sollten zusätzliche Error Handling und Monitoring implementiert werden.
