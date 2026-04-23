#!/bin/bash
set -e

# Build a minimal Debian package for mark-core-v2
# Usage: ./build-deb.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
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
mkdir -p "$WORK_DIR/etc/mark-core-v2"

# Copy control files
cp "$SCRIPT_DIR/deb/control" "$DEBIAN_DIR/"
cp "$SCRIPT_DIR/deb/postinst" "$DEBIAN_DIR/"
cp "$SCRIPT_DIR/deb/prerm" "$DEBIAN_DIR/"
chmod 755 "$DEBIAN_DIR/postinst"
chmod 755 "$DEBIAN_DIR/prerm"

# Copy backend code (exclude unnecessary files)
rsync -av --exclude='.git' --exclude='.venv' \
    --exclude='__pycache__' --exclude='*.pyc' \
    --exclude='.mark-runtime' \
    --exclude='packaging' \
    --exclude='.vscode' \
    "$REPO_ROOT/" "$WORK_DIR/opt/jarvis/backend/"

# Copy systemd files
cp "$REPO_ROOT/systemd/mark-core-v2.service" "$WORK_DIR/etc/systemd/system/"
cp "$REPO_ROOT/systemd/mark-core-v2.environment" "$WORK_DIR/etc/mark-core-v2/environment"

# Create the package
fakeroot dpkg-deb --root-owner-group --build "$WORK_DIR" "$SCRIPT_DIR/$DEB_FILE"

echo "Package created: $SCRIPT_DIR/$DEB_FILE"
echo "Install with: sudo dpkg -i $DEB_FILE"

# Cleanup
rm -rf "$WORK_DIR"
