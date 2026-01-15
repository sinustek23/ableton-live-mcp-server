# 🎵 Music Copilot Avatar

Ein interaktiver Desktop-Copilot für Musikproduktion in Ableton Live, dargestellt als animierter Bassschlüssel-Avatar.

## 🎯 Konzept

Der Avatar ist ein "Always on Top" Desktop-Assistent in Form eines liegenden Bassschlüssels, der als Co-Actor fungiert und:

- 🎹 **MIDI spielt** - Generiert und spielt musikalische Ideen
- 👁️ **Den User beobachtet** - Lernt von deinem Spielstil
- 🔧 **Eigene Tools schreibt** - Meta-Programming im Lock Mode
- 🤖 **KI-gesteuert** - Nutzt Claude oder GPT für musikalische Intelligenz

## 🏗️ Architektur

```
avatar/
├── gui/                    # PyQt6 GUI Komponenten
│   ├── bass_clef_widget.py    # Der animierte Avatar
│   └── transparent_window.py  # Transparentes Hauptfenster
├── brain/                  # KI & Logik
│   ├── ai_controller.py       # LangChain Integration
│   └── mode_manager.py        # Modi-Verwaltung
├── audio/                  # Audio/MIDI Integration
│   ├── ableton_connector.py   # OSC Kommunikation
│   └── midi_handler.py        # MIDI I/O (mido)
├── dynamic_tools/          # Musik-Bibliothek & Skills
│   ├── music_theory.py        # Grundbausteine (Harmonien, Rhythmus)
│   └── generated_skills/      # Selbstgeschriebene Skills
└── main.py                 # Entry Point
```

## 🎭 Modi

### 1. 💤 Idle Mode
Der Avatar beobachtet passiv. Guter Ausgangszustand.

### 2. 🎸 Freestyle Jam Mode
**Call & Response** - Der Avatar generiert musikalische Ideen und spielt mit dir.

- Generiert Melodien, Harmonien, Rhythmen
- Reagiert auf dein Spiel
- Perfekt für kreative Sessions

### 3. 👁️ Learn by Watching Mode
Der Avatar **zeichnet dein MIDI-Spiel auf** und analysiert:

- Harmonien & Akkordfolgen
- Rhythmische Patterns
- Spielstil (z.B. "Arpeggios auf der 1, Akkorde auf der 2")

### 4. 🔒 Lock Mode (Meta-Programming!)
Das **Highlight**: Der Avatar analysiert deinen Workflow und **schreibt automatisch ein Python-Skript**, das:

1. Deine Patterns abstrahiert
2. Als `.py` Modul gespeichert wird
3. Via `importlib` dynamisch geladen wird
4. Als neuer **Skill** parallel läuft

**Beispiel**:
- Du spielst immer Akkorde auf Beat 1 und Arpeggios auf Beat 2
- Lock Mode erstellt `auto_arpeggiator_v1.py`
- Ab sofort ergänzt der Avatar automatisch deine Akkorde mit Arpeggios!

## 🚀 Installation

### Voraussetzungen

