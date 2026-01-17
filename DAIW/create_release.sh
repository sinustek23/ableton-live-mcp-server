#!/usr/bin/env bash
# Create DAIW Release Package
# Generates downloadable archives for distribution

set -e

VERSION="2.0.0"
PROJECT="daiw"
RELEASE_DIR="release"

echo "Creating DAIW v${VERSION} release package..."

# Clean previous releases
rm -rf ${RELEASE_DIR}
mkdir -p ${RELEASE_DIR}

# 1. Source Archive
echo "[1/5] Creating source archive..."
git archive --format=tar.gz --prefix=${PROJECT}-${VERSION}/ HEAD > ${RELEASE_DIR}/${PROJECT}-${VERSION}-source.tar.gz
git archive --format=zip --prefix=${PROJECT}-${VERSION}/ HEAD > ${RELEASE_DIR}/${PROJECT}-${VERSION}-source.zip
echo "✓ Source archives created"

# 2. Python Wheel
echo "[2/5] Building Python wheel..."
python -m build --wheel --outdir ${RELEASE_DIR}
echo "✓ Python wheel created"

# 3. Standalone Executables (optional - requires PyInstaller)
if command -v pyinstaller &> /dev/null; then
    echo "[3/5] Building standalone executables..."

    # Create spec file
    cat > ${PROJECT}.spec << EOF
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['daiw/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('daiw/gui', 'daiw/gui'),
        ('daiw/dynamic_tools', 'daiw/dynamic_tools'),
        ('.env.template', '.'),
    ],
    hiddenimports=[
        'PyQt6',
        'qasync',
        'anthropic',
        'openai',
        'langchain',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='${PROJECT}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico'
)
EOF

    pyinstaller ${PROJECT}.spec --distpath ${RELEASE_DIR} --workpath build --clean
    echo "✓ Standalone executable created"
else
    echo "[3/5] PyInstaller not found, skipping standalone executable"
fi

# 4. Documentation Package
echo "[4/5] Creating documentation package..."
tar -czf ${RELEASE_DIR}/${PROJECT}-${VERSION}-docs.tar.gz docs/ *.md
echo "✓ Documentation package created"

# 5. Demo Package
echo "[5/5] Creating demo package..."
mkdir -p ${RELEASE_DIR}/demo
cp demo_visual_effects.py ${RELEASE_DIR}/demo/
cp -r daiw/gui ${RELEASE_DIR}/demo/
tar -czf ${RELEASE_DIR}/${PROJECT}-${VERSION}-demo.tar.gz -C ${RELEASE_DIR} demo
rm -rf ${RELEASE_DIR}/demo
echo "✓ Demo package created"

# Generate checksums
echo "Generating checksums..."
cd ${RELEASE_DIR}
sha256sum * > SHA256SUMS
cd ..

# List created files
echo ""
echo "Release packages created in ${RELEASE_DIR}/:"
ls -lh ${RELEASE_DIR}/

echo ""
echo "✅ Release v${VERSION} ready for distribution!"
echo ""
echo "Next steps:"
echo "1. Test installation from packages"
echo "2. Create GitHub release and upload files"
echo "3. Upload wheel to PyPI: twine upload ${RELEASE_DIR}/${PROJECT}-${VERSION}-*.whl"
echo "4. Announce release!"
