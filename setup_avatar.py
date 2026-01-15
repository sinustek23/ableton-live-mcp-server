#!/usr/bin/env python3
"""
Setup Script for Music Copilot Avatar

Validiert die Umgebung und installiert Dependencies
"""

import sys
import subprocess
import socket
from pathlib import Path
from typing import List, Tuple


class Colors:
    """ANSI color codes"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str) -> None:
    """Print a section header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.RESET}\n")


def print_success(text: str) -> None:
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")


def print_warning(text: str) -> None:
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")


def print_error(text: str) -> None:
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")


def check_python_version() -> bool:
    """Check Python version"""
    print_header("Checking Python Version")

    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")

    if version.major == 3 and version.minor >= 10:
        print_success(f"Python {version.major}.{version.minor} is compatible")
        return True
    else:
        print_error(f"Python 3.10+ required, found {version.major}.{version.minor}")
        return False


def check_port_available(port: int, name: str) -> bool:
    """Check if a port is available"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()

        if result == 0:
            print_warning(f"Port {port} ({name}) is in use - daemon might be running")
            return True
        else:
            print_warning(f"Port {port} ({name}) is not in use - daemon needs to be started")
            return False

    except Exception as e:
        print_error(f"Error checking port {port}: {e}")
        return False


def check_ports() -> Tuple[bool, bool, bool]:
    """Check required ports"""
    print_header("Checking Ports")

    daemon_port = check_port_available(65432, "OSC Daemon Socket")
    osc_send = check_port_available(11000, "Ableton OSC Send")
    osc_receive = check_port_available(11001, "Ableton OSC Receive")

    return daemon_port, osc_send, osc_receive


def check_midi_devices() -> bool:
    """Check available MIDI devices"""
    print_header("Checking MIDI Devices")

    try:
        import mido

        print("Available MIDI output ports:")
        output_ports = mido.get_output_names()

        if output_ports:
            for port in output_ports:
                print(f"  - {port}")
            print_success(f"Found {len(output_ports)} MIDI output port(s)")
            return True
        else:
            print_warning("No MIDI output ports found")
            print("  You may need to create a virtual MIDI port")
            print("  On Windows: Use loopMIDI or similar")
            print("  On macOS: Use IAC Driver (Audio MIDI Setup)")
            print("  On Linux: Use ALSA or JACK")
            return False

    except ImportError:
        print_error("mido not installed - run: pip install mido")
        return False
    except Exception as e:
        print_error(f"Error checking MIDI devices: {e}")
        return False


def check_api_keys() -> Tuple[bool, bool]:
    """Check for AI API keys"""
    print_header("Checking AI API Keys")

    import os

    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    if anthropic_key:
        print_success("ANTHROPIC_API_KEY found")
    else:
        print_warning("ANTHROPIC_API_KEY not set")

    if openai_key:
        print_success("OPENAI_API_KEY found")
    else:
        print_warning("OPENAI_API_KEY not set")

    if not anthropic_key and not openai_key:
        print_warning("No AI API keys found. Set at least one:")
        print("  export ANTHROPIC_API_KEY=your_key")
        print("  export OPENAI_API_KEY=your_key")

    return bool(anthropic_key), bool(openai_key)


def check_dependencies() -> List[str]:
    """Check required Python packages"""
    print_header("Checking Dependencies")

    required_packages = [
        "PyQt6",
        "qasync",
        "mido",
        "python-osc",
        "librosa",
        "langchain",
        "fastmcp",
    ]

    missing = []

    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print_success(f"{package} installed")
        except ImportError:
            print_error(f"{package} not installed")
            missing.append(package)

    return missing


def install_dependencies(packages: List[str]) -> bool:
    """Install missing dependencies"""
    if not packages:
        return True

    print_header("Installing Missing Dependencies")

    print(f"Installing: {', '.join(packages)}")

    try:
        subprocess.check_call([
            sys.executable,
            "-m",
            "pip",
            "install",
            *packages
        ])
        print_success("Dependencies installed successfully")
        return True

    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install dependencies: {e}")
        return False


def create_env_template() -> None:
    """Create .env template file"""
    print_header("Creating Environment Template")

    env_path = Path(__file__).parent / ".env.template"

    env_content = """# AI API Keys (set at least one)
ANTHROPIC_API_KEY=your_anthropic_key_here
OPENAI_API_KEY=your_openai_key_here

# Avatar Configuration
AVATAR_MODE=idle
AVATAR_AI_PROVIDER=anthropic  # or openai
AVATAR_AI_MODEL=claude-3-5-sonnet-20241022

# Ableton OSC Configuration
OSC_DAEMON_HOST=127.0.0.1
OSC_DAEMON_PORT=65432
ABLETON_OSC_SEND_PORT=11000
ABLETON_OSC_RECEIVE_PORT=11001

# MIDI Configuration
MIDI_OUTPUT_PORT=  # Leave empty for auto-detect
MIDI_INPUT_PORT=   # Leave empty for auto-detect
"""

    with open(env_path, "w") as f:
        f.write(env_content)

    print_success(f"Created .env.template at {env_path}")
    print("Copy to .env and fill in your API keys:")
    print(f"  cp .env.template .env")


def main():
    """Main setup routine"""
    print(f"\n{Colors.BOLD}Music Copilot Avatar - Setup{Colors.RESET}")

    all_checks_passed = True

    # 1. Check Python version
    if not check_python_version():
        all_checks_passed = False

    # 2. Check ports
    daemon_port, osc_send, osc_receive = check_ports()
    if not daemon_port:
        print_warning("OSC Daemon not running. Start with: python osc_daemon.py")

    # 3. Check MIDI devices
    if not check_midi_devices():
        all_checks_passed = False

    # 4. Check API keys
    anthropic, openai = check_api_keys()
    if not anthropic and not openai:
        print_warning("AI features will not work without API keys")

    # 5. Check dependencies
    missing = check_dependencies()

    # 6. Install missing dependencies if needed
    if missing:
        print(f"\nFound {len(missing)} missing package(s)")
        response = input("Install missing packages? [y/N]: ").strip().lower()

        if response == 'y':
            if install_dependencies(missing):
                print_success("All dependencies installed")
            else:
                all_checks_passed = False
                print_error("Some dependencies failed to install")
        else:
            all_checks_passed = False
            print_warning("Skipped dependency installation")

    # 7. Create .env template
    create_env_template()

    # Summary
    print_header("Setup Summary")

    if all_checks_passed:
        print_success("All checks passed!")
        print("\nNext steps:")
        print("  1. Make sure OSC Daemon is running:")
        print("     python osc_daemon.py")
        print("  2. Set your API keys in .env file")
        print("  3. Make sure AbletonOSC is installed in Ableton Live")
        print("  4. Start the avatar:")
        print("     python avatar/main.py")
    else:
        print_warning("Some checks failed. Please resolve issues above.")

    print()


if __name__ == "__main__":
    main()
