#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
DIST_DIR="${SCRIPT_DIR}/dist"
WORK_DIR="$(mktemp -d)"
PACKAGE_NAME="mark-core-v2-frontend"
VERSION="0.1.0"
RELEASE="1"
DEB_FILE="${PACKAGE_NAME}_${VERSION}-${RELEASE}_all.deb"

echo "Building Debian package for ${PACKAGE_NAME}..."
echo "Working directory: $WORK_DIR"
mkdir -p "$DIST_DIR"

DEBIAN_DIR="$WORK_DIR/DEBIAN"
APP_DIR="$WORK_DIR/opt/jarvis/frontend"
mkdir -p "$DEBIAN_DIR"
mkdir -p "$APP_DIR/src"
mkdir -p "$WORK_DIR/usr/bin"
mkdir -p "$WORK_DIR/usr/share/applications"
mkdir -p "$WORK_DIR/usr/share/icons/hicolor/scalable/apps"

cp "$SCRIPT_DIR/frontend/deb/control" "$DEBIAN_DIR/control"
cp "$SCRIPT_DIR/frontend/deb/postinst" "$DEBIAN_DIR/postinst"
cp "$SCRIPT_DIR/frontend/deb/prerm" "$DEBIAN_DIR/prerm"
chmod 755 "$DEBIAN_DIR/postinst" "$DEBIAN_DIR/prerm"

mkdir -p "$APP_DIR/src/frontend"
rsync -a \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    "$REPO_ROOT/src/frontend/" "$APP_DIR/src/frontend/"
cp "$REPO_ROOT/requirements-frontend.txt" "$APP_DIR/"
cp "$SCRIPT_DIR/frontend/bin/mark-core-v2-frontend" "$WORK_DIR/usr/bin/mark-core-v2-frontend"
cp "$SCRIPT_DIR/frontend/desktop/mark-core-v2-frontend.desktop" \
    "$WORK_DIR/usr/share/applications/mark-core-v2-frontend.desktop"
cp "$SCRIPT_DIR/frontend/assets/mark-core-v2-frontend.svg" \
    "$WORK_DIR/usr/share/icons/hicolor/scalable/apps/mark-core-v2-frontend.svg"
chmod 755 "$WORK_DIR/usr/bin/mark-core-v2-frontend"

if command -v desktop-file-validate >/dev/null 2>&1; then
    desktop-file-validate "$WORK_DIR/usr/share/applications/mark-core-v2-frontend.desktop"
fi

fakeroot dpkg-deb --root-owner-group --build "$WORK_DIR" "$DIST_DIR/$DEB_FILE"

echo "Package created: $DIST_DIR/$DEB_FILE"
echo "Install with: sudo dpkg -i $DIST_DIR/$DEB_FILE"

rm -rf "$WORK_DIR"
