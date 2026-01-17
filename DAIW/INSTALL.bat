@echo off
REM DAIW Automated Installer for Windows
REM Requires: Python 3.10+

setlocal enabledelayedexpansion

color 0B
echo ╔══════════════════════════════════════════════════════════╗
echo ║                                                          ║
echo ║    DAIW - Digital AI Workspace                         ║
echo ║    The Ultimate AI-Powered Creative Companion          ║
echo ║                                                          ║
echo ║    v2.0 - Beautiful, Fast, Universal                    ║
echo ║                                                          ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

REM Check Python
echo [1/7] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [✗] Python not found!
    echo.
    echo Please install Python 3.10+ from https://www.python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo [✓] Python %PYTHON_VERSION% found
echo.

REM Create virtual environment
echo [2/7] Creating virtual environment...
if exist venv (
    echo [⚠] Virtual environment already exists, skipping...
) else (
    python -m venv venv
    if errorlevel 1 (
        echo [✗] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [✓] Virtual environment created
)
echo.

REM Activate virtual environment
echo [3/7] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [✗] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [✓] Virtual environment activated
echo.

REM Upgrade pip
echo [4/7] Upgrading pip...
python -m pip install --upgrade pip setuptools wheel --quiet
if errorlevel 1 (
    echo [⚠] Warning: Failed to upgrade pip
)
echo [✓] pip upgraded
echo.

REM Install dependencies
echo [5/7] Installing Python dependencies...
echo This may take a few minutes...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [✗] Failed to install dependencies
    echo.
    echo Try running manually:
    echo   pip install -r requirements.txt
    pause
    exit /b 1
)
echo [✓] Dependencies installed successfully
echo.

REM Install DAIW
echo [6/7] Installing DAIW...
pip install -e . --quiet
if errorlevel 1 (
    echo [✗] Failed to install DAIW
    pause
    exit /b 1
)
echo [✓] DAIW installed successfully
echo.

REM Create configuration
echo [7/7] Creating configuration...
if not exist .env (
    copy .env.template .env >nul
    echo [✓] Configuration file created (.env)
    echo [⚠] Please edit .env and add your API keys!
) else (
    echo [⚠] Configuration file already exists, skipping...
)
echo.

REM Optional: C++ extensions
echo [Optional] Build C++ extensions for maximum performance?
echo This requires Visual Studio 2019+ with C++ tools and CMake.
set /p BUILD_CPP="Build C++ extensions? (y/N): "

if /i "%BUILD_CPP%"=="y" (
    echo.
    echo Building C++ extensions...

    REM Check for CMake
    cmake --version >nul 2>&1
    if errorlevel 1 (
        echo [✗] CMake not found!
        echo.
        echo Install CMake from: https://cmake.org/download/
        echo Or use: winget install cmake
    ) else (
        cd cpp_extensions
        if not exist build mkdir build
        cd build

        cmake .. -G "Visual Studio 16 2019" -DCMAKE_BUILD_TYPE=Release
        if errorlevel 1 (
            echo [⚠] CMake configuration failed
        ) else (
            cmake --build . --config Release
            if errorlevel 1 (
                echo [⚠] C++ build failed, continuing with Python-only version
            ) else (
                cmake --install . --prefix %VIRTUAL_ENV%\Lib\site-packages
                echo [✓] C++ extensions built and installed!
                echo [✓] DAIW now has ^<10ms latency!
            )
        )

        cd ..\..
    )
)
echo.

REM Installation complete
color 0A
echo ╔══════════════════════════════════════════════════════════╗
echo ║                                                          ║
echo ║    ✓ DAIW Installation Complete!                        ║
echo ║                                                          ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

color 07
echo Next Steps:
echo   1. Edit .env and add your API keys (Anthropic/OpenAI)
echo   2. Launch DAIW:
echo      venv\Scripts\activate
echo      daiw
echo.
echo   3. Try the visual effects demo:
echo      python demo_visual_effects.py
echo.
echo   4. Read the documentation:
echo      docs\QUICKSTART.md
echo      docs\VISUAL_ENHANCEMENTS.md
echo      docs\FL_STUDIO_INTEGRATION.md
echo.

echo Optional:
echo   - Start CollabNet server: daiw-server
echo   - Read keyboard shortcuts: docs\KEYBOARD_SHORTCUTS.md
echo.

echo Support:
echo   - Documentation: docs\
echo   - Issues: https://github.com/yourusername/daiw/issues
echo.

echo Happy creating! 🎵✨
echo.
pause
