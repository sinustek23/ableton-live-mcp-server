"""
STEM Separator - Separate audio into vocals, drums, bass, other

Nutzt Demucs für hochqualitative Source Separation
"""

import asyncio
from typing import Optional, Dict, List, Callable
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import tempfile

try:
    import torch
    from demucs.pretrained import get_model
    from demucs.apply import apply_model
    from demucs.audio import AudioFile, save_audio
    DEMUCS_AVAILABLE = True
except ImportError:
    DEMUCS_AVAILABLE = False
    print("[STEMSeparator] Warning: demucs not available")


class StemType(Enum):
    """Available stem types"""
    VOCALS = "vocals"
    DRUMS = "drums"
    BASS = "bass"
    OTHER = "other"


@dataclass
class SeparatedStems:
    """Container for separated audio stems"""
    source_file: Path
    output_dir: Path

    vocals: Optional[Path] = None
    drums: Optional[Path] = None
    bass: Optional[Path] = None
    other: Optional[Path] = None

    def get_stem(self, stem_type: StemType) -> Optional[Path]:
        """Get path to a specific stem"""
        return getattr(self, stem_type.value, None)

    def get_all_stems(self) -> Dict[StemType, Path]:
        """Get all available stems"""
        stems = {}
        for stem_type in StemType:
            path = self.get_stem(stem_type)
            if path and path.exists():
                stems[stem_type] = path
        return stems


