# 🧠 Neuralink Mode v1.5

**Real-Time Collaborative Music Production über WAN** - Arbeite mit anderen Produzenten zusammen, egal wo sie sind!

## 🎯 Konzept

Neuralink Mode verwandelt den DAIW (Digital AI Workspace) in einen **kollaborativen Hub**, der mehrere Benutzer über das Internet (WAN) verbindet. **Alle Ableton-Aktionen werden in Echtzeit synchronisiert** - wenn User A einen MIDI-Track bearbeitet, sieht User B die Änderungen sofort!

### Was ist das Besondere?

- 🌐 **WAN-Support**: Zusammenarbeit über Internet, nicht nur lokales Netzwerk
- ⚡ **Echtzeit-Synchronisation**: <100ms Latenz für Action-Mirroring
- 🎭 **Avatar-Visualisierung**: Sieh die Avatare der anderen User & ihre Aktionen
- 🔒 **Session-basiert**: Erstelle private Sessions mit Passwortschutz
- 👥 **Multi-User**: Bis zu 16 Produzenten gleichzeitig
- 💬 **Integrated Chat**: Kommuniziere während der Session

## 🏗️ Architektur

### Hybrid Approach: Server + P2P

```
User A (Berlin)          Neuralink Server          User B (London)
    Avatar  ←──WebSocket──→  (Signaling)  ←──WebSocket──→  Avatar
       │                                                       │
       └───────────────Action Mirroring──────────────────────┘
```

**Komponenten:**

1. **Neuralink Server** (`neuralink_server.py`)
   - WebSocket Server für Session Management
   - Action-Routing zwischen Clients
   - User Authentication & Authorization

2. **Neuralink Client** (`neuralink_client.py`)
   - WebSocket Client im Avatar integriert
   - Action Serialization & Deserialization
   - Local Action Buffering

3. **GUI** (`neuralink_dialogs.py`)
   - Session erstellen/beitreten
   - User-Liste & Status
   - Chat

## 🚀 Verwendung

### 1. Neuralink Server starten

**Option A: Lokaler Server (für Tests)**
```bash
python daiw/network/neuralink_server.py
```
Server läuft auf `ws://localhost:8765`

**Option B: Public Server (für WAN)**
```bash
# Mit öffentlicher IP
python daiw/network/neuralink_server.py --host 0.0.0.0 --port 8765
```

**Option C: Cloud Server (Empfohlen für Produktion)**
```bash
# Auf VPS/Cloud-Server (z.B. AWS, DigitalOcean)
sudo python daiw/network/neuralink_server.py --host 0.0.0.0 --port 8765
```

### 2. Avatar verbinden

