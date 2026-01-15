"""
DAIW - Digital AI Workspace
Setup script for installation
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip()
        for line in requirements_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="daiw",
    version="1.5.0",
    description="Digital AI Workspace - AI-Powered Collaborative Music Production Platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="DAIW Team",
    author_email="team@daiw.ai",
    url="https://github.com/yourusername/DAIW",
    project_urls={
        "Documentation": "https://github.com/yourusername/DAIW/tree/main/docs",
        "Source": "https://github.com/yourusername/DAIW",
        "Tracker": "https://github.com/yourusername/DAIW/issues",
    },
    packages=find_packages(include=["daiw", "daiw.*"]),
    include_package_data=True,
    package_data={
        "daiw": ["**/*.ui", "**/*.qss", "**/*.json"],
    },
    install_requires=requirements,
    extras_require={
        "dev": [
            "black>=24.4.2",
            "mypy>=1.10.0",
            "pytest>=8.2.0",
            "pytest-asyncio>=0.23.6",
            "pytest-cov>=5.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "daiw=daiw.main:main",
            "daiw-server=daiw.network.collabnet_server:run_server",
        ],
    },
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Multimedia :: Sound/Audio :: MIDI",
        "Topic :: Artistic Software",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords="music-production ai ableton midi collaboration daw audio real-time",
    license="MIT",
    zip_safe=False,
)
