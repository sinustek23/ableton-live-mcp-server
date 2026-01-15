# 🎵 Interactive Features Update

Der Avatar wurde mit **drei mächtigen interaktiven Features** erweitert, die ihn zu einem echten Musik-Produktions-Assistenten machen!

## 🆕 Neue Features

### 1. 🎥 YouTube Reference Analyzer

**Analysiere YouTube-Songs und kopiere ihren Stil!**

#### Was es kann:
- YouTube-Videos downloaden (URL oder Suchbegriff)
- Audio extrahieren und analysieren:
  - Tempo (BPM) Erkennung
  - Key/Tonart Detection
  - Energy-Level Analyse
  - Stil-Klassifizierung
- KI-generierte musikalische Ideen im Stil des analysierten Songs

#### Verwendung:

1. **Rechtsklick auf Avatar** → `🎥 Analyze YouTube Song`
2. URL oder Suchbegriff eingeben:
   - Direkter Link: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
   - Suche: `Daft Punk Get Lucky`
3. Warten auf Download & Analyse
4. Ergebnisse ansehen:
   ```
   Tempo: 116.0 BPM
   Key: F# minor
   Energy: 0.245
   Style: medium tempo
   ```
5. Optional: `Copy Style to Jam Mode` → Avatar jammt im analysierten Stil!

#### Technische Details:
- `yt-dlp` für YouTube-Download
- `librosa` für Audio-Analyse
- Tempo-Detection via Beat-Tracking
- Chroma-Features für Key-Detection
- LangChain-Integration für Stil-Prompts

#### Code:
```python
# YouTube Handler
handler = YouTubeHandler()
track = await handler.download_and_analyze("Daft Punk Get Lucky")

print(f"Tempo: {track.tempo} BPM")
print(f"Key: {track.key}")

# AI Style Prompt
prompt = await handler.extract_style_prompt(track)
idea = await ai.generate_musical_idea(prompt)
```

---

### 2. ✂️ STEM Separator

**Separiere Audio in Vocals, Drums, Bass, Other!**

#### Was es kann:
- Audio-Files in einzelne Stems trennen mit **Demucs** (State-of-the-Art ML)
- Unterstützte Stems:
  - 🎤 Vocals
  - 🥁 Drums
  - 🎸 Bass
  - 🎹 Other (Synths, Piano, etc.)
- Wahlweise einzelne oder alle Stems extrahieren
- Instrumental-Mix erstellen (ohne Vocals)

#### Verwendung:

1. **Rechtsklick auf Avatar** → `✂️ Separate STEM`
2. Audio-File auswählen (MP3, WAV, FLAC, etc.)
3. Stems wählen (z.B. nur Vocals oder alle)
4. `Separate` klicken
5. Stems werden gespeichert in `/tmp/music_copilot_stems/<filename>/`

#### Use Cases:
- **Learn from Vocals**: Extrahiere Vocals → Analysiere Melodie
- **Drums als Reference**: Nutze Drum-Stem für Rhythm-Analysis
- **Karaoke**: Erstelle Instrumental-Version
- **Remix**: Nutze einzelne Stems in Ableton

#### Technische Details:
- **Demucs** (htdemucs model) - hochqualitative Source Separation
- GPU-Support (CUDA) falls verfügbar
- Fortschrittsanzeige während Separation
- Automatisches Cleanup alter Stems

#### Code:
```python
# STEM Separator
separator = STEMSeparator()
stems = await separator.separate(Path("song.mp3"))

# Vocals nur
vocals = await separator.get_vocals(Path("song.mp3"))

# Instrumental (ohne Vocals)
instrumental = await separator.get_instrumental(Path("song.mp3"))
```

---

### 3. 🎤 Humming → MIDI Recorder

**Summe eine Melodie, Avatar spielt sie als MIDI!**

#### Was es kann:
- **Echtzeit-Aufnahme** von Stimme/Summen/Pfeifen
- **Pitch Detection** (aubio YIN algorithm)
- Konvertierung zu **MIDI-Noten**
- **Echtzeit-Anzeige** der gesungenen Note
- **Playback** der erkannten Melodie
- Harmonisierung durch KI (coming soon)

