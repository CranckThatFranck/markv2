#!/bin/bash
set -e

# Build a minimal Debian package for mark-core-v2
# Usage: ./build-deb.sh

WORK_DIR=$(mktemp -d)
PACKAGE_NAME="mark-core-v2"
VERSION="0.1.0"
RELEASE="1"
DEB_FILE="${PACKAGE_NAME}_${VERSION}-${RELEASE}_all.deb"

echo "Building Debian package..."
echo "Working directory: $WORK_DIR"

# Create package structure
DEBIAN_DIR="$WORK_DIR/DEBIAN"
mkdir -p "$DEBIAN_DIR"
mkdir -p "$WORK_DIR/opt/jarvis/backend"
mkdir -p "$WORK_DIR/etc/systemd/system"

# Copy control files
cp packaging/deb/control "$DEBIAN_DIR/"
cp packaging/deb/postinst "$DEBIAN_DIR/"
cp packaging/deb/prerm "$DEBIAN_DIR/"
chmod 755 "$DEBIAN_DIR/postinst"
chmod 755 "$DEBIAN_DIR/prerm"

# Copy backend code (exclude unnecessary files)
rsync -av --exclude='.git' --exclude='.venv' \
    --exclude='__pycache__' --exclude='*.pyc' \
    --exclude='.mark-runtime' \
    --exclude='packaging' \
    --exclude='.vscode' \
    . "$WORK_DIR/opt/jarvis/backend/"

# Create .venv in package
cd "$WORK_DIR/opt/jarvis/backend"
python3.12 -m venv .venv
.venv/bin/pip install -U pip setuptools wheel > /dev/null 2>&1
.venv/bin/pip install -r requirements-backend.txt > /dev/null 2>&1
cd - > /dev/null

# Copy systemd files
cp systemd/mark-core-v2.service "$WORK_DIR/etc/systemd/system/"
cp systemd/mark-core-v2.socket "$WORK_DIR/etc/systemd/system/"

# Create the package
fakeroot dpkg-deb --build "$WORK_DIR" "$DEB_FILE"

echo "Package created: $DEB_FILE"
echo "Install with: sudo dpkg -i $DEB_FILE"

# Cleanup
rm -rf "$WORK_DIR"
