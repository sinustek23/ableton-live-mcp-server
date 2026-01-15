"""
YouTube Handler - Download and analyze YouTube songs

Ermöglicht das Herunterladen von YouTube-Songs, Extrahieren von Audio
und Analyse des musikalischen Stils.
"""

import asyncio
from typing import Optional, Dict, Any, Callable
from pathlib import Path
from dataclasses import dataclass
import json
import tempfile

try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False
    print("[YouTubeHandler] Warning: yt-dlp not available")

try:
    import librosa
    import numpy as np
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    print("[YouTubeHandler] Warning: librosa not available")


@dataclass
class YouTubeTrackInfo:
    """Information about a YouTube track"""
    video_id: str
    title: str
    artist: Optional[str] = None
    duration: float = 0.0
    url: str = ""
    audio_path: Optional[Path] = None

    # Musical analysis
    tempo: Optional[float] = None
    key: Optional[str] = None
    energy: Optional[float] = None
    style: Optional[str] = None


class YouTubeHandler:
    """
    Handler for downloading and analyzing YouTube content
    """

    def __init__(self, download_dir: Optional[Path] = None):
        self.download_dir = download_dir or Path(tempfile.gettempdir()) / "music_copilot_youtube"
        self.download_dir.mkdir(parents=True, exist_ok=True)

        # Progress callbacks
        self._progress_callbacks: list[Callable] = []

        # Cache
        self._analyzed_tracks: Dict[str, YouTubeTrackInfo] = {}

    async def download_audio(self, url: str, progress_callback: Optional[Callable] = None) -> Optional[YouTubeTrackInfo]:
        """
        Download audio from YouTube URL

        Args:
            url: YouTube URL
            progress_callback: Optional callback for download progress

        Returns:
            YouTubeTrackInfo if successful, None otherwise
        """
        if not YT_DLP_AVAILABLE:
            print("[YouTubeHandler] yt-dlp not available")
            return None

        try:
            # yt-dlp options
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': str(self.download_dir / '%(id)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'progress_hooks': [self._progress_hook] if progress_callback else [],
            }

            # Download in executor (blocking operation)
            info = await asyncio.get_event_loop().run_in_executor(
                None,
                self._download_sync,
                url,
                ydl_opts
            )

            if not info:
                return None

            # Create track info
            track = YouTubeTrackInfo(
                video_id=info['id'],
                title=info.get('title', 'Unknown'),
                artist=info.get('artist') or info.get('uploader'),
                duration=info.get('duration', 0.0),
                url=url,
                audio_path=self.download_dir / f"{info['id']}.mp3"
            )

            # Cache
            self._analyzed_tracks[track.video_id] = track

            print(f"[YouTubeHandler] Downloaded: {track.title}")
            return track

        except Exception as e:
            print(f"[YouTubeHandler] Error downloading from {url}: {e}")
            return None

    def _download_sync(self, url: str, ydl_opts: dict) -> Optional[dict]:
        """Synchronous download helper"""
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                return info
        except Exception as e:
            print(f"[YouTubeHandler] Download error: {e}")
            return None

    def _progress_hook(self, d: dict) -> None:
        """Progress hook for yt-dlp"""
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%')
            print(f"[YouTubeHandler] Downloading: {percent}", end='\r')
        elif d['status'] == 'finished':
            print("[YouTubeHandler] Download finished, converting...")

    async def analyze_track(self, track: YouTubeTrackInfo) -> YouTubeTrackInfo:
        """
        Analyze musical characteristics of a track

        Args:
            track: YouTubeTrackInfo with audio_path

        Returns:
            Updated track with analysis
        """
        if not LIBROSA_AVAILABLE or not track.audio_path or not track.audio_path.exists():
            print("[YouTubeHandler] Cannot analyze track")
            return track

        try:
            print(f"[YouTubeHandler] Analyzing: {track.title}")

            # Load audio (in executor - blocking)
            y, sr = await asyncio.get_event_loop().run_in_executor(
                None,
                librosa.load,
                str(track.audio_path),
                None,  # sr=None (native)
                False,  # mono=False
                0.0,    # offset
                60.0    # duration (analyze first 60 seconds)
            )

            # Tempo detection
            tempo, _ = await asyncio.get_event_loop().run_in_executor(
                None,
                librosa.beat.beat_track,
                y,
                sr
            )
            track.tempo = float(tempo)

            # Key detection (simple approach using chroma)
            chroma = await asyncio.get_event_loop().run_in_executor(
                None,
                librosa.feature.chroma_cqt,
                y,
                sr
            )

            # Find dominant pitch class
            chroma_mean = np.mean(chroma, axis=1)
            key_idx = np.argmax(chroma_mean)
            key_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            track.key = key_names[key_idx]

            # Energy (RMS)
            rms = await asyncio.get_event_loop().run_in_executor(
                None,
                librosa.feature.rms,
                y=y
            )
            track.energy = float(np.mean(rms))

            # Style classification (simple heuristic)
            if track.tempo and track.tempo > 140:
                track.style = "fast/energetic"
            elif track.tempo and track.tempo < 90:
                track.style = "slow/ballad"
            else:
                track.style = "medium tempo"

            print(f"[YouTubeHandler] Analysis complete:")
            print(f"  Tempo: {track.tempo:.1f} BPM")
            print(f"  Key: {track.key}")
            print(f"  Energy: {track.energy:.3f}")
            print(f"  Style: {track.style}")

            # Update cache
            self._analyzed_tracks[track.video_id] = track

            return track

        except Exception as e:
            print(f"[YouTubeHandler] Error analyzing track: {e}")
            return track

    async def extract_style_prompt(self, track: YouTubeTrackInfo) -> str:
        """
        Create a prompt for AI to replicate the style

        Args:
            track: Analyzed track

        Returns:
            Prompt string
        """
        prompt = f"""Analyze and replicate the musical style of: "{track.title}"

Musical characteristics:
- Tempo: {track.tempo:.1f} BPM
- Key: {track.key}
- Energy level: {track.energy:.3f}
- Style: {track.style}

Create a musical idea that captures this style. Focus on:
1. Matching the tempo and feel
2. Using the detected key
3. Capturing the energy and mood
4. Generating appropriate chord progressions and melodies
"""
        return prompt

    async def download_and_analyze(self, url: str) -> Optional[YouTubeTrackInfo]:
        """
        Download and analyze a YouTube track (convenience method)

        Args:
            url: YouTube URL

        Returns:
            Analyzed track info
        """
        # Download
        track = await self.download_audio(url)
        if not track:
            return None

        # Analyze
        track = await self.analyze_track(track)

        return track

    def get_cached_track(self, video_id: str) -> Optional[YouTubeTrackInfo]:
        """Get a previously analyzed track from cache"""
        return self._analyzed_tracks.get(video_id)

    def list_downloaded_tracks(self) -> list[YouTubeTrackInfo]:
        """List all downloaded and analyzed tracks"""
        return list(self._analyzed_tracks.values())

    def cleanup_downloads(self, keep_recent: int = 5) -> None:
        """
        Clean up old downloads, keeping only recent ones

        Args:
            keep_recent: Number of recent downloads to keep
        """
        try:
            # Get all mp3 files
            files = sorted(
                self.download_dir.glob("*.mp3"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )

            # Remove old files
            for file in files[keep_recent:]:
                file.unlink()
                print(f"[YouTubeHandler] Removed old download: {file.name}")

        except Exception as e:
            print(f"[YouTubeHandler] Error cleaning up: {e}")

    async def search_and_download(self, query: str, max_results: int = 1) -> Optional[YouTubeTrackInfo]:
        """
        Search YouTube and download first result

        Args:
            query: Search query
            max_results: Maximum number of results to consider

        Returns:
            First downloaded track
        """
        if not YT_DLP_AVAILABLE:
            return None

        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
            }

            # Search
            search_url = f"ytsearch{max_results}:{query}"
            info = await asyncio.get_event_loop().run_in_executor(
                None,
                self._extract_info_sync,
                search_url,
                ydl_opts
            )

            if not info or 'entries' not in info or not info['entries']:
                print(f"[YouTubeHandler] No results for: {query}")
                return None

            # Get first result
            first_result = info['entries'][0]
            video_url = f"https://www.youtube.com/watch?v={first_result['id']}"

            print(f"[YouTubeHandler] Found: {first_result.get('title', 'Unknown')}")

            # Download and analyze
            return await self.download_and_analyze(video_url)

        except Exception as e:
            print(f"[YouTubeHandler] Error searching: {e}")
            return None

    def _extract_info_sync(self, url: str, ydl_opts: dict) -> Optional[dict]:
        """Synchronous info extraction helper"""
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(url, download=False)
        except Exception as e:
            print(f"[YouTubeHandler] Extract info error: {e}")
            return None


# Example usage
async def _example_usage():
    """Example usage of YouTubeHandler"""
    handler = YouTubeHandler()

    # Download and analyze
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Example
    track = await handler.download_and_analyze(url)

    if track:
        print(f"Track: {track.title}")
        print(f"Tempo: {track.tempo} BPM")
        print(f"Key: {track.key}")

        # Get style prompt
        prompt = await handler.extract_style_prompt(track)
        print(f"\nStyle prompt:\n{prompt}")


if __name__ == "__main__":
    asyncio.run(_example_usage())
