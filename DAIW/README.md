# 🎵 DAIW - Digital AI Workspace

**The Ultimate AI-Powered Universal Workspace** ✨ **v2.0 - Quality of Life Edition**

DAIW is a revolutionary desktop application that transforms not just music production, but your entire creative workflow into an intelligent, collaborative, and interactive experience. Featuring an animated bass clef avatar, AI-powered tools, real-time collaboration, and now **universal assistant capabilities** - DAIW is your intelligent co-pilot for music, code, writing, research, and more!

---

## 🌟 What is DAIW?

**DAIW** (Digital AI Workspace) is an always-on-top desktop assistant that combines:

- 🤖 **AI-Powered Assistance** - Claude/GPT integration for musical intelligence
- 🎹 **Interactive Avatar** - Animated bass clef that responds to your workflow
- 🌐 **Real-Time Collaboration** - Work with producers worldwide via CollabNet Mode
- 🎥 **Advanced Audio Tools** - YouTube analysis, STEM separation, humming-to-MIDI
- 🔧 **Meta-Programming** - Avatar writes custom tools based on your workflow
- 🎨 **Visual Feedback** - See music theory and patterns come alive

### ✨ NEW in v2.0: Quality of Life Features

**Making DAIW the most convenient AI workspace ever!**

- ⌘ **Command Palette** - Instant access to everything (Cmd+K / Ctrl+K)
- ⌨️ **Keyboard Shortcuts** - Fully customizable hotkeys for all features
- 💾 **Presets System** - Save/load favorite configurations instantly
- ↶↷ **Undo/Redo** - Unlimited history with time-travel debugging
- 🖱️ **Drag & Drop** - Drop audio files, URLs, PDFs, images onto avatar
- 🎯 **System Tray** - Always-accessible from any application
- 🚀 **Global Hotkeys** - Trigger features even when app not focused
- 🌍 **Beyond Music** - Voice assistant, code helper, writing assistant, PDF reader, task manager
- 💡 **Smart Suggestions** - AI proactively suggests next steps
- 📋 **Recent Items** - Quick access to recent projects and actions

👉 **[Complete QoL Features Guide](docs/QOL_FEATURES.md)**
👉 **[Keyboard Shortcuts Reference](docs/KEYBOARD_SHORTCUTS.md)**

---

## 🚀 Key Features

### 🎭 Operating Modes

#### 💤 Idle Mode
Passive observation - perfect starting state

#### 🎸 Jam Mode
AI generates musical ideas in real-time (Call & Response)
- Melodic phrases
- Harmonic progressions
- Rhythm patterns

#### 👁️ Learn Mode
Observes and analyzes your playing style
- Records MIDI input
- Identifies patterns
- Learns harmonic preferences

#### 🔒 Lock Mode (Meta-Programming)
**The Game-Changer**: Avatar analyzes your workflow and writes Python code to automate it!
- Generates custom skills
- Loads modules dynamically
- Executes parallel to your work

Example: You always play chords on beat 1 and arpeggios on beat 2
→ Lock Mode creates `auto_arpeggiator.py`
→ Avatar now complements your playing automatically!

### 🧠 CollabNet Mode v1.5 ⚡ NEW!

**Real-Time Collaborative Music Production over WAN**

Work with other producers anywhere in the world with <100ms action mirroring:
- All Ableton actions synchronized (MIDI, tempo, tracks, etc.)
- Up to 16 users per session
- Integrated chat
- Password-protected sessions
- Visual user avatars

👉 **[Full Documentation](docs/COLLABNET_MODE.md)**

### 🎥 YouTube Reference Analyzer

Download and analyze songs from YouTube:
- Tempo detection (BPM)
- Key/scale identification
- Energy level analysis
- Style classification
- AI generates ideas in the analyzed style

