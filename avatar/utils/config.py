"""
Configuration utilities for the Avatar

Loads configuration from environment variables and .env files
"""

from typing import Optional
from pathlib import Path
from dataclasses import dataclass
import os

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False


@dataclass
class AvatarConfig:
    """Central configuration for the Avatar"""

    # AI Configuration
    ai_provider: str = "anthropic"  # "anthropic" or "openai"
    ai_model: str = "claude-3-5-sonnet-20241022"
    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    ai_temperature: float = 0.7
    ai_max_tokens: int = 2000

    # OSC/Ableton Configuration
    osc_daemon_host: str = "127.0.0.1"
    osc_daemon_port: int = 65432
    ableton_osc_send_port: int = 11000
    ableton_osc_receive_port: int = 11001

    # MIDI Configuration
    midi_output_port: Optional[str] = None
    midi_input_port: Optional[str] = None

    # Avatar Configuration
    default_mode: str = "idle"
    window_always_on_top: bool = True
    window_click_through: bool = False

    # Paths
    project_root: Path = Path(__file__).parent.parent.parent
    skills_dir: Path = Path(__file__).parent.parent / "dynamic_tools" / "generated_skills"

    @classmethod
    def load_from_env(cls, env_file: Optional[Path] = None) -> "AvatarConfig":
        """
        Load configuration from environment variables

        Args:
            env_file: Optional path to .env file

        Returns:
            AvatarConfig instance
        """
        # Load .env file if available
        if DOTENV_AVAILABLE:
            if env_file and env_file.exists():
                load_dotenv(env_file)
            else:
                # Try to find .env in project root
                project_root = Path(__file__).parent.parent.parent
                env_path = project_root / ".env"
                if env_path.exists():
                    load_dotenv(env_path)

        # Create config from environment
        return cls(
            # AI
            ai_provider=os.getenv("AVATAR_AI_PROVIDER", "anthropic"),
            ai_model=os.getenv("AVATAR_AI_MODEL", "claude-3-5-sonnet-20241022"),
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            ai_temperature=float(os.getenv("AVATAR_AI_TEMPERATURE", "0.7")),
            ai_max_tokens=int(os.getenv("AVATAR_AI_MAX_TOKENS", "2000")),

            # OSC/Ableton
            osc_daemon_host=os.getenv("OSC_DAEMON_HOST", "127.0.0.1"),
            osc_daemon_port=int(os.getenv("OSC_DAEMON_PORT", "65432")),
            ableton_osc_send_port=int(os.getenv("ABLETON_OSC_SEND_PORT", "11000")),
            ableton_osc_receive_port=int(os.getenv("ABLETON_OSC_RECEIVE_PORT", "11001")),

            # MIDI
            midi_output_port=os.getenv("MIDI_OUTPUT_PORT") or None,
            midi_input_port=os.getenv("MIDI_INPUT_PORT") or None,

            # Avatar
            default_mode=os.getenv("AVATAR_MODE", "idle"),
            window_always_on_top=os.getenv("AVATAR_ALWAYS_ON_TOP", "true").lower() == "true",
            window_click_through=os.getenv("AVATAR_CLICK_THROUGH", "false").lower() == "true",
        )

    def save_to_env(self, env_file: Path) -> None:
        """
        Save configuration to .env file

        Args:
            env_file: Path to .env file
        """
        env_content = f"""# AI API Keys
ANTHROPIC_API_KEY={self.anthropic_api_key or ''}
OPENAI_API_KEY={self.openai_api_key or ''}

# Avatar Configuration
AVATAR_MODE={self.default_mode}
AVATAR_AI_PROVIDER={self.ai_provider}
AVATAR_AI_MODEL={self.ai_model}
AVATAR_AI_TEMPERATURE={self.ai_temperature}
AVATAR_AI_MAX_TOKENS={self.ai_max_tokens}

# Ableton OSC Configuration
OSC_DAEMON_HOST={self.osc_daemon_host}
OSC_DAEMON_PORT={self.osc_daemon_port}
ABLETON_OSC_SEND_PORT={self.ableton_osc_send_port}
ABLETON_OSC_RECEIVE_PORT={self.ableton_osc_receive_port}

# MIDI Configuration
MIDI_OUTPUT_PORT={self.midi_output_port or ''}
MIDI_INPUT_PORT={self.midi_input_port or ''}

# Window Configuration
AVATAR_ALWAYS_ON_TOP={str(self.window_always_on_top).lower()}
AVATAR_CLICK_THROUGH={str(self.window_click_through).lower()}
"""

        with open(env_file, "w") as f:
            f.write(env_content)

        print(f"Configuration saved to {env_file}")


# Global config instance
_config: Optional[AvatarConfig] = None


def get_config() -> AvatarConfig:
    """Get the global configuration instance"""
    global _config

    if _config is None:
        _config = AvatarConfig.load_from_env()

    return _config


def reload_config(env_file: Optional[Path] = None) -> AvatarConfig:
    """Reload configuration from environment"""
    global _config
    _config = AvatarConfig.load_from_env(env_file)
    return _config
