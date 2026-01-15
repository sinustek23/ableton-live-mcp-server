"""
Feature Dialogs - Interactive dialogs for Avatar features

Dialogs für YouTube-Analyse, STEM-Separation, Humming-Recording, etc.
"""

from typing import Optional, Callable
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QProgressBar,
    QComboBox,
    QTextEdit,
    QCheckBox,
    QGroupBox,
    QSpinBox,
    QDoubleSpinBox,
    QFileDialog,
    QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont
from pathlib import Path


class YouTubeAnalyzerDialog(QDialog):
    """Dialog for YouTube song analysis"""

    analyze_requested = pyqtSignal(str)  # URL

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("🎵 YouTube Reference Analyzer")
        self.setMinimumWidth(500)

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()

        # Title
        title = QLabel("Analyze YouTube Songs")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Description
        desc = QLabel("Enter a YouTube URL or search query to analyze the musical style:")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # URL/Search input
        input_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("YouTube URL or search query (e.g., 'Daft Punk Get Lucky')")
        input_layout.addWidget(self.url_input)

        self.analyze_button = QPushButton("🔍 Analyze")
        self.analyze_button.clicked.connect(self._on_analyze)
        input_layout.addWidget(self.analyze_button)

        layout.addLayout(input_layout)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        # Status label
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        # Results group
        results_group = QGroupBox("Analysis Results")
        results_layout = QVBoxLayout()

        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMaximumHeight(200)
        results_layout.addWidget(self.results_text)

        results_group.setLayout(results_layout)
        layout.addWidget(results_group)

        # Actions
        actions_layout = QHBoxLayout()

        self.copy_style_button = QPushButton("📋 Copy Style to Jam Mode")
        self.copy_style_button.setEnabled(False)
        self.copy_style_button.clicked.connect(self._on_copy_style)
        actions_layout.addWidget(self.copy_style_button)

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        actions_layout.addWidget(self.close_button)

        layout.addLayout(actions_layout)

        self.setLayout(layout)

    def _on_analyze(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Input Required", "Please enter a YouTube URL or search query")
            return

        self.analyze_requested.emit(url)

    def _on_copy_style(self):
        # TODO: Implement copying style to jam mode
        QMessageBox.information(self, "Style Copied", "Style parameters copied to Jam Mode!")

    def set_progress(self, value: int, status: str = ""):
        self.progress.setVisible(value < 100)
        self.progress.setValue(value)
        if status:
            self.status_label.setText(status)

    def set_results(self, results: str):
        self.results_text.setPlainText(results)
        self.copy_style_button.setEnabled(True)


class STEMSeparatorDialog(QDialog):
    """Dialog for STEM separation"""

    separate_requested = pyqtSignal(str, list)  # file_path, stem_types

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("🎼 STEM Separator")
        self.setMinimumWidth(500)

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()

        # Title
        title = QLabel("Separate Audio into Stems")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Description
        desc = QLabel("Separate audio into vocals, drums, bass, and other instruments:")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # File selection
        file_layout = QHBoxLayout()
        file_label = QLabel("Audio File:")
        file_layout.addWidget(file_label)

        self.file_input = QLineEdit()
        self.file_input.setReadOnly(True)
        file_layout.addWidget(self.file_input)

        self.browse_button = QPushButton("📁 Browse")
        self.browse_button.clicked.connect(self._on_browse)
        file_layout.addWidget(self.browse_button)

        layout.addLayout(file_layout)

        # Stem selection
        stems_group = QGroupBox("Stems to Extract")
        stems_layout = QVBoxLayout()

        self.vocals_check = QCheckBox("🎤 Vocals")
        self.vocals_check.setChecked(True)
        stems_layout.addWidget(self.vocals_check)

        self.drums_check = QCheckBox("🥁 Drums")
        self.drums_check.setChecked(True)
        stems_layout.addWidget(self.drums_check)

        self.bass_check = QCheckBox("🎸 Bass")
        self.bass_check.setChecked(True)
        stems_layout.addWidget(self.bass_check)

        self.other_check = QCheckBox("🎹 Other")
        self.other_check.setChecked(True)
        stems_layout.addWidget(self.other_check)

        stems_group.setLayout(stems_layout)
        layout.addWidget(stems_group)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        # Status label
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        # Actions
        actions_layout = QHBoxLayout()

        self.separate_button = QPushButton("✂️ Separate")
        self.separate_button.clicked.connect(self._on_separate)
        actions_layout.addWidget(self.separate_button)

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        actions_layout.addWidget(self.close_button)

        layout.addLayout(actions_layout)

        self.setLayout(layout)

    def _on_browse(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Audio File",
            "",
            "Audio Files (*.mp3 *.wav *.flac *.m4a *.ogg);;All Files (*)"
        )

        if file_path:
            self.file_input.setText(file_path)

    def _on_separate(self):
        file_path = self.file_input.text().strip()
        if not file_path:
            QMessageBox.warning(self, "File Required", "Please select an audio file")
            return

        # Get selected stems
        stems = []
        if self.vocals_check.isChecked():
            stems.append("vocals")
        if self.drums_check.isChecked():
            stems.append("drums")
        if self.bass_check.isChecked():
            stems.append("bass")
        if self.other_check.isChecked():
            stems.append("other")

        if not stems:
            QMessageBox.warning(self, "Selection Required", "Please select at least one stem to extract")
            return

        self.separate_requested.emit(file_path, stems)

    def set_progress(self, value: float, status: str = ""):
        self.progress.setVisible(value < 1.0)
        self.progress.setValue(int(value * 100))
        if status:
            self.status_label.setText(status)


class HummingRecorderDialog(QDialog):
    """Dialog for humming/singing recording"""

    record_requested = pyqtSignal()
    stop_requested = pyqtSignal()
    playback_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("🎤 Humming Recorder")
        self.setMinimumWidth(500)

        self._recording = False
        self._recorded_phrase = None

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()

        # Title
        title = QLabel("Record Humming → MIDI")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Description
        desc = QLabel("Hum or sing a melody, and the avatar will convert it to MIDI notes:")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Recording controls
        controls_group = QGroupBox("Recording Controls")
        controls_layout = QVBoxLayout()

        # Input device selection
        device_layout = QHBoxLayout()
        device_label = QLabel("Input Device:")
        device_layout.addWidget(device_label)

        self.device_combo = QComboBox()
        device_layout.addWidget(self.device_combo)

        controls_layout.addLayout(device_layout)

        # Settings
        settings_layout = QHBoxLayout()

        sensitivity_label = QLabel("Sensitivity:")
        settings_layout.addWidget(sensitivity_label)

        self.sensitivity_spin = QDoubleSpinBox()
        self.sensitivity_spin.setRange(0.1, 1.0)
        self.sensitivity_spin.setValue(0.5)
        self.sensitivity_spin.setSingleStep(0.1)
        settings_layout.addWidget(self.sensitivity_spin)

        settings_layout.addStretch()
        controls_layout.addLayout(settings_layout)

        controls_group.setLayout(controls_layout)
        layout.addWidget(controls_group)

        # Recording button
        self.record_button = QPushButton("⏺️  Start Recording")
        self.record_button.setMinimumHeight(50)
        self.record_button.clicked.connect(self._on_record_toggle)
        layout.addWidget(self.record_button)

        # Real-time pitch display
        pitch_group = QGroupBox("Real-time Pitch")
        pitch_layout = QVBoxLayout()

        self.pitch_label = QLabel("Waiting...")
        self.pitch_label.setFont(QFont("Courier", 14))
        self.pitch_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pitch_layout.addWidget(self.pitch_label)

        pitch_group.setLayout(pitch_layout)
        layout.addWidget(pitch_group)

        # Results
        results_group = QGroupBox("Detected Melody")
        results_layout = QVBoxLayout()

        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMaximumHeight(150)
        results_layout.addWidget(self.results_text)

        results_group.setLayout(results_layout)
        layout.addWidget(results_group)

        # Playback controls
        playback_layout = QHBoxLayout()

        self.playback_button = QPushButton("▶️ Play Back as MIDI")
        self.playback_button.setEnabled(False)
        self.playback_button.clicked.connect(self._on_playback)
        playback_layout.addWidget(self.playback_button)

        self.learn_button = QPushButton("💡 Learn This Melody")
        self.learn_button.setEnabled(False)
        playback_layout.addWidget(self.learn_button)

        layout.addLayout(playback_layout)

        # Close button
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        layout.addWidget(self.close_button)

        self.setLayout(layout)

    def set_devices(self, devices: list):
        """Set available input devices"""
        self.device_combo.clear()
        for idx, name in devices:
            self.device_combo.addItem(f"{idx}: {name}", idx)

    def _on_record_toggle(self):
        if not self._recording:
            # Start recording
            self._recording = True
            self.record_button.setText("⏹️  Stop Recording")
            self.record_button.setStyleSheet("background-color: #ff4444;")
            self.pitch_label.setText("🎤 Listening...")
            self.record_requested.emit()
        else:
            # Stop recording
            self._recording = False
            self.record_button.setText("⏺️  Start Recording")
            self.record_button.setStyleSheet("")
            self.pitch_label.setText("Processing...")
            self.stop_requested.emit()

    def _on_playback(self):
        self.playback_requested.emit()

    def update_pitch(self, pitch_hz: float, note_name: str):
        """Update real-time pitch display"""
        self.pitch_label.setText(f"🎵 {note_name} ({pitch_hz:.1f} Hz)")

    def set_results(self, results: str):
        """Set detected melody results"""
        self.results_text.setPlainText(results)
        self.playback_button.setEnabled(True)
        self.learn_button.setEnabled(True)
        self.pitch_label.setText("Complete!")


class FeatureMenuDialog(QDialog):
    """Main feature selection dialog"""

    youtube_requested = pyqtSignal()
    stem_requested = pyqtSignal()
    humming_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("🎵 Interactive Features")
        self.setMinimumWidth(400)

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()

        # Title
        title = QLabel("Choose a Feature")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Feature buttons
        youtube_btn = QPushButton("🎥 Analyze YouTube Song\n(Copy style & feel)")
        youtube_btn.setMinimumHeight(70)
        youtube_btn.clicked.connect(lambda: (self.youtube_requested.emit(), self.close()))
        layout.addWidget(youtube_btn)

        stem_btn = QPushButton("✂️ Separate STEM\n(Extract vocals, drums, bass, etc.)")
        stem_btn.setMinimumHeight(70)
        stem_btn.clicked.connect(lambda: (self.stem_requested.emit(), self.close()))
        layout.addWidget(stem_btn)

        humming_btn = QPushButton("🎤 Hum → MIDI\n(Record melody and convert)")
        humming_btn.setMinimumHeight(70)
        humming_btn.clicked.connect(lambda: (self.humming_requested.emit(), self.close()))
        layout.addWidget(humming_btn)

        # Close button
        close_btn = QPushButton("Cancel")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

        self.setLayout(layout)
