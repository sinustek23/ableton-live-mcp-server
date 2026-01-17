#!/usr/bin/env python3
"""
Quick test to verify new bass clef avatar integration
"""

import sys
sys.path.insert(0, '/home/user/ableton-live-mcp-server/DAIW')

from PyQt6.QtWidgets import QApplication
from daiw.gui.bass_clef_widget import BassClefWidget, AvatarState

def test_avatar():
    """Test that avatar loads and works"""
    app = QApplication(sys.argv)

    print("Testing new bass clef avatar...")

    # Create avatar
    avatar = BassClefWidget()

    # Test all states
    states = [
        AvatarState.IDLE,
        AvatarState.THINKING,
        AvatarState.JAMMING,
        AvatarState.LEARNING,
        AvatarState.LOCKED,
        AvatarState.HAPPY,
        AvatarState.ERROR,
        AvatarState.SLEEPING,
    ]

    print("✓ Avatar created")

    for state in states:
        avatar.set_state(state)
        print(f"✓ State {state.value} works")

    print("\n✅ All tests passed!")
    print("New bass clef avatar is working correctly!")

    return 0

if __name__ == "__main__":
    sys.exit(test_avatar())
