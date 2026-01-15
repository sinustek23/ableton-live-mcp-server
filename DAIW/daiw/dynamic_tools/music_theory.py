"""
Music Theory Library - Grundbausteine für dynamische Skripte

Diese Library bietet die Basis-Funktionen für Harmonie, Rhythmus und MIDI-Manipulation,
auf die sich die selbstgeschriebenen Skripte im Lock Mode beziehen können.
"""

from typing import List, Dict, Tuple, Optional
from enum import Enum
import random


class ChordType(Enum):
    """Chord types for harmony generation"""
    MAJOR = "major"
    MINOR = "minor"
    DIMINISHED = "dim"
    AUGMENTED = "aug"
    MAJOR_7 = "maj7"
    MINOR_7 = "min7"
    DOMINANT_7 = "dom7"
    SUSPENDED_2 = "sus2"
    SUSPENDED_4 = "sus4"


class Scale(Enum):
    """Musical scales"""
    MAJOR = [0, 2, 4, 5, 7, 9, 11]
    MINOR = [0, 2, 3, 5, 7, 8, 10]
    HARMONIC_MINOR = [0, 2, 3, 5, 7, 8, 11]
    MELODIC_MINOR = [0, 2, 3, 5, 7, 9, 11]
    DORIAN = [0, 2, 3, 5, 7, 9, 10]
    PHRYGIAN = [0, 1, 3, 5, 7, 8, 10]
    LYDIAN = [0, 2, 4, 6, 7, 9, 11]
    MIXOLYDIAN = [0, 2, 4, 5, 7, 9, 10]
    PENTATONIC_MAJOR = [0, 2, 4, 7, 9]
    PENTATONIC_MINOR = [0, 3, 5, 7, 10]
    BLUES = [0, 3, 5, 6, 7, 10]


# Note name to MIDI number mapping
NOTE_TO_MIDI: Dict[str, int] = {
    "C": 0, "C#": 1, "Db": 1,
    "D": 2, "D#": 3, "Eb": 3,
    "E": 4,
    "F": 5, "F#": 6, "Gb": 6,
    "G": 7, "G#": 8, "Ab": 8,
    "A": 9, "A#": 10, "Bb": 10,
    "B": 11
}

MIDI_TO_NOTE: List[str] = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def note_to_midi(note: str, octave: int = 4) -> int:
    """
    Convert note name + octave to MIDI number

    Args:
        note: Note name (e.g., "C", "C#", "Db")
        octave: Octave number (default: 4, middle C)

    Returns:
        MIDI note number (0-127)
    """
    base = NOTE_TO_MIDI.get(note)
    if base is None:
        raise ValueError(f"Invalid note: {note}")
    return base + (octave + 1) * 12


