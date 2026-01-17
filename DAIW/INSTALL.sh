#!/usr/bin/env bash
# DAIW Automated Installer
# Supports: Linux, macOS, Windows (Git Bash/WSL)

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
cat << "EOF"
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║    DAIW - Digital AI Workspace                         ║
║    The Ultimate AI-Powered Creative Companion          ║
║                                                          ║
║    v2.0 - Beautiful, Fast, Universal                    ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Detect OS
OS="$(uname -s)"
case "${OS}" in
    Linux*)     PLATFORM=Linux;;
    Darwin*)    PLATFORM=macOS;;
    CYGWIN*|MINGW*|MSYS*) PLATFORM=Windows;;
    *)          PLATFORM="UNKNOWN";;
esac

echo -e "${GREEN}✓${NC} Detected platform: ${PLATFORM}"

# Check Python version
echo -e "\n${BLUE}[1/7]${NC} Checking Python installation..."

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗${NC} Python 3 not found!"
    echo "Please install Python 3.10+ from https://www.python.org"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓${NC} Python ${PYTHON_VERSION} found"

# Check if version is >= 3.10
REQUIRED_VERSION="3.10"
if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${YELLOW}⚠${NC} Warning: Python 3.10+ recommended (found ${PYTHON_VERSION})"
fi

# Create virtual environment
echo -e "\n${BLUE}[2/7]${NC} Creating virtual environment..."

if [ -d "venv" ]; then
    echo -e "${YELLOW}⚠${NC} Virtual environment already exists, skipping..."
else
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
fi

# Activate virtual environment
echo -e "\n${BLUE}[3/7]${NC} Activating virtual environment..."

if [ "${PLATFORM}" = "Windows" ]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

echo -e "${GREEN}✓${NC} Virtual environment activated"

# Upgrade pip
echo -e "\n${BLUE}[4/7]${NC} Upgrading pip..."
python -m pip install --upgrade pip setuptools wheel --quiet
echo -e "${GREEN}✓${NC} pip upgraded"

# Install dependencies
echo -e "\n${BLUE}[5/7]${NC} Installing Python dependencies..."
echo "This may take a few minutes..."

pip install -r requirements.txt --quiet

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Dependencies installed successfully"
else
    echo -e "${RED}✗${NC} Failed to install dependencies"
    exit 1
fi

# Install DAIW package
echo -e "\n${BLUE}[6/7]${NC} Installing DAIW..."

pip install -e . --quiet

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} DAIW installed successfully"
else
    echo -e "${RED}✗${NC} Failed to install DAIW"
    exit 1
fi

# Create configuration file
echo -e "\n${BLUE}[7/7]${NC} Creating configuration..."

if [ ! -f ".env" ]; then
    cp .env.template .env
    echo -e "${GREEN}✓${NC} Configuration file created (.env)"
    echo -e "${YELLOW}⚠${NC} Please edit .env and add your API keys!"
else
    echo -e "${YELLOW}⚠${NC} Configuration file already exists, skipping..."
fi

# Optional: Build C++ extensions
echo -e "\n${BLUE}[Optional]${NC} Build C++ extensions for maximum performance?"
echo "This requires CMake and a C++ compiler."
read -p "Build C++ extensions? (y/N): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "\n${BLUE}Building C++ extensions...${NC}"

    # Check for CMake
    if ! command -v cmake &> /dev/null; then
        echo -e "${RED}✗${NC} CMake not found!"
        echo "Install CMake:"
        echo "  macOS: brew install cmake"
        echo "  Linux: sudo apt install cmake"
        echo "  Windows: https://cmake.org/download/"
    else
        cd cpp_extensions
        mkdir -p build
        cd build

        cmake .. -DCMAKE_BUILD_TYPE=Release

        if [ $? -eq 0 ]; then
            cmake --build . -j$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4)

            if [ $? -eq 0 ]; then
                cmake --install . --prefix $(python -c "import site; print(site.getsitepackages()[0])")
                echo -e "${GREEN}✓${NC} C++ extensions built and installed!"
                echo -e "${GREEN}✓${NC} DAIW now has <10ms latency!"
            else
                echo -e "${YELLOW}⚠${NC} C++ build failed, continuing with Python-only version"
            fi
        else
            echo -e "${YELLOW}⚠${NC} CMake configuration failed"
        fi

        cd ../..
    fi
fi

# Installation complete
echo -e "\n${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                          ║${NC}"
echo -e "${GREEN}║    ✓ DAIW Installation Complete!                        ║${NC}"
echo -e "${GREEN}║                                                          ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"

echo -e "\n${BLUE}Next Steps:${NC}"
echo -e "  1. Edit ${YELLOW}.env${NC} and add your API keys (Anthropic/OpenAI)"
echo -e "  2. Launch DAIW:"
echo -e "     ${GREEN}source venv/bin/activate${NC}  # or venv\\Scripts\\activate on Windows"
echo -e "     ${GREEN}daiw${NC}"
echo -e "\n  3. Try the visual effects demo:"
echo -e "     ${GREEN}python demo_visual_effects.py${NC}"
echo -e "\n  4. Read the documentation:"
echo -e "     ${BLUE}docs/QUICKSTART.md${NC}"
echo -e "     ${BLUE}docs/VISUAL_ENHANCEMENTS.md${NC}"
echo -e "     ${BLUE}docs/FL_STUDIO_INTEGRATION.md${NC}"

echo -e "\n${YELLOW}Optional:${NC}"
echo -e "  - Start CollabNet server: ${GREEN}daiw-server${NC}"
echo -e "  - Read keyboard shortcuts: ${BLUE}docs/KEYBOARD_SHORTCUTS.md${NC}"

echo -e "\n${BLUE}Support:${NC}"
echo -e "  - Documentation: ${BLUE}docs/${NC}"
echo -e "  - Issues: ${BLUE}https://github.com/yourusername/daiw/issues${NC}"

echo -e "\n${GREEN}Happy creating! 🎵✨${NC}\n"