- Python 3.10+
- Windows (Elitebook) - kann aber auch auf macOS/Linux laufen
- Ableton Live mit [AbletonOSC](https://github.com/ideoforms/AbletonOSC)

### Setup

1. **Clone & Install Dependencies**

```bash
# Dependencies installieren
pip install -r requirements.txt

# Oder mit uv (empfohlen)
uv sync
```

2. **Setup Script ausführen**

```bash
python setup_avatar.py
```

Das Script prüft:
- ✅ Python Version
- ✅ Ports (OSC Daemon)
- ✅ MIDI Devices
- ✅ API Keys
- ✅ Dependencies

3. **API Keys setzen**

Kopiere `.env.template` zu `.env`:

```bash
cp .env.template .env
```

Füge deine API Keys ein:

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-xxx
# ODER
OPENAI_API_KEY=sk-xxx
```

4. **OSC Daemon starten**

In einem separaten Terminal:

```bash
python osc_daemon.py
```

5. **Avatar starten**

```bash
python avatar/main.py
```

## 🎮 Bedienung

### Basis-Interaktion

- **Links-Klick + Drag**: Avatar verschieben
- **Rechts-Klick**: Context Menu öffnen
- **Doppelklick**: Durch Modi rotieren

### Context Menu

```
🎸 Freestyle Jam
👁️ Learn by Watching
🔒 Lock Mode (Meta-Programming)
💤 Idle
---
⚙️ Settings
❌ Exit
```

### Avatar-Zustände (Visuell)

- **Blau (Idle)**: Wartet
- **Grün (Listening)**: Nimmt auf, animierte "Ohr-Wellen"
- **Pink/Rot (Playing)**: Spielt MIDI, vibriert zum Takt
- **Lila (Thinking)**: KI denkt nach, pulsiert
- **Gold (Locked)**: Lock Mode aktiv, Vorhängeschloss sichtbar

## 🎹 MIDI Setup

### Windows (empfohlen: loopMIDI)

1. Installiere [loopMIDI](https://www.tobias-erichsen.de/software/loopmidi.html)
2. Erstelle einen virtuellen Port (z.B. "Avatar MIDI")
3. In Ableton: Preferences → MIDI → aktiviere "Avatar MIDI" als Input

### macOS (IAC Driver)

1. Audio MIDI Setup öffnen
2. MIDI Studio → IAC Driver aktivieren
3. Port erstellen
4. In Ableton aktivieren

### Linux (ALSA/JACK)

```bash
# ALSA Virtual Port
modprobe snd-virmidi

# Oder JACK
jack_lsp
```

## 🧠 Music Theory Library

Die `music_theory.py` Library bietet Grundbausteine für generierte Skills:

```python
from avatar.dynamic_tools.music_theory import *

# Akkorde erstellen
chord = create_chord(60, ChordType.MAJOR)  # [60, 64, 67]

# Arpeggios
arp = create_arpeggio(chord, pattern="up-down", octaves=2)

# Skalen
scale = get_scale_notes(60, Scale.MAJOR, octaves=2)

# Rhythmus
rhythm = generate_rhythm_pattern(16, density=0.6)

# Chord Progressions
progression = apply_progression(60, Scale.MAJOR, "I-V-vi-IV")
```

## 🔧 Lock Mode Details

### Wie es funktioniert

1. **Analyse**: Avatar beobachtet deinen Workflow (Learn Mode)
2. **Abstraktion**: KI extrahiert Patterns:
   ```
   "User spielt immer Cmaj7 auf Beat 1, dann Arpeggio auf Beat 2-4"
   ```
3. **Code-Generierung**: KI schreibt Python-Skill:
   ```python
   # auto_chord_arp_v1.py
   async def execute_skill(midi_handler, ableton_connector, **kwargs):
       # Automatisierter Code hier
       pass
   ```
4. **Dynamisches Laden**: `importlib` lädt das Modul
5. **Ausführung**: Skill läuft parallel und unterstützt dich

### Beispiel-Skill

```python
# generated_skills/auto_arpeggiator_v1.py
from avatar.dynamic_tools.music_theory import create_chord, create_arpeggio, ChordType
from avatar.audio.midi_handler import MIDINote

async def execute_skill(midi_handler, ableton_connector, **kwargs):
    """
    Spielt automatisch Arpeggios basierend auf erkannten Akkorden
    """
    # Erkenne Akkord aus User-Input
    user_notes = kwargs.get('user_notes', [60, 64, 67])

    # Erstelle Arpeggio
    arp = create_arpeggio(user_notes, pattern="up", octaves=1)

    # Spiele Arpeggio
    for note in arp:
        midi_note = MIDINote(note=note, velocity=80, duration=0.25)
        await midi_handler.send_note_async(midi_note)

SKILL_NAME = "auto_arpeggiator"
SKILL_DESCRIPTION = "Automatische Arpeggios aus User-Akkorden"
```

## 🐳 Docker Swarm Integration (Optional)

Für Heavy Processing (z.B. ML-Training) kannst du einen Raspi-Worker nutzen:

1. **Swarm Setup** (auf Raspi):
   ```bash
   docker swarm init
   ```

2. **Worker deployen**:
   ```bash
   docker service create --name music-ml-worker \
     -p 8080:8080 \
     your-pytorch-image
   ```

3. **Im Avatar** (zukünftige Feature):
   ```python
   # Sende Trainings-Daten an Worker
   await swarm_client.train_model(audio_files, target_style="jazz")

   # Empfange trainierte Weights
   weights = await swarm_client.get_weights()
   ```

## 🎨 Anpassungen

### Avatar-Farben ändern

In `avatar/gui/bass_clef_widget.py`:

```python
self._state_colors = {
    AvatarState.IDLE: QColor(100, 150, 255, 200),  # Deine Farbe
    # ...
}
```

### Eigene Skills hinzufügen

Erstelle eine `.py` Datei in `avatar/dynamic_tools/generated_skills/`:

```python
# my_custom_skill.py
async def execute_skill(midi_handler, ableton_connector, **kwargs):
    # Dein Code
    pass

SKILL_NAME = "my_skill"
SKILL_DESCRIPTION = "Was es tut"
```

Lade es im Lock Mode oder manuell:

```python
await mode_manager.load_skill(Path("path/to/my_custom_skill.py"))
await mode_manager.execute_skill("my_skill")
```

## 🐛 Troubleshooting

### Avatar startet nicht

```bash
# Check dependencies
python setup_avatar.py

# Check OSC Daemon läuft
python osc_daemon.py
```

### Kein MIDI Output

```bash
# Liste verfügbare Ports
python -c "import mido; print(mido.get_output_names())"

# Setze Port manuell in .env
MIDI_OUTPUT_PORT=dein_port_name
```

### KI antwortet nicht

```bash
# Check API Keys
echo $ANTHROPIC_API_KEY
echo $OPENAI_API_KEY

# Test Connection
python -c "from anthropic import Anthropic; print(Anthropic().messages.create(...))"
```

### OSC Verbindung fehlgeschlagen

```bash
# Check Daemon
netstat -an | grep 65432

# Restart Daemon
pkill -f osc_daemon.py
python osc_daemon.py
```

## 🚧 Roadmap

- [ ] **Audio-Analyse** mit `librosa` (FFT, Onset Detection)
- [ ] **Lokale Pattern-Erkennung** mit PyTorch LSTM
- [ ] **Docker Swarm Integration** für ML-Training
- [ ] **Drag & Drop** für Audio-Files (Learn by Files Mode)
- [ ] **Settings GUI** (PyQt6 Dialog)
- [ ] **Skill Store** (Teilen von generierten Skills)
- [ ] **Multi-Avatar** (mehrere Avatare gleichzeitig)

## 📚 Tech Stack

- **GUI**: PyQt6 (SVG-basiert, transparent)
- **Async**: qasync (Qt + asyncio)
- **AI**: LangChain + Anthropic/OpenAI
- **Audio**: python-osc, mido, librosa
- **ML**: PyTorch (optional)
- **Meta**: importlib (dynamisches Laden)

## 🙏 Credits

- [AbletonOSC](https://github.com/ideoforms/AbletonOSC) - OSC Implementation
- [MCP](https://modelcontextprotocol.io) - Model Context Protocol
- [LangChain](https://python.langchain.com/) - AI Framework
- Inspiration: Jazz-Musiker, die improvisieren und aufeinander reagieren 🎷

## 📄 Lizenz

MIT License - siehe `LICENSE` Datei

---

**Happy Jamming!** 🎵🤖

Bei Fragen oder Ideen: Erstelle ein Issue im GitHub Repo.