#### Verwendung:

1. **Rechtsklick auf Avatar** → `🎤 Hum → MIDI`
2. Input Device wählen (Mikrofon)
3. Sensitivity einstellen (0.1 - 1.0)
4. `⏺️ Start Recording` klicken
5. Melodie summen/singen/pfeifen
6. `⏹️ Stop Recording` klicken
7. Erkannte Noten ansehen:
   ```
   Detected 8 notes:
   1. C4 (0.5s)
   2. D4 (0.3s)
   3. E4 (0.4s)
   ...
   ```
8. `▶️ Play Back as MIDI` → Avatar spielt die Melodie!

#### Echtzeit-Feedback:
Während der Aufnahme siehst du:
```
🎵 C4 (261.6 Hz)
```

#### Use Cases:
- **Melodie-Skizzen**: Ideen schnell festhalten
- **Call & Response**: Avatar antwortet auf deine Melodie
- **Harmonisierung**: KI ergänzt Akkorde zu deiner Melodie
- **MIDI-Input ohne Keyboard**: Summen statt Spielen

#### Technische Details:
- **sounddevice** für Audio-Recording
- **aubio** für Pitch-Detection (YIN algorithm)
- Real-time Processing mit asyncio
- Silence-Threshold für saubere Note-Segmentierung
- Hz → MIDI Konvertierung

#### Code:
```python
# Humming Detector
detector = HummingDetector()

# Start recording
await detector.start_recording()
await asyncio.sleep(5)  # Record for 5 seconds

# Stop and get phrase
phrase = await detector.stop_recording()

# Play back
midi_handler = MIDIHandler()
await detector.play_back_as_midi(phrase, midi_handler)
```

---

## 🎯 Feature-Architektur

### Neue Module:

```
avatar/
├── audio/
│   ├── youtube_handler.py       # YouTube Download & Analysis
│   ├── stem_separator.py        # Demucs STEM Separation
│   └── humming_detector.py      # Pitch Detection & MIDI Conversion
├── brain/
│   └── feature_manager.py       # Feature-Koordination
└── gui/
    └── feature_dialogs.py       # PyQt6 Dialogs
```

### Feature Manager

Der `InteractiveFeatureManager` koordiniert alle Features:

```python
feature_manager = InteractiveFeatureManager(ai_controller, midi_handler)

# YouTube
track = await feature_manager.analyze_youtube_song("search query")
idea = await feature_manager.generate_from_youtube_style()

# STEM
stems = await feature_manager.separate_stems(audio_file)

# Humming
await feature_manager.start_humming_recording()
phrase = await feature_manager.stop_humming_recording()
await feature_manager.playback_humming_as_midi()
```

---

## 🖱️ GUI Integration

### Erweiterte Context-Menu:

```
🎸 Freestyle Jam
👁️ Learn by Watching
🔒 Lock Mode (Meta-Programming)
💤 Idle
-------------------
✨ Interactive Features...      (Feature-Auswahl Dialog)
🎥 Analyze YouTube Song        (Direkter Zugriff)
✂️ Separate STEM              (Direkter Zugriff)
🎤 Hum → MIDI                  (Direkter Zugriff)
-------------------
⚙️ Settings
❌ Exit
```

### Dialogs:

Alle Features haben eigene **PyQt6 Dialogs** mit:
- Progress Bars
- Echtzeit-Status
- Ergebnis-Anzeige
- Weitere Aktionen

---

## 📦 Neue Dependencies

```bash
# YouTube
yt-dlp==2024.4.9

# STEM Separation
demucs==4.0.1

# Audio Recording & Pitch Detection
sounddevice==0.4.6
aubio==0.4.9
pydub==0.25.1
resampy==0.4.2
```

Installation:
```bash
pip install -r requirements.txt

# Oder selektiv
pip install yt-dlp demucs sounddevice aubio pydub
```

---

## 🚀 Beispiel-Workflows

### Workflow 1: "Learn from a Song"

