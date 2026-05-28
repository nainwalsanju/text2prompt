#!/bin/bash
set -e

echo "📦 Building text2prompt v2.0.0..."

APP_NAME="text2prompt"
VERSION="2.0.0"
DIST_DIR="dist"
APP_BUNDLE="$DIST_DIR/$APP_NAME.app"
DMG_FILE="$DIST_DIR/${APP_NAME}-${VERSION}.dmg"
VENV=".venv"

# Clean previous builds
rm -rf build "$DIST_DIR"

# Ensure venv exists
if [ ! -d "$VENV" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV"
fi

# Install dependencies
echo "📥 Installing dependencies..."
"$VENV/bin/pip" install --quiet py2app "setuptools<70"

# Install the package (non-editable so py2app can find it)
echo "📥 Installing text2prompt..."
"$VENV/bin/pip" install --quiet .

# Temporarily move pyproject.toml (py2app/setuptools conflict)
mv pyproject.toml pyproject.toml.bak 2>/dev/null || true

# Build the app bundle
echo "🔨 Building .app bundle..."
"$VENV/bin/python" setup.py py2app

# Restore pyproject.toml
mv pyproject.toml.bak pyproject.toml

# Copy icon into bundle
if [ -f "assets/text2prompt.icns" ]; then
    cp assets/text2prompt.icns "$APP_BUNDLE/Contents/Resources/"
    echo "🖼️ Icon added"
fi

# Determine the Python version inside the venv
PYVER=$("$VENV/bin/python3" -c 'import sys; print(f"python{sys.version_info.major}.{sys.version_info.minor}")')

# Verify text2prompt is in bundle
if [ ! -d "$APP_BUNDLE/Contents/Resources/lib/$PYVER/text2prompt" ]; then
    SITE_PKG=$(find "$VENV/lib" -name "text2prompt" -type d | head -1)
    if [ -n "$SITE_PKG" ]; then
        cp -r "$SITE_PKG" "$APP_BUNDLE/Contents/Resources/lib/$PYVER/"
        echo "📁 Source copied from site-packages"
    fi
fi

# Create DMG
echo "💿 Creating DMG..."
hdiutil create -volname "$APP_NAME" -srcfolder "$APP_BUNDLE" -ov -format UDZO "$DMG_FILE"

echo ""
echo "✅ Build complete!"
echo "📁 App bundle: $APP_BUNDLE"
echo "💿 DMG: $DMG_FILE"
echo ""
echo "To test: open $APP_BUNDLE"
echo "To distribute: share $DMG_FILE"