class STEMSeparator:
    """
    Audio source separation using Demucs
    """

    def __init__(self, output_dir: Optional[Path] = None, model_name: str = "htdemucs"):
        """
        Initialize STEM separator

        Args:
            output_dir: Directory for separated stems
            model_name: Demucs model to use (htdemucs, htdemucs_ft, htdemucs_6s)
        """
        self.output_dir = output_dir or Path(tempfile.gettempdir()) / "music_copilot_stems"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.model_name = model_name
        self._model = None
        self._device = "cuda" if torch.cuda.is_available() else "cpu"

        # Progress callbacks
        self._progress_callbacks: List[Callable] = []

        print(f"[STEMSeparator] Using device: {self._device}")

    async def load_model(self) -> bool:
        """
        Load Demucs model

        Returns:
            True if loaded successfully
        """
        if not DEMUCS_AVAILABLE:
            print("[STEMSeparator] Demucs not available")
            return False

        try:
            print(f"[STEMSeparator] Loading model: {self.model_name}")

            # Load model in executor (can be slow)
            self._model = await asyncio.get_event_loop().run_in_executor(
                None,
                get_model,
                self.model_name
            )

            self._model.to(self._device)
            self._model.eval()

            print("[STEMSeparator] Model loaded successfully")
            return True

        except Exception as e:
            print(f"[STEMSeparator] Error loading model: {e}")
            return False

    async def separate(
        self,
        audio_file: Path,
        stems_to_extract: Optional[List[StemType]] = None,
        progress_callback: Optional[Callable] = None
    ) -> Optional[SeparatedStems]:
        """
        Separate audio into stems

        Args:
            audio_file: Path to audio file
            stems_to_extract: List of stems to extract (None = all)
            progress_callback: Optional progress callback

        Returns:
            SeparatedStems if successful
        """
        if not DEMUCS_AVAILABLE or not self._model:
            print("[STEMSeparator] Model not loaded")
            if not await self.load_model():
                return None

        if not audio_file.exists():
            print(f"[STEMSeparator] File not found: {audio_file}")
            return None

        try:
            print(f"[STEMSeparator] Separating: {audio_file.name}")

            if progress_callback:
                await progress_callback(0.1, "Loading audio...")

            # Load audio
            wav = await asyncio.get_event_loop().run_in_executor(
                None,
                AudioFile(str(audio_file)).read,
                None,  # streams
                self._model.samplerate,
                self._model.audio_channels
            )

            # Prepare batch
            ref = wav.mean(0)
            wav = (wav - ref.mean()) / ref.std()
            wav = wav.unsqueeze(0)  # Add batch dimension

            if progress_callback:
                await progress_callback(0.3, "Separating sources...")

            # Apply model (in executor - GPU intensive)
            with torch.no_grad():
                sources = await asyncio.get_event_loop().run_in_executor(
                    None,
                    self._apply_model_sync,
                    wav
                )

            # Denormalize
            sources = sources * ref.std() + ref.mean()

            if progress_callback:
                await progress_callback(0.7, "Saving stems...")

            # Save stems
            output_subdir = self.output_dir / audio_file.stem
            output_subdir.mkdir(parents=True, exist_ok=True)

            separated = SeparatedStems(
                source_file=audio_file,
                output_dir=output_subdir
            )

            # Demucs outputs: drums, bass, other, vocals
            stem_names = self._model.sources
            extract_all = stems_to_extract is None

            for i, stem_name in enumerate(stem_names):
                # Map demucs names to our StemType
                try:
                    stem_type = StemType(stem_name)
                except ValueError:
                    continue

                # Check if we should extract this stem
                if not extract_all and stem_type not in stems_to_extract:
                    continue

                # Save stem
                stem_path = output_subdir / f"{stem_name}.wav"

                await asyncio.get_event_loop().run_in_executor(
                    None,
                    save_audio,
                    sources[0, i],
                    str(stem_path),
                    self._model.samplerate
                )

                # Update result
                setattr(separated, stem_name, stem_path)

                print(f"[STEMSeparator] Saved: {stem_name}.wav")

            if progress_callback:
                await progress_callback(1.0, "Complete!")

            print(f"[STEMSeparator] Separation complete: {output_subdir}")
            return separated

        except Exception as e:
            print(f"[STEMSeparator] Error separating: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _apply_model_sync(self, wav: torch.Tensor) -> torch.Tensor:
        """Synchronous model application"""
        return apply_model(
            self._model,
            wav.to(self._device),
            device=self._device,
            shifts=1,
            split=True,
            overlap=0.25,
            progress=True
        )[0].cpu()

    async def extract_single_stem(
        self,
        audio_file: Path,
        stem_type: StemType,
        progress_callback: Optional[Callable] = None
    ) -> Optional[Path]:
        """
        Extract a single stem from audio

        Args:
            audio_file: Path to audio file
            stem_type: Type of stem to extract
            progress_callback: Optional progress callback

        Returns:
            Path to extracted stem
        """
        result = await self.separate(
            audio_file,
            stems_to_extract=[stem_type],
            progress_callback=progress_callback
        )

        if result:
            return result.get_stem(stem_type)

        return None

    async def get_vocals(self, audio_file: Path) -> Optional[Path]:
        """Convenience method to extract vocals only"""
        return await self.extract_single_stem(audio_file, StemType.VOCALS)

    async def get_instrumental(self, audio_file: Path, output_path: Optional[Path] = None) -> Optional[Path]:
        """
        Get instrumental (all except vocals)

        Args:
            audio_file: Path to audio file
            output_path: Optional output path

        Returns:
            Path to instrumental mix
        """
        result = await self.separate(audio_file)
        if not result:
            return None

        # Mix drums, bass, other
        try:
            import soundfile as sf
            import numpy as np

            stems_to_mix = [StemType.DRUMS, StemType.BASS, StemType.OTHER]
            mixed = None
            sr = None

            for stem_type in stems_to_mix:
                stem_path = result.get_stem(stem_type)
                if stem_path and stem_path.exists():
                    data, sr = sf.read(str(stem_path))
                    if mixed is None:
                        mixed = data
                    else:
                        mixed += data

            if mixed is not None:
                # Save mixed instrumental
                output = output_path or result.output_dir / "instrumental.wav"
                sf.write(str(output), mixed, sr)
                print(f"[STEMSeparator] Saved instrumental: {output}")
                return output

        except Exception as e:
            print(f"[STEMSeparator] Error creating instrumental: {e}")

        return None

    def cleanup_old_stems(self, keep_recent: int = 3) -> None:
        """
        Clean up old stem folders

        Args:
            keep_recent: Number of recent separations to keep
        """
        try:
            # Get all stem directories
            stem_dirs = sorted(
                [d for d in self.output_dir.iterdir() if d.is_dir()],
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )

            # Remove old directories
            for stem_dir in stem_dirs[keep_recent:]:
                import shutil
                shutil.rmtree(stem_dir)
                print(f"[STEMSeparator] Removed old stems: {stem_dir.name}")

        except Exception as e:
            print(f"[STEMSeparator] Error cleaning up: {e}")

    def add_progress_callback(self, callback: Callable) -> None:
        """Add a progress callback"""
        self._progress_callbacks.append(callback)

    def remove_progress_callback(self, callback: Callable) -> None:
        """Remove a progress callback"""
        if callback in self._progress_callbacks:
            self._progress_callbacks.remove(callback)


# Example usage
async def _example_usage():
    """Example usage of STEMSeparator"""
    separator = STEMSeparator()

    # Example audio file
    audio_file = Path("example.mp3")

    if audio_file.exists():
        # Separate all stems
        result = await separator.separate(audio_file)

        if result:
            print(f"Stems saved to: {result.output_dir}")

            # Get specific stem
            vocals = result.get_stem(StemType.VOCALS)
            if vocals:
                print(f"Vocals: {vocals}")

        # Extract vocals only
        vocals_path = await separator.get_vocals(audio_file)
        if vocals_path:
            print(f"Vocals extracted: {vocals_path}")

        # Get instrumental
        instrumental = await separator.get_instrumental(audio_file)
        if instrumental:
            print(f"Instrumental: {instrumental}")


if __name__ == "__main__":
    asyncio.run(_example_usage())
