#!/bin/bash
set -e

# Build an RPM package for mark-core-v2
# Usage: ./build-rpm.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
DIST_DIR="${SCRIPT_DIR}/dist"
PACKAGE_NAME="mark-core-v2"
VERSION="0.1.0"
RELEASE="1"

echo "Building RPM package..."
mkdir -p "$DIST_DIR"

if ! command -v rpmbuild >/dev/null 2>&1; then
    echo "rpmbuild not found. Install rpm-build to generate the .rpm artifact."
    exit 1
fi

# Create RPM build directories
WORK_DIR=$(mktemp -d)
mkdir -p "$WORK_DIR/BUILD"
mkdir -p "$WORK_DIR/RPMS"
mkdir -p "$WORK_DIR/SOURCES"
mkdir -p "$WORK_DIR/SPECS"
mkdir -p "$WORK_DIR/SRPMS"

# Copy spec file
cp "$SCRIPT_DIR/rpm/mark-core-v2.spec" "$WORK_DIR/SPECS/"

# Create source tarball
SOURCE_DIR="$WORK_DIR/${PACKAGE_NAME}-${VERSION}"
mkdir -p "$SOURCE_DIR"
rsync -a --exclude='.git' \
    --exclude='.venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.mark-runtime' \
    --exclude='packaging' \
    --exclude='.vscode' \
    "$REPO_ROOT/" "$SOURCE_DIR/"
tar czf "$WORK_DIR/SOURCES/${PACKAGE_NAME}-${VERSION}.tar.gz" -C "$WORK_DIR" "${PACKAGE_NAME}-${VERSION}"

# Build RPM
cd "$WORK_DIR"
rpmbuild -ba --define "_topdir $WORK_DIR" "SPECS/mark-core-v2.spec"

# Copy result to current directory
cp "$WORK_DIR/RPMS"/*/*.rpm "$DIST_DIR/" || cp "$WORK_DIR/RPMS"/*/*.noarch.rpm "$DIST_DIR/" 2>/dev/null || true

RPM_OUTPUT="$(find "$DIST_DIR" -maxdepth 1 -type f -name "${PACKAGE_NAME}-${VERSION}-${RELEASE}*.rpm" | sort | tail -n 1)"
echo "RPM created: ${RPM_OUTPUT:-<not found>}"
echo "Install with: sudo rpm -i ${RPM_OUTPUT:-$DIST_DIR/${PACKAGE_NAME}-${VERSION}-${RELEASE}.x86_64.rpm}"

# Cleanup
rm -rf "$WORK_DIR"
