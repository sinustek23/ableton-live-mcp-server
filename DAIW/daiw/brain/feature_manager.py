"""
Interactive Feature Manager - Manages YouTube, STEM, Humming features

Koordiniert die neuen interaktiven Features des Avatars
"""

from typing import Optional, Dict, Any
import asyncio
from pathlib import Path

from daiw.audio.youtube_handler import YouTubeHandler, YouTubeTrackInfo
from daiw.audio.stem_separator import STEMSeparator, SeparatedStems, StemType
from daiw.audio.humming_detector import HummingDetector, HummingPhrase
from daiw.audio.midi_handler import MIDIHandler
from daiw.brain.ai_controller import AIController


class InteractiveFeatureManager:
    """
    Manages all interactive features (YouTube, STEM, Humming)
    """

    def __init__(
        self,
        ai_controller: AIController,
        midi_handler: MIDIHandler
    ):
        self.ai = ai_controller
        self.midi = midi_handler

        # Feature handlers
        self.youtube_handler: Optional[YouTubeHandler] = None
        self.stem_separator: Optional[STEMSeparator] = None
        self.humming_detector: Optional[HummingDetector] = None

        # Current context
        self._current_youtube_track: Optional[YouTubeTrackInfo] = None
        self._current_stems: Optional[SeparatedStems] = None
        self._current_humming: Optional[HummingPhrase] = None

        # Initialize handlers
        self._initialize_handlers()

    def _initialize_handlers(self) -> None:
        """Initialize feature handlers"""
        try:
            self.youtube_handler = YouTubeHandler()
            print("[FeatureManager] YouTube handler initialized")
        except Exception as e:
            print(f"[FeatureManager] YouTube handler failed: {e}")

        try:
            self.stem_separator = STEMSeparator()
            print("[FeatureManager] STEM separator initialized")
        except Exception as e:
            print(f"[FeatureManager] STEM separator failed: {e}")

        try:
            self.humming_detector = HummingDetector()
            print("[FeatureManager] Humming detector initialized")
        except Exception as e:
            print(f"[FeatureManager] Humming detector failed: {e}")

    # ========== YouTube Features ==========

    async def analyze_youtube_song(
        self,
        url_or_query: str,
        progress_callback: Optional[callable] = None
    ) -> Optional[YouTubeTrackInfo]:
        """
        Analyze a YouTube song

        Args:
            url_or_query: YouTube URL or search query
            progress_callback: Optional progress callback

        Returns:
            Analyzed track info
        """
        if not self.youtube_handler:
            print("[FeatureManager] YouTube handler not available")
            return None

        try:
            # Check if it's a URL or search query
            if "youtube.com" in url_or_query or "youtu.be" in url_or_query:
                # Direct URL
                if progress_callback:
                    await progress_callback(10, "Downloading...")

                track = await self.youtube_handler.download_and_analyze(url_or_query)
            else:
                # Search query
                if progress_callback:
                    await progress_callback(10, "Searching...")

                track = await self.youtube_handler.search_and_download(url_or_query)

            if track:
                self._current_youtube_track = track

                if progress_callback:
                    await progress_callback(100, "Complete!")

                return track

            return None

        except Exception as e:
            print(f"[FeatureManager] Error analyzing YouTube song: {e}")
            return None

    async def get_youtube_style_prompt(self) -> Optional[str]:
        """Get AI prompt for current YouTube track style"""
        if not self._current_youtube_track:
            return None

        return await self.youtube_handler.extract_style_prompt(self._current_youtube_track)

    async def generate_from_youtube_style(self) -> Optional[Dict[str, Any]]:
        """
        Generate musical idea based on current YouTube track style

        Returns:
            Musical idea dictionary
        """
        if not self._current_youtube_track or not self.ai:
            return None

        # Get style prompt
        prompt = await self.get_youtube_style_prompt()

        if not prompt:
            return None

        # Generate idea
        idea = await self.ai.generate_musical_idea(
            prompt,
            constraints={
                "tempo": self._current_youtube_track.tempo,
                "key": self._current_youtube_track.key
            }
        )

        return idea

    # ========== STEM Separation Features ==========

    async def separate_stems(
        self,
        audio_file: Path,
        stems_to_extract: Optional[list] = None,
        progress_callback: Optional[callable] = None
    ) -> Optional[SeparatedStems]:
        """
        Separate audio into stems

        Args:
            audio_file: Path to audio file
            stems_to_extract: List of stem types to extract
            progress_callback: Optional progress callback

        Returns:
            Separated stems
        """
        if not self.stem_separator:
            print("[FeatureManager] STEM separator not available")
            return None

        try:
            # Convert stem names to StemType if needed
            stem_types = None
            if stems_to_extract:
                stem_types = [StemType(name) for name in stems_to_extract]

            # Separate
            stems = await self.stem_separator.separate(
                audio_file,
                stems_to_extract=stem_types,
                progress_callback=progress_callback
            )

            if stems:
                self._current_stems = stems
                return stems

            return None

        except Exception as e:
            print(f"[FeatureManager] Error separating stems: {e}")
            return None

    async def play_stem_as_reference(self, stem_type: StemType) -> bool:
        """
        Play a separated stem as reference

        Args:
            stem_type: Type of stem to play

        Returns:
            True if successful
        """
        if not self._current_stems:
            print("[FeatureManager] No stems available")
            return False

        stem_path = self._current_stems.get_stem(stem_type)
        if not stem_path or not stem_path.exists():
            print(f"[FeatureManager] Stem not found: {stem_type}")
            return False

        # TODO: Implement audio playback
        print(f"[FeatureManager] Would play: {stem_path}")
        return True

    async def analyze_stem_pattern(self, stem_type: StemType) -> Optional[Dict]:
        """
        Analyze musical pattern in a stem using AI

        Args:
            stem_type: Stem to analyze

        Returns:
            Analysis results
        """
        if not self._current_stems or not self.ai:
            return None

        stem_path = self._current_stems.get_stem(stem_type)
        if not stem_path:
            return None

        # TODO: Implement librosa analysis → MIDI extraction → AI analysis
        print(f"[FeatureManager] Analyzing stem: {stem_type}")
        return None

    # ========== Humming Features ==========

    async def start_humming_recording(self, device_id: Optional[int] = None) -> bool:
        """
        Start recording humming

        Args:
            device_id: Optional audio input device ID

        Returns:
            True if started
        """
        if not self.humming_detector:
            print("[FeatureManager] Humming detector not available")
            return False

        return await self.humming_detector.start_recording(device_id)

    async def stop_humming_recording(self) -> Optional[HummingPhrase]:
        """
        Stop recording and process humming

        Returns:
            Processed humming phrase
        """
        if not self.humming_detector:
            return None

        phrase = await self.humming_detector.stop_recording()

        if phrase:
            self._current_humming = phrase

        return phrase

    async def playback_humming_as_midi(self) -> bool:
        """
        Play back current humming phrase as MIDI

        Returns:
            True if successful
        """
        if not self._current_humming or not self.humming_detector or not self.midi:
            return False

        try:
            await self.humming_detector.play_back_as_midi(self._current_humming, self.midi)
            return True
        except Exception as e:
            print(f"[FeatureManager] Error playing back humming: {e}")
            return False

    async def harmonize_humming(self) -> Optional[Dict]:
        """
        Create harmonies for the hummed melody using AI

        Returns:
            Harmonized musical idea
        """
        if not self._current_humming or not self.ai:
            return None

        # Extract melody notes
        melody_notes = [note.note for note in self._current_humming.midi_notes]

        # Ask AI to harmonize
        prompt = f"""Harmonize this melody: {melody_notes}

Create chord accompaniment that fits the melody.
Return as JSON with:
- chords: List of chord progressions
- bass_line: Complementary bass notes
"""

        response = await self.ai.chat(prompt)

        # TODO: Parse response and return harmonization
        print(f"[FeatureManager] Harmonization: {response}")
        return None

    def list_audio_input_devices(self) -> list:
        """List available audio input devices"""
        if not self.humming_detector:
            return []

        return self.humming_detector.list_input_devices()

    def add_humming_pitch_callback(self, callback: callable) -> None:
        """Add callback for real-time pitch detection"""
        if self.humming_detector:
            self.humming_detector.add_pitch_callback(callback)

    def remove_humming_pitch_callback(self, callback: callable) -> None:
        """Remove pitch callback"""
        if self.humming_detector:
            self.humming_detector.remove_pitch_callback(callback)

    # ========== Utility Methods ==========

    def get_current_youtube_track(self) -> Optional[YouTubeTrackInfo]:
        """Get current analyzed YouTube track"""
        return self._current_youtube_track

    def get_current_stems(self) -> Optional[SeparatedStems]:
        """Get current separated stems"""
        return self._current_stems

    def get_current_humming(self) -> Optional[HummingPhrase]:
        """Get current humming phrase"""
        return self._current_humming

    async def cleanup_all(self) -> None:
        """Clean up old files from all features"""
        if self.youtube_handler:
            self.youtube_handler.cleanup_downloads(keep_recent=3)

        if self.stem_separator:
            self.stem_separator.cleanup_old_stems(keep_recent=2)

        if self.humming_detector:
            self.humming_detector.cleanup_old_recordings(keep_recent=5)

        print("[FeatureManager] Cleanup complete")
