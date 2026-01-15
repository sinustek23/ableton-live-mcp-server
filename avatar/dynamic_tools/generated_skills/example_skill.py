"""
Example Skill - Template for Lock Mode generated skills

Dieses Beispiel zeigt, wie ein auto-generierter Skill aufgebaut ist.
"""

from avatar.dynamic_tools.music_theory import (
    create_chord,
    create_arpeggio,
    ChordType,
    Scale,
    get_scale_notes
)
from avatar.audio.midi_handler import MIDINote


async def execute_skill(midi_handler, ableton_connector, **kwargs):
    """
    Example skill that plays a simple chord progression

    Args:
        midi_handler: MIDIHandler instance for sending MIDI
        ableton_connector: AbletonConnector instance for OSC communication
        **kwargs: Additional parameters (e.g., root_note, tempo)

    Returns:
        Dictionary with execution results
    """
    # Get parameters
    root_note = kwargs.get('root_note', 60)  # Default: Middle C
    tempo = kwargs.get('tempo', 120)

    print(f"[ExampleSkill] Executing with root={root_note}, tempo={tempo}")

    # Create a simple I-IV-V-I progression in C major
    progressions = [
        (root_note, ChordType.MAJOR),      # I
        (root_note + 5, ChordType.MAJOR),  # IV
        (root_note + 7, ChordType.MAJOR),  # V
        (root_note, ChordType.MAJOR),      # I
    ]

    results = []

    for root, chord_type in progressions:
        # Create chord
        chord_notes = create_chord(root, chord_type)

        print(f"[ExampleSkill] Playing {chord_type.value} chord: {chord_notes}")

        # Play chord
        for note in chord_notes:
            midi_note = MIDINote(
                note=note,
                velocity=90,
                duration=0.8
            )
            await midi_handler.send_note_async(midi_note)

        results.append({
            'root': root,
            'chord_type': chord_type.value,
            'notes': chord_notes
        })

        # Wait between chords
        import asyncio
        await asyncio.sleep(1.0)

    print("[ExampleSkill] Execution complete")

    return {
        'status': 'success',
        'chords_played': len(results),
        'results': results
    }


# Metadata (required for Lock Mode)
SKILL_NAME = "example_chord_progression"
SKILL_DESCRIPTION = "Plays a simple I-IV-V-I chord progression in the given key"
SKILL_VERSION = "1.0.0"
SKILL_AUTHOR = "Music Copilot Avatar"


# Optional: Skill configuration
SKILL_CONFIG = {
    'default_root_note': 60,
    'default_tempo': 120,
    'supported_scales': ['major', 'minor'],
}


# Optional: Validation function
def validate_parameters(**kwargs) -> bool:
    """
    Validate skill parameters before execution

    Args:
        **kwargs: Parameters to validate

    Returns:
        True if parameters are valid
    """
    root_note = kwargs.get('root_note', 60)

    # MIDI note must be in valid range
    if not (0 <= root_note <= 127):
        print(f"[ExampleSkill] Invalid root_note: {root_note}")
        return False

    return True


# Optional: Help text
HELP_TEXT = """
Example Chord Progression Skill

Plays a I-IV-V-I chord progression in the given key.

Parameters:
  - root_note (int): MIDI note number for the root (default: 60 = Middle C)
  - tempo (int): Tempo in BPM (default: 120)

Example usage:
  await mode_manager.execute_skill(
      'example_chord_progression',
      root_note=60,
      tempo=100
  )
"""


if __name__ == "__main__":
    """Test the skill standalone"""
    import asyncio
    from avatar.audio.midi_handler import MIDIHandler

    async def test():
        handler = MIDIHandler()
        if handler.open_output():
            result = await execute_skill(
                midi_handler=handler,
                ableton_connector=None,
                root_note=60,
                tempo=120
            )
            print(f"Result: {result}")
            handler.close()

    asyncio.run(test())