def midi_to_note(midi: int) -> Tuple[str, int]:
    """
    Convert MIDI number to note name + octave

    Args:
        midi: MIDI note number (0-127)

    Returns:
        Tuple of (note_name, octave)
    """
    octave = (midi // 12) - 1
    note = MIDI_TO_NOTE[midi % 12]
    return note, octave


def create_chord(root: int, chord_type: ChordType) -> List[int]:
    """
    Create a chord from a root note

    Args:
        root: Root MIDI note number
        chord_type: Type of chord to create

    Returns:
        List of MIDI note numbers forming the chord
    """
    chord_intervals: Dict[ChordType, List[int]] = {
        ChordType.MAJOR: [0, 4, 7],
        ChordType.MINOR: [0, 3, 7],
        ChordType.DIMINISHED: [0, 3, 6],
        ChordType.AUGMENTED: [0, 4, 8],
        ChordType.MAJOR_7: [0, 4, 7, 11],
        ChordType.MINOR_7: [0, 3, 7, 10],
        ChordType.DOMINANT_7: [0, 4, 7, 10],
        ChordType.SUSPENDED_2: [0, 2, 7],
        ChordType.SUSPENDED_4: [0, 5, 7],
    }

    intervals = chord_intervals[chord_type]
    return [root + interval for interval in intervals]


def create_arpeggio(
    chord: List[int],
    pattern: str = "up",
    octaves: int = 1
) -> List[int]:
    """
    Create an arpeggio pattern from a chord

    Args:
        chord: List of MIDI notes forming a chord
        pattern: Pattern type ("up", "down", "up-down", "random")
        octaves: Number of octaves to span

    Returns:
        List of MIDI notes forming the arpeggio
    """
    arp = []

    for octave in range(octaves):
        octave_shift = octave * 12
        current_chord = [note + octave_shift for note in chord]

        if pattern == "up":
            arp.extend(current_chord)
        elif pattern == "down":
            arp.extend(reversed(current_chord))
        elif pattern == "up-down":
            arp.extend(current_chord)
            arp.extend(reversed(current_chord[1:-1]))
        elif pattern == "random":
            arp.extend(random.sample(current_chord, len(current_chord)))

    return arp


def get_scale_notes(root: int, scale: Scale, octaves: int = 1) -> List[int]:
    """
    Get all notes in a scale across one or more octaves

    Args:
        root: Root MIDI note number
        scale: Scale type
        octaves: Number of octaves to span

    Returns:
        List of MIDI note numbers in the scale
    """
    notes = []
    intervals = scale.value

    for octave in range(octaves):
        octave_shift = octave * 12
        notes.extend([root + interval + octave_shift for interval in intervals])

    return notes


def quantize_to_scale(note: int, root: int, scale: Scale) -> int:
    """
    Quantize a MIDI note to the nearest note in a given scale

    Args:
        note: MIDI note to quantize
        root: Root note of the scale
        scale: Scale type

    Returns:
        Quantized MIDI note number
    """
    # Get scale notes across multiple octaves to cover range
    scale_notes = get_scale_notes(root, scale, octaves=10)

    # Find closest scale note
    closest = min(scale_notes, key=lambda x: abs(x - note))
    return closest


def detect_chord_type(notes: List[int]) -> Optional[ChordType]:
    """
    Detect the chord type from a list of MIDI notes

    Args:
        notes: List of MIDI note numbers

    Returns:
        Detected ChordType or None if not recognized
    """
    if len(notes) < 2:
        return None

    # Normalize to intervals from root
    sorted_notes = sorted(notes)
    root = sorted_notes[0]
    intervals = sorted(set((note - root) % 12 for note in sorted_notes))

    # Match against known chord patterns
    chord_patterns: Dict[Tuple[int, ...], ChordType] = {
        (0, 4, 7): ChordType.MAJOR,
        (0, 3, 7): ChordType.MINOR,
        (0, 3, 6): ChordType.DIMINISHED,
        (0, 4, 8): ChordType.AUGMENTED,
        (0, 4, 7, 11): ChordType.MAJOR_7,
        (0, 3, 7, 10): ChordType.MINOR_7,
        (0, 4, 7, 10): ChordType.DOMINANT_7,
        (0, 2, 7): ChordType.SUSPENDED_2,
        (0, 5, 7): ChordType.SUSPENDED_4,
    }

    return chord_patterns.get(tuple(intervals))


def generate_rhythm_pattern(
    beats: int = 16,
    density: float = 0.5,
    emphasis: List[int] = None
) -> List[bool]:
    """
    Generate a rhythm pattern

    Args:
        beats: Number of beats in the pattern
        density: Probability of a beat being active (0.0 - 1.0)
        emphasis: List of beat positions to emphasize (always active)

    Returns:
        List of booleans indicating active beats
    """
    if emphasis is None:
        emphasis = [0, 4, 8, 12]  # Default: emphasize downbeats

    pattern = [False] * beats

    # Set emphasized beats
    for beat in emphasis:
        if beat < beats:
            pattern[beat] = True

    # Fill in remaining beats based on density
    for i in range(beats):
        if not pattern[i] and random.random() < density:
            pattern[i] = True

    return pattern


def swing_timing(
    positions: List[float],
    swing_amount: float = 0.5
) -> List[float]:
    """
    Apply swing to timing positions

    Args:
        positions: List of note positions (in beats)
        swing_amount: Amount of swing (0.0 = straight, 1.0 = maximum swing)

    Returns:
        List of swung positions
    """
    swung = []

    for pos in positions:
        beat_pos = pos % 1.0
        beat_num = int(pos)

        # Apply swing to off-beats
        if 0.4 < beat_pos < 0.6:  # Near the half-beat
            offset = swing_amount * 0.15  # Shift by up to 15% of a beat
            swung.append(beat_num + beat_pos + offset)
        else:
            swung.append(pos)

    return swung


def velocity_curve(
    count: int,
    curve_type: str = "linear",
    min_vel: int = 40,
    max_vel: int = 120
) -> List[int]:
    """
    Generate a velocity curve for a sequence of notes

    Args:
        count: Number of velocity values to generate
        curve_type: Type of curve ("linear", "exponential", "random", "accent")
        min_vel: Minimum velocity
        max_vel: Maximum velocity

    Returns:
        List of velocity values (0-127)
    """
    velocities = []

    for i in range(count):
        t = i / max(count - 1, 1)  # Normalize to 0-1

        if curve_type == "linear":
            vel = int(min_vel + (max_vel - min_vel) * t)
        elif curve_type == "exponential":
            vel = int(min_vel + (max_vel - min_vel) * (t ** 2))
        elif curve_type == "accent":
            # Accent every 4th note
            vel = max_vel if i % 4 == 0 else min_vel
        elif curve_type == "random":
            vel = random.randint(min_vel, max_vel)
        else:
            vel = min_vel

        velocities.append(max(0, min(127, vel)))

    return velocities


# Common chord progressions (in Roman numeral notation, converted to scale degrees)
CHORD_PROGRESSIONS: Dict[str, List[int]] = {
    "I-IV-V-I": [0, 3, 4, 0],
    "I-V-vi-IV": [0, 4, 5, 3],  # Pop progression
    "ii-V-I": [1, 4, 0],  # Jazz turnaround
    "I-vi-IV-V": [0, 5, 3, 4],  # 50s progression
    "vi-IV-I-V": [5, 3, 0, 4],  # Sensitive progression
}


def apply_progression(
    root: int,
    scale: Scale,
    progression_name: str = "I-IV-V-I"
) -> List[List[int]]:
    """
    Generate a chord progression in a given key

    Args:
        root: Root MIDI note
        scale: Scale to use
        progression_name: Name of the progression

    Returns:
        List of chord note lists
    """
    if progression_name not in CHORD_PROGRESSIONS:
        raise ValueError(f"Unknown progression: {progression_name}")

    degrees = CHORD_PROGRESSIONS[progression_name]
    scale_notes = get_scale_notes(root, scale, octaves=1)
    chords = []

    for degree in degrees:
        chord_root = scale_notes[degree]
        # Build triad from scale degree (simple tertian harmony)
        chord = [
            chord_root,
            scale_notes[(degree + 2) % len(scale_notes)],
            scale_notes[(degree + 4) % len(scale_notes)]
        ]
        chords.append(chord)

    return chords


if __name__ == "__main__":
    # Example usage
    print("=== Music Theory Library Test ===\n")

    # Create a C major chord
    c_major = create_chord(60, ChordType.MAJOR)  # Middle C
    print(f"C Major chord: {c_major}")

    # Create an arpeggio
    arp = create_arpeggio(c_major, pattern="up-down", octaves=2)
    print(f"Arpeggio: {arp}")

    # Get C major scale
    c_major_scale = get_scale_notes(60, Scale.MAJOR, octaves=2)
    print(f"C Major scale: {c_major_scale}")

    # Generate a rhythm
    rhythm = generate_rhythm_pattern(16, density=0.6)
    print(f"Rhythm pattern: {rhythm}")

    # Generate velocity curve
    velocities = velocity_curve(8, curve_type="accent")
    print(f"Velocity curve: {velocities}")

    # Chord progression
    progression = apply_progression(60, Scale.MAJOR, "I-V-vi-IV")
    print(f"I-V-vi-IV progression: {progression}")
