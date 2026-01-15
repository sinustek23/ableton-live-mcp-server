# 🚀 DAIW Quick Start Guide

Get up and running with DAIW (Digital AI Workspace) in 5 minutes!

## Prerequisites

- Python 3.10 or higher
- Ableton Live (any version)
- Virtual MIDI port (loopMIDI on Windows, IAC Driver on macOS, virmidi on Linux)
- AI API key (Anthropic Claude or OpenAI)

## Installation Steps

### 1. Clone & Install

```bash
cd /home/user/ableton-live-mcp-server/DAIW
pip install -e .
```

Or install from requirements:
```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the template and fill in your values:
```bash
cp .env.template .env
nano .env  # or your preferred editor
```

**Required settings:**
```bash
# AI Provider (choose one)
ANTHROPIC_API_KEY=sk-ant-your-key-here
# OR
OPENAI_API_KEY=sk-your-key-here

# Choose provider
AI_PROVIDER=anthropic  # or openai
AI_MODEL=claude-3-5-sonnet-20241022  # or gpt-4

# OSC Daemon
OSC_DAEMON_HOST=127.0.0.1
OSC_DAEMON_PORT=65432
```

### 3. Set Up Ableton Live

1. **Install AbletonOSC:**
   - Download from: https://github.com/ideoforms/AbletonOSC
   - Place in `Ableton/User Library/Remote Scripts/`
   - Restart Ableton

2. **Configure Control Surface:**
   - Preferences → Link/Tempo/MIDI
   - Control Surface: Select "AbletonOSC"
   - Input/Output: Select your MIDI ports

3. **Create Virtual MIDI Port:**
   - **Windows**: Install loopMIDI, create port "DAIW Port"
   - **macOS**: IAC Driver (already installed)
   - **Linux**: `modprobe snd-virmidi`

### 4. Start OSC Daemon

In a separate terminal:
```bash
cd /home/user/ableton-live-mcp-server
python osc_daemon.py
```

You should see:
```
[OSC Daemon] Starting on localhost:65432...
[OSC Daemon] Ready to accept connections
```

### 5. Launch DAIW

```bash
daiw
```

Or:
```bash
python -m daiw.main
```

You should see the bass clef avatar appear on your screen!

## First Steps

### 1. Right-Click the Avatar

Access the context menu to:
- Switch modes (Jam, Learn, Lock)
- Access interactive features
- Open settings

### 2. Try Jam Mode

1. Right-click → **"🎸 Freestyle Jam"**
2. Avatar starts generating musical ideas
3. Ideas are sent to Ableton via MIDI

### 3. Try Learn Mode

1. Right-click → **"👁️ Learn by Watching"**
2. Play something on your MIDI keyboard
3. Avatar analyzes your playing style
4. Switch to Jam mode to hear it adapt

### 4. Try YouTube Analyzer

1. Right-click → **"🎥 Analyze YouTube Song"**
2. Enter a YouTube URL or search term
3. Wait for analysis (BPM, key, style)
4. Click "Copy Style to Jam Mode"

## Troubleshooting

### Avatar doesn't appear
- Check Python version: `python --version` (must be 3.10+)
- Check PyQt6 installation: `pip show PyQt6`
- Run with debug: `DEBUG=true python -m daiw.main`

### No MIDI output
- Verify virtual MIDI port exists
- Check `.env` MIDI settings
- Test with: `python -c "import mido; print(mido.get_output_names())"`

### OSC connection failed
- Ensure `osc_daemon.py` is running
- Check port 65432 is not in use: `netstat -an | grep 65432`
- Verify Ableton has AbletonOSC installed

### AI not responding
- Verify API key in `.env`
- Check internet connection
- Test API: `curl https://api.anthropic.com/v1/messages -H "x-api-key: YOUR_KEY"`

## Next Steps

- **Read full docs:** `docs/ARCHITECTURE.md`, `docs/INTERACTIVE_FEATURES.md`
- **Try Neuralink Mode:** `docs/NEURALINK_MODE.md` for collaborative sessions
- **Lock Mode:** Create custom skills via meta-programming
- **STEM Separator:** Extract vocals, drums, bass from songs
- **Humming Recorder:** Sing melodies, convert to MIDI

## Common Commands

```bash
# Start DAIW
daiw

# Start Neuralink server
daiw-server

# Run tests
pytest

# Check installation
python -c "import daiw; print(daiw.__version__)"
```

## Getting Help

- **Documentation:** Check `docs/` folder
- **GitHub Issues:** Report bugs and feature requests
- **Configuration:** All settings in `.env` file

---

**Have fun making music with DAIW!** 🎵🤖