1. **Rechtsklick auf Avatar** → `🧠 Neuralink Mode`
2. **Connect Dialog**:
   - Server: `ws://server-ip:8765`
   - Username: Dein Producer-Name
   - Color: Avatar-Farbe (#hex)
3. `Connect` klicken

### 3. Session erstellen oder beitreten

**Session erstellen:**
1. Tab `Create Session`
2. Session Name eingeben (z.B. "Beat Making Session")
3. Optional: Passwort für private Session
4. Max Users wählen (2-16)
5. `Create Session` klicken

**Session beitreten:**
1. Tab `Join Session`
2. `Refresh Sessions` klicken
3. Session aus Liste wählen
4. Optional: Passwort eingeben
5. `Join Session` klicken

### 4. Kollaborativ arbeiten!

**Alle Aktionen werden automatisch synchronisiert:**
- 🎹 MIDI-Noten spielen
- 🎛️ Tempo ändern
- 🔇 Tracks muten/solo/armen
- 🎬 Scenes/Clips triggern
- 🎨 Avatar-Modi wechseln
- 💬 Chat-Nachrichten

## 🎮 Synchronisierte Actions

### MIDI Actions
```python
# User A spielt Note → User B sieht/hört es
await client.send_midi_note(note=60, velocity=100, duration=0.5)
```

### Ableton Actions
```python
# User A ändert Tempo → User B's Ableton folgt
await client.send_tempo_change(tempo=128.0)

# Track muten
await client.send_action(ActionType.TRACK_MUTE, {"track": 1, "mute": True})

# Scene triggern
await client.send_action(ActionType.SCENE_TRIGGER, {"scene": 2})
```

### Avatar Actions
```python
# Mode wechseln → Andere sehen es
await client.send_mode_change(mode="jam")

# Feature nutzen
await client.send_action(ActionType.FEATURE_USE, {"feature": "youtube", "action": "analyze"})
```

### Chat
```python
# Nachricht an alle
await client.send_chat_message("Let's add drums here!")
```

## 🎨 Remote Avatar Visualisierung

Jeder verbundene User wird als **Ghost Avatar** visualisiert:

```
┌─────────────────────────┐
│  Your Avatar (Green)    │  ← Du
├─────────────────────────┤
│  Remote User 1 (Red)    │  ← User in Berlin
│  Playing: C4 → E4       │
├─────────────────────────┤
│  Remote User 2 (Blue)   │  ← User in London
│  Mode: Learn            │
└─────────────────────────┘
```

**Ghost Avatare zeigen:**
- Username & Farbe
- Letzte Aktion
- Aktueller Mode
- Echtzeit-Position

## 🔒 Security & Permissions

### Authentication
- Jeder Client authentifiziert sich mit Username
- Server vergibt eindeutige User IDs

### Session Permissions
- **Host**: Kann Session löschen, Users kicken (geplant)
- **Member**: Kann alle Actions ausführen
- **Password Protection**: Optional für private Sessions

### Encryption (Geplant v1.6)
- TLS/SSL für WebSocket (wss://)
- End-to-End Encryption für sensible Actions

## 📊 Technische Details

### WebSocket Protocol

**Message Format:**
```json
{
  "type": "action",
  "session_id": "uuid",
  "action": {
    "action_id": "uuid",
    "action_type": "midi_note_on",
    "user_id": "uuid",
    "timestamp": 1234567890.123,
    "data": {
      "note": 60,
      "velocity": 100,
      "duration": 0.5
    }
  }
}
```

### Action Types

```python
class ActionType(Enum):
    # MIDI
    MIDI_NOTE_ON = "midi_note_on"
    MIDI_NOTE_OFF = "midi_note_off"
    MIDI_CC = "midi_cc"

    # Ableton
    TEMPO_CHANGE = "tempo_change"
    TRACK_MUTE = "track_mute"
    TRACK_SOLO = "track_solo"
    TRACK_ARM = "track_arm"
    SCENE_TRIGGER = "scene_trigger"
    CLIP_TRIGGER = "clip_trigger"

    # Avatar
    MODE_CHANGE = "mode_change"
    FEATURE_USE = "feature_use"

    # Session
    USER_JOIN = "user_join"
    USER_LEAVE = "user_leave"
    CHAT_MESSAGE = "chat_message"
```

### Conflict Resolution

**Last-Write-Wins (LWW)** mit Timestamps:
- Jede Action hat einen Timestamp
- Bei Konflikten gewinnt die spätere Action
- Funktioniert gut für unabhängige Parameter (Tempo, Track-Mutes)

**Operational Transformation (geplant v1.6):**
- Für komplexe Edits (MIDI-Clips, Automation)
- Konflikt-freie Zusammenarbeit an demselben Clip

### Performance

- **Latenz**: <100ms für Action-Mirroring (abhängig von Netzwerk)
- **Bandbreite**: ~10-50 KB/s pro User bei aktiver Nutzung
- **Skalierung**: Server kann 50+ gleichzeitige Sessions handeln

## 🌐 NAT Traversal & Firewall

### Problem: Beide Users hinter NAT/Firewall

**Lösung 1: Public Server (Empfohlen)**
- Nutze Cloud-Server (AWS, DigitalOcean, Linode)
- Server hat öffentliche IP
- Beide Clients verbinden sich zu Server
- Server routet Actions

**Lösung 2: Port Forwarding**
- Ein User hosted den Server
- Router Port Forwarding einrichten: Port 8765 → Local IP
- Andere User verbinden sich zu `ws://public-ip:8765`

**Lösung 3: Ngrok/Localtunnel (Für Tests)**
```bash
# Ngrok installieren
ngrok http 8765

# URL teilen (z.B. ws://abc123.ngrok.io)
```

## 🎯 Use Cases

### 1. Remote Jam Session
```
User A (Berlin): Spielt Drums
User B (London): Spielt Bass
User C (NYC):    Spielt Melodie

→ Alle hören sich in Echtzeit und jammen zusammen!
```

### 2. Mixing/Mastering Feedback
```
Producer sendet Mix → Engineer joined Session
Engineer: "Kick zu leise" (Chat)
Producer: Hebt Kick-Level → Engineer sieht Änderung sofort
```

### 3. Teaching/Learning
```
Lehrer erstellt Session
Schüler joined
Lehrer demonstriert Workflow → Schüler sieht jeden Schritt
```

### 4. Songwriting Collaboration
```
User A schreibt Akkorde → User B ergänzt Melodie
User C fügt Drums hinzu → User D tunt Arrangement
→ Song entsteht in Echtzeit!
```

## 🔧 Server Setup (Production)

### Option 1: DigitalOcean Droplet

```bash
# 1. Create Droplet (Ubuntu 22.04, $5/month)
# 2. SSH in
ssh root@your-droplet-ip

# 3. Install Python & Dependencies
apt update && apt install python3.10 python3-pip
pip3 install websockets

# 4. Copy server file
scp daiw/network/neuralink_server.py root@your-droplet-ip:/root/

# 5. Run with systemd
cat > /etc/systemd/system/neuralink.service <<EOF
[Unit]
Description=Neuralink Collaboration Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root
ExecStart=/usr/bin/python3 /root/neuralink_server.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 6. Start service
systemctl enable neuralink
systemctl start neuralink

# 7. Check status
systemctl status neuralink
```

### Option 2: Docker Container

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app
RUN pip install websockets

COPY daiw/network/neuralink_server.py .

EXPOSE 8765

CMD ["python", "neuralink_server.py"]
```

```bash
# Build & Run
docker build -t neuralink-server .
docker run -d -p 8765:8765 --name neuralink neuralink-server
```

### Option 3: AWS Lambda + API Gateway (Serverless)

*Coming in v1.6*

## 🐛 Troubleshooting

### Connection failed
```
Problem: Can't connect to server
Solutions:
1. Check server is running: netstat -an | grep 8765
2. Check firewall: sudo ufw allow 8765
3. Try localhost first: ws://localhost:8765
4. Check server logs
```

### High Latency
```
Problem: Actions delayed >500ms
Solutions:
1. Use server closer to users (same region)
2. Check network: ping server-ip
3. Reduce action rate (buffer/throttle)
4. Use P2P DataChannels (v1.6)
```

### Actions not syncing
```
Problem: Remote user doesn't see actions
Solutions:
1. Check both users in same session
2. Check WebSocket connection: client.is_connected()
3. Check server logs for errors
4. Refresh session
```

### Server crashed
```
Problem: Server stops responding
Solutions:
1. Check server logs
2. Restart server
3. Check system resources (RAM/CPU)
4. Limit max users per session
```

## 🗺️ Roadmap

### v1.6 (Next Release)
- [ ] End-to-End Encryption
- [ ] WebRTC DataChannels für P2P (Ultra-Low-Latency)
- [ ] STUN/TURN Server Integration
- [ ] Operational Transformation für MIDI-Clips
- [ ] Permission System (Read-Only Users)
- [ ] Session Recording & Playback

### v1.7
- [ ] Voice Chat Integration
- [ ] Video Streaming (Screen Share)
- [ ] Ableton Project Sync (Download/Upload)
- [ ] Plugin State Sync
- [ ] Collaborative Loop Library

### v2.0 - "Neuralink Pro"
- [ ] Blockchain-basierte Sessions (Web3)
- [ ] NFT für Session-Recordings
- [ ] AI-Moderator (Avatar-hosted Sessions)
- [ ] VR-Support (VR-Avatar Interaction)
- [ ] DAW-agnostisch (Logic Pro, FL Studio, etc.)

## 💡 Pro-Tips

1. **Low-Latency Setup**: Beide Users nutzen Server in derselben Region
2. **Bandwidth sparen**: Limitiere Actions auf wichtige (kein Cursor-Movement)
3. **Session Organization**: Nutze klare Session-Namen & Passwörter
4. **Communication**: Nutze Chat für Koordination vor großen Changes
5. **Host Responsibility**: Host sollte stable Connection haben
6. **Backup**: Speichere Ableton-Projekt lokal (Server speichert keine DAW-Files)

## 🎓 Advanced: Custom Actions

Erstelle eigene Action Types für spezielle Workflows:

```python
# Definiere Custom Action
class CustomActionType(Enum):
    SEND_LOOP = "send_loop"
    SHARE_PLUGIN_PRESET = "share_plugin_preset"

# Sende Custom Action
await client.send_action(CustomActionType.SEND_LOOP, {
    "loop_data": base64_encoded_audio,
    "bpm": 120,
    "key": "Am"
})

# Handle Custom Action (Client-Side)
async def on_action(action: CollaborativeAction):
    if action.action_type == "send_loop":
        loop_data = action.data["loop_data"]
        # Process & import loop
```

## 📚 API Reference

### NeuralinkClient

```python
client = NeuralinkClient(username="Producer", color="#00ff00")

# Connection
await client.connect("ws://server:8765")
await client.disconnect()

# Session Management
await client.create_session("Session Name", password="1234", max_users=8)
await client.join_session(session_id, password="1234")
await client.leave_session()
await client.list_sessions()

# Actions
await client.send_midi_note(60, 100, 0.5)
await client.send_tempo_change(120.0)
await client.send_mode_change("jam")
await client.send_chat_message("Hello!")

# Callbacks
client.add_action_callback(on_action)
client.add_user_join_callback(on_user_join)
client.add_user_leave_callback(on_user_leave)

# Getters
client.get_current_session()  # (session_id, session_name)
client.get_remote_users()     # List[RemoteUser]
client.get_user_id()          # str
```

### NeuralinkServer

```python
server = NeuralinkServer(host="0.0.0.0", port=8765)

# Start/Stop
await server.start()
await server.stop()

# Standalone
python daiw/network/neuralink_server.py
```

## 🤝 Contributing

Neuralink Mode ist ein komplexes Feature mit vielen Verbesserungsmöglichkeiten!

**Wanted Features:**
- WebRTC Integration
- Better Conflict Resolution
- Voice/Video Chat
- Mobile Client (iOS/Android)

## 📄 License

MIT License - Teil des DAIW (Digital AI Workspace) Projekts

---

**Join the revolution of collaborative music production!** 🧠🎵

Bei Fragen oder Issues: GitHub Repository Issues