👉 **[Feature Guide](docs/INTERACTIVE_FEATURES.md#youtube-analyzer)**

### ✂️ STEM Separator

Professional-grade source separation using Demucs:
- Extract: Vocals, Drums, Bass, Other
- Create instrumentals
- Isolate elements for analysis
- GPU-accelerated processing

👉 **[Feature Guide](docs/INTERACTIVE_FEATURES.md#stem-separator)**

### 🎤 Humming → MIDI

Sing or hum melodies, get MIDI notes:
- Real-time pitch detection (aubio YIN)
- Automatic MIDI conversion
- Playback as MIDI
- AI harmonization (planned)

👉 **[Feature Guide](docs/INTERACTIVE_FEATURES.md#humming-recorder)**

### 🌍 Universal Assistant Modes ⚡ NEW in v2.0!

**DAIW now goes beyond music!**

Expand your productivity with AI assistance for any task:

#### 💬 Voice Assistant
General AI assistant for anything:
- Answer questions on any topic
- Get information
- Conversational context memory
- Natural language interface

#### 💻 Code Assistant
Programming help for all languages:
- Explain any code
- Debug and fix errors
- Generate code from descriptions
- Refactor and optimize
- Python, JavaScript, Java, C++, and more!

#### ✍️ Writing Assistant
Improve your writing:
- Grammar and style improvements
- Brainstorm ideas
- Write articles, emails, blogs
- Summarize long texts
- Expand on concepts

#### 🖼️ Image Analysis
Visual AI capabilities:
- Describe images
- Object detection
- Text extraction (OCR)
- Style analysis
- Color palette extraction

#### 📄 PDF Reader
Smart document processing:
- Extract text from PDFs
- Summarize documents
- Answer questions about content
- Key points extraction

#### 🔍 Web Research
AI-powered research assistant:
- Research any topic
- Compile information
- Present findings
- Source recommendations

#### ✅ Task Manager
AI-powered productivity:
- Create and track tasks
- Priority management
- AI suggests subtasks
- Progress tracking
- Smart reminders

#### 📝 Note Taking
Intelligent note organization:
- Quick capture notes
- AI categorization
- Tag management
- Search and filter
- Auto-organization

**Access all modes via Command Palette (Ctrl+K) or System Tray!**

👉 **[Universal Assistant Guide](docs/QOL_FEATURES.md#beyond-music)**

---

## 🏗️ Architecture

```
DAIW/
├── daiw/                   # Main application
│   ├── gui/               # PyQt6 interface
│   │   ├── bass_clef_widget.py       # Animated avatar
│   │   ├── transparent_window.py     # Main window
│   │   ├── feature_dialogs.py        # Interactive features
│   │   ├── collabnet_dialogs.py      # Collaboration UI
│   │   ├── command_palette_dialog.py # Command palette UI ⚡NEW
│   │   └── system_tray.py            # System tray icon ⚡NEW
│   │
│   ├── brain/             # AI & Logic
│   │   ├── ai_controller.py          # LangChain integration
│   │   ├── mode_manager.py           # Mode coordination
│   │   ├── feature_manager.py        # Feature orchestration
│   │   ├── command_palette.py        # Command system ⚡NEW
│   │   ├── preset_manager.py         # Preset save/load ⚡NEW
│   │   ├── history_manager.py        # Undo/redo ⚡NEW
│   │   └── assistant_modes.py        # Universal assistant ⚡NEW
│   │
│   ├── audio/             # Audio/MIDI
│   │   ├── midi_handler.py           # MIDI I/O
│   │   ├── ableton_connector.py      # OSC bridge
│   │   ├── youtube_handler.py        # YouTube integration
│   │   ├── stem_separator.py         # Demucs wrapper
│   │   └── humming_detector.py       # Pitch detection
│   │
│   ├── utils/             # Utilities ⚡NEW
│   │   ├── config.py                 # Configuration
│   │   ├── shortcuts.py              # Keyboard shortcuts ⚡NEW
│   │   └── drag_drop.py              # Drag & drop handler ⚡NEW
│   │
│   ├── network/           # Collaboration
│   │   ├── collabnet_server.py       # WebSocket server
│   │   └── collabnet_client.py       # WebSocket client
│   │
│   ├── dynamic_tools/     # Music library & generated skills
│   │   ├── music_theory.py           # Harmony/rhythm toolkit
│   │   └── generated_skills/         # Auto-generated code
│   │
│   └── main.py            # Application entry point
│
├── docs/                  # Documentation
│   ├── ARCHITECTURE.md
│   ├── INTERACTIVE_FEATURES.md
│   ├── COLLABNET_MODE.md
│   ├── QOL_FEATURES.md               # QoL guide ⚡NEW
│   └── KEYBOARD_SHORTCUTS.md         # Shortcuts reference ⚡NEW
│
├── examples/              # Example workflows & skills
├── tests/                 # Test suite
└── requirements.txt       # Dependencies
```

👉 **[Architecture Details](docs/ARCHITECTURE.md)**

---

## 📦 Installation

### Prerequisites

- **Python 3.10+**
- **Ableton Live** with [AbletonOSC](https://github.com/ideoforms/AbletonOSC)
- **OS**: Windows, macOS, or Linux
- **Optional**: MIDI controller, Audio interface, GPU (for STEM separation)

### Quick Start

```bash
# 1. Clone repository
git clone https://github.com/yourusername/DAIW.git
cd DAIW

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up API keys
cp .env.template .env
# Edit .env and add your API keys:
#   ANTHROPIC_API_KEY=your_key
#   or OPENAI_API_KEY=your_key

# 4. Start OSC daemon (Terminal 1)
python osc_daemon.py

# 5. Start DAIW (Terminal 2)
python -m daiw.main
```

### Configuration

Create `.env` file:

```env
# AI Provider (anthropic or openai)
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-xxx
OPENAI_API_KEY=sk-xxx

# CollabNet Server (optional)
COLLABNET_SERVER=ws://localhost:8765
```

---

## 🎮 Usage

### Basic Interaction

- **Right-click avatar** → Context menu
- **Left-click + drag** → Move avatar
- **Double-click** → Cycle through modes

### Context Menu

```
🎸 Freestyle Jam
👁️ Learn by Watching
🔒 Lock Mode (Meta-Programming)
💤 Idle
───────────────────────
✨ Interactive Features
🎥 Analyze YouTube Song
✂️ Separate STEM
🎤 Hum → MIDI
───────────────────────
🧠 CollabNet Mode
───────────────────────
⚙️ Settings
❌ Exit
```

### Workflows

#### Workflow 1: Learn from Reference
```
1. YouTube Analyzer → Analyze "Daft Punk - Get Lucky"
2. Jam Mode → Avatar jams in the detected style (116 BPM, F# minor)
3. Learn Mode → Record your variations
4. Lock Mode → Generate auto-accompaniment skill
```

#### Workflow 2: Collaborative Production
```
1. Start CollabNet Server
2. Create session "Beat Making"
3. Friend joins from another city
4. Jam together in real-time
5. All actions synchronized (<100ms)
```

#### Workflow 3: Vocal Processing
```
1. STEM Separator → Extract vocals from song
2. Humming Recorder → Record your melody idea
3. AI → Harmonize your melody
4. Ableton → Import both and blend
```

---

## 🛠️ Tech Stack

### Core Technologies
- **Python 3.10+** - Main language
- **PyQt6** - GUI framework
- **qasync** - Qt + asyncio integration
- **websockets** - Real-time collaboration

### AI & Music
- **LangChain** - AI orchestration
- **Anthropic Claude / OpenAI GPT** - Musical intelligence
- **librosa** - Audio analysis
- **aubio** - Pitch detection
- **Demucs** - Source separation

### MIDI & Audio
- **mido** - MIDI I/O
- **python-osc** - Ableton communication
- **sounddevice** - Audio recording
- **yt-dlp** - YouTube download

### Optional
- **PyTorch** - Pattern recognition
- **Docker** - CollabNet server deployment

---

## 🌐 CollabNet Server Deployment

### Local Testing
```bash
python daiw/network/collabnet_server.py
```

### Cloud Deployment (DigitalOcean)
```bash
# On your VPS
apt update && apt install python3 python3-pip
pip3 install websockets

# Run with systemd
sudo systemctl enable daiw-collabnet
sudo systemctl start daiw-collabnet
```

### Docker
```bash
docker run -d -p 8765:8765 daiw/collabnet-server
```

👉 **[Deployment Guide](docs/COLLABNET_MODE.md#deployment)**

---

## 🎓 Music Theory Library

DAIW includes a comprehensive music theory toolkit:

```python
from daiw.dynamic_tools.music_theory import *

# Create chords
chord = create_chord(60, ChordType.MAJOR)  # [60, 64, 67]

# Generate arpeggios
arp = create_arpeggio(chord, "up-down", octaves=2)

# Get scale notes
scale = get_scale_notes(60, Scale.MAJOR, octaves=2)

# Apply progressions
progression = apply_progression(60, Scale.MAJOR, "I-V-vi-IV")
```

Over 300 lines of musical building blocks for AI-generated skills!

---

## 🤝 Use Cases

### For Producers
- AI co-producer that learns your style
- Real-time collaboration worldwide
- Reference analysis (YouTube)
- Idea capture (humming)

### For Teachers
- Demonstrate workflows to students remotely
- Real-time feedback during lessons
- Visual music theory demonstrations

### For Bands
- Rehearse remotely with full DAW sync
- Jam sessions across continents
- Share ideas instantly

### For Engineers
- Collaborate on mixing remotely
- Isolate stems for processing
- Live feedback during sessions

---

## 🗺️ Roadmap

### v1.6 (Next Release)
- [ ] WebRTC P2P data channels (ultra-low latency)
- [ ] End-to-end encryption (CollabNet)
- [ ] Voice chat integration
- [ ] Mobile companion app (iOS/Android)
- [ ] FL Studio / Logic Pro support

### v2.0 "DAIW Pro"
- [ ] VST/AU plugin version
- [ ] Cloud project storage
- [ ] AI-powered mastering
- [ ] Marketplace for generated skills
- [ ] VR/AR avatar interaction

### v3.0 "DAIW Universe"
- [ ] Blockchain-based collaboration
- [ ] NFT session recordings
- [ ] Metaverse integration
- [ ] Multi-DAW orchestration
- [ ] AI band members

---

## 📊 Performance

- **Latency**: <100ms action mirroring (CollabNet)
- **GUI**: 60 FPS animations
- **Audio**: Real-time pitch detection
- **AI**: <2s response time (Claude/GPT)
- **STEM**: 30-60s separation (GPU)
- **YouTube**: 10-30s download + analysis

---

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Specific modules
pytest tests/test_music_theory.py
pytest tests/test_collabnet_client.py

# With coverage
pytest --cov=daiw tests/
```

---

## 🤝 Contributing

We welcome contributions! Areas we're looking for help:

- **CollabNet WebRTC implementation**
- **Additional DAW integrations** (Logic, FL Studio, Bitwig)
- **Mobile clients** (iOS/Android)
- **Plugin format** (VST/AU)
- **Documentation translations**
- **Example skills & workflows**

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file

---

## 🙏 Credits

### Built With
- [AbletonOSC](https://github.com/ideoforms/AbletonOSC) - Ableton integration
- [Demucs](https://github.com/facebookresearch/demucs) - Source separation
- [LangChain](https://python.langchain.com/) - AI framework
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - GUI framework

### Inspiration
- Jazz musicians who improvise and respond to each other
- Google Docs-style real-time collaboration
- The concept of AI as a creative partner, not just a tool

---

## 📞 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/yourusername/DAIW/issues)
- **Discord**: [DAIW Community](https://discord.gg/daiw)
- **Email**: support@daiw.ai

---

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/DAIW&type=Date)](https://star-history.com/#yourusername/DAIW&Date)

---

<p align="center">
  <strong>Built with ❤️ for musicians, by musicians</strong><br>
  <sub>DAIW - Where AI meets creativity</sub>
</p>

<p align="center">
  <a href="#-what-is-daiw">Features</a> •
  <a href="#-installation">Install</a> •
  <a href="#-usage">Usage</a> •
  <a href="docs/">Docs</a> •
  <a href="#-roadmap">Roadmap</a>
</p>

---

**Start creating music with AI today!** 🎵🤖
