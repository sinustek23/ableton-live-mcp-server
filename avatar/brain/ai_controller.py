"""
AI Controller - The brain of the avatar

Manages AI interactions, pattern learning, and decision making
"""

from typing import Optional, List, Dict, Any, Callable
import asyncio
from enum import Enum
from dataclasses import dataclass
import os
from pathlib import Path

# AI imports (with fallback if not available)
try:
    from langchain_anthropic import ChatAnthropic
    from langchain_openai import ChatOpenAI
    from langchain.schema import HumanMessage, SystemMessage, AIMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("[AIController] Warning: LangChain not available. AI features will be limited.")


@dataclass
class AIConfig:
    """Configuration for AI controller"""
    provider: str = "anthropic"  # "anthropic" or "openai"
    model: str = "claude-3-5-sonnet-20241022"
    api_key: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2000


class AIController:
    """
    Central AI controller for the avatar
    """

    def __init__(self, config: Optional[AIConfig] = None):
        self.config = config or AIConfig()

        # Get API key from environment if not provided
        if not self.config.api_key:
            if self.config.provider == "anthropic":
                self.config.api_key = os.getenv("ANTHROPIC_API_KEY")
            elif self.config.provider == "openai":
                self.config.api_key = os.getenv("OPENAI_API_KEY")

        # Initialize LLM
        self._llm = None
        if LANGCHAIN_AVAILABLE:
            self._initialize_llm()

        # Conversation history
        self._conversation_history: List[Any] = []

        # System prompt
        self._system_prompt = self._create_system_prompt()

    def _initialize_llm(self) -> None:
        """Initialize the language model"""
        try:
            if self.config.provider == "anthropic":
                self._llm = ChatAnthropic(
                    model=self.config.model,
                    anthropic_api_key=self.config.api_key,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens
                )
            elif self.config.provider == "openai":
                self._llm = ChatOpenAI(
                    model=self.config.model,
                    openai_api_key=self.config.api_key,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens
                )
            print(f"[AIController] Initialized {self.config.provider} model: {self.config.model}")

        except Exception as e:
            print(f"[AIController] Error initializing LLM: {e}")
            self._llm = None

    def _create_system_prompt(self) -> str:
        """Create the system prompt for the AI"""
        return """You are a Music Copilot AI assistant, embodied as a Bass Clef avatar.
You are an expert in music theory, harmony, rhythm, and MIDI composition.

Your capabilities:
- Generate musical ideas (melodies, harmonies, rhythms)
- Analyze user's playing patterns
- Learn from user behavior and adapt
- Create Python code to automate musical tasks (in Lock Mode)

You have access to a music_theory library with functions like:
- create_chord(root, chord_type)
- create_arpeggio(chord, pattern, octaves)
- get_scale_notes(root, scale, octaves)
- generate_rhythm_pattern(beats, density)
- apply_progression(root, scale, progression_name)

When in Lock Mode, you can write Python scripts that will be executed as new skills.
These scripts should use the music_theory library and follow best practices.

Always be creative, musical, and helpful. Think like a jazz musician - responsive,
adaptive, and always ready to jam!
"""

    async def chat(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Send a message to the AI and get a response

        Args:
            message: User message
            context: Optional context dictionary (mode, current state, etc.)

        Returns:
            AI response as string
        """
        if not self._llm:
            return "AI not available. Please check your API configuration."

        try:
            # Build messages
            messages = [SystemMessage(content=self._system_prompt)]

            # Add context if provided
            if context:
                context_msg = f"Current context: {context}"
                messages.append(SystemMessage(content=context_msg))

            # Add conversation history
            messages.extend(self._conversation_history[-10:])  # Keep last 10 messages

            # Add current message
            messages.append(HumanMessage(content=message))

            # Get response
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                self._llm.invoke,
                messages
            )

            # Update conversation history
            self._conversation_history.append(HumanMessage(content=message))
            self._conversation_history.append(response)

            return response.content

        except Exception as e:
            print(f"[AIController] Error in chat: {e}")
            return f"Error: {str(e)}"

    async def generate_musical_idea(self, prompt: str, constraints: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a musical idea based on a prompt

        Args:
            prompt: Description of what to generate
            constraints: Optional constraints (key, scale, tempo, etc.)

        Returns:
            Dictionary with musical data (notes, rhythm, etc.)
        """
        context = {
            "task": "generate_musical_idea",
            "constraints": constraints or {}
        }

        full_prompt = f"""Generate a musical idea: {prompt}

Constraints: {constraints or 'None'}

Respond with a JSON object containing:
- notes: List of MIDI note numbers
- durations: List of note durations in beats
- velocities: List of velocities (0-127)
- description: Brief description of the idea

Example:
{{
  "notes": [60, 64, 67, 72],
  "durations": [0.5, 0.5, 0.5, 1.0],
  "velocities": [100, 90, 85, 110],
  "description": "Ascending C major arpeggio"
}}
"""

        response = await self.chat(full_prompt, context)

        # Try to parse JSON response
        try:
            import json
            # Extract JSON from response (might have markdown formatting)
            json_str = response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()

            return json.loads(json_str)

        except Exception as e:
            print(f"[AIController] Error parsing musical idea: {e}")
            return {
                "notes": [60, 64, 67],  # Default C major chord
                "durations": [1.0, 1.0, 1.0],
                "velocities": [100, 100, 100],
                "description": "Default C major chord (parsing failed)"
            }

    async def analyze_pattern(self, midi_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze a MIDI pattern to extract musical features

        Args:
            midi_data: List of MIDI events (note, time, velocity)

        Returns:
            Analysis results
        """
        context = {
            "task": "analyze_pattern",
            "data_length": len(midi_data)
        }

        prompt = f"""Analyze this MIDI pattern and extract key features:

MIDI Data: {midi_data[:20]}  # Show first 20 events

Identify:
1. Key/scale
2. Chord progressions
3. Rhythmic patterns
4. Playing style (e.g., "arpeggiated chords on downbeats")

Respond with a JSON object containing your analysis.
"""

        response = await self.chat(prompt, context)

        try:
            import json
            json_str = response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()

            return json.loads(json_str)

        except Exception as e:
            print(f"[AIController] Error parsing pattern analysis: {e}")
            return {
                "key": "C major",
                "chords": ["C", "Am", "F", "G"],
                "rhythm": "quarter notes",
                "style": "simple chord progression"
            }

    async def generate_skill_code(self, task_description: str, pattern_analysis: Optional[Dict] = None) -> str:
        """
        Generate Python code for a new skill (Lock Mode)

        Args:
            task_description: Description of what the skill should do
            pattern_analysis: Optional analysis of user's playing pattern

        Returns:
            Python code as string
        """
        context = {
            "task": "generate_skill_code",
            "pattern_analysis": pattern_analysis
        }

        prompt = f"""Create a Python skill (function) that: {task_description}

{f'Based on this pattern analysis: {pattern_analysis}' if pattern_analysis else ''}

The code should:
1. Import necessary functions from avatar.dynamic_tools.music_theory
2. Define an async function called `execute_skill(midi_handler, ableton_connector, **kwargs)`
3. Use the music_theory library functions
4. Be well-documented with docstrings
5. Handle errors gracefully

Example structure:
```python
from avatar.dynamic_tools.music_theory import create_chord, ChordType, create_arpeggio
from avatar.audio.midi_handler import MIDINote

async def execute_skill(midi_handler, ableton_connector, **kwargs):
    \"\"\"
    Brief description of what this skill does
    \"\"\"
    # Your code here
    pass

# Metadata
SKILL_NAME = "descriptive_name"
SKILL_DESCRIPTION = "Brief description"
```

Generate the complete, working code now:
"""

        response = await self.chat(prompt, context)

        # Extract code block
        if "```python" in response:
            code = response.split("```python")[1].split("```")[0].strip()
        elif "```" in response:
            code = response.split("```")[1].split("```")[0].strip()
        else:
            code = response

        return code

    def clear_history(self) -> None:
        """Clear conversation history"""
        self._conversation_history.clear()
        print("[AIController] Conversation history cleared")

    def get_history_length(self) -> int:
        """Get length of conversation history"""
        return len(self._conversation_history)