1. **YouTube Analyzer**: Analysiere Reference-Track
   ```
   Input: "John Mayer Slow Dancing"
   Output: Tempo 90 BPM, Key A Major, Medium Energy
   ```

2. **STEM Separator**: Extrahiere Vocals
   ```
   Input: Downloaded track
   Output: vocals.wav
   ```

3. **Jam Mode**: Avatar generiert im analysierten Stil
   ```
   Style: Slow ballad, A Major, 90 BPM
   ```

### Workflow 2: "Capture & Expand Melody"

1. **Humming Recorder**: Summe Melodie
   ```
   Input: 🎵 (summen)
   Output: C4-D4-E4-G4 (MIDI)
   ```

2. **AI Harmonization**: KI ergänzt Harmonien
   ```
   Input: Detected melody
   Output: Chord progression + Bass line
   ```

3. **Learn Mode**: Avatar adaptiert deinen Stil
   ```
   Avatar lernt: "User mag aufsteigende Melodien"
   ```

### Workflow 3: "Remix Builder"

1. **STEM Separator**: Trenne Song in Stems
   ```
   Output: vocals.wav, drums.wav, bass.wav, other.wav
   ```

2. **Humming**: Summe neue Melodie
   ```
   Input: 🎵 (neue Idee)
   Output: MIDI notes
   ```

3. **Lock Mode**: Avatar erstellt Auto-Remix Skill
   ```
   Skill: Kombiniert Original-Drums mit neuer Melodie
   ```

---

## 🎮 Keyboard Shortcuts (geplant)

```
Ctrl+Y : YouTube Analyzer
Ctrl+S : STEM Separator
Ctrl+H : Humming Recorder
Ctrl+Space : Quick Feature Menu
```

---

## 🔮 Zukünftige Erweiterungen

### YouTube Analyzer:
- [ ] Playlist-Support (ganze Playlists analysieren)
- [ ] Style-Transfer (Song A im Stil von Song B)
- [ ] Automatic Skill Generation basierend auf Song

### STEM Separator:
- [ ] 6-Stem Model (separate Gitarre + Piano)
- [ ] Direkt in Ableton Live importieren
- [ ] STEM-basierte Loop-Erkennung

### Humming Detector:
- [ ] Multi-Track Recording (Harmonien selbst einsingen)
- [ ] Auto-Quantization zu Grid
- [ ] Vibrato & Expression erkennen
- [ ] Lyrics-to-Melody (Text singen → Melodie + Lyrics)

### Neue Features:
- [ ] **Beat Maker**: Beatbox → Drum Pattern
- [ ] **Loop Finder**: Finde ähnliche Loops in Library
- [ ] **Genre Classifier**: Erkenne Genre aus Audio
- [ ] **Chord Recognizer**: Akkorde aus Audio extrahieren

---

## 🛠️ Troubleshooting

### YouTube Download schlägt fehl:
```bash
# Update yt-dlp
pip install --upgrade yt-dlp

# Check ffmpeg
ffmpeg -version
```

### STEM Separation zu langsam:
```bash
# Check GPU
python -c "import torch; print(torch.cuda.is_available())"

# Nutze kleineres Model
separator = STEMSeparator(model_name="htdemucs_ft")
```

### Humming Detection ungenau:
1. Lauter summen/singen
2. Sensitivity erhöhen (0.7-0.9)
3. Besseres Mikrofon nutzen
4. Hintergrundgeräusche minimieren

### Keine Audio Input Devices:
```bash
# List devices
python -c "import sounddevice as sd; print(sd.query_devices())"

# Test Recording
python -c "import sounddevice as sd; print(sd.rec(44100, blocking=True))"
```

---

## 💡 Pro-Tips

1. **YouTube**: Nutze hochqualitative Videos (mind. 192 kbps Audio)
2. **STEM**: GPU macht Separation 10x schneller
3. **Humming**: Klare, stabile Töne funktionieren besser als vibrato
4. **Kombination**: YouTube Analyzer → STEM Separator → Lock Mode für maximale Power!

---

**Die Möglichkeiten sind endlos!** 🚀

Probiere die Features aus und erschaffe etwas Einzigartiges! 🎵
