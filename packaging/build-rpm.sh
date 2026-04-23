#!/bin/bash
set -e

# Build an RPM package for mark-core-v2
# Usage: ./build-rpm.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PACKAGE_NAME="mark-core-v2"
VERSION="0.1.0"
RELEASE="1"
RPM_FILE="${PACKAGE_NAME}-${VERSION}-${RELEASE}.el7.x86_64.rpm"

echo "Building RPM package..."

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
cp "$WORK_DIR/RPMS"/*/*.rpm "$SCRIPT_DIR/" || cp "$WORK_DIR/RPMS"/*/*.noarch.rpm "$SCRIPT_DIR/" 2>/dev/null || true

echo "RPM created: $RPM_FILE (or similar)"
echo "Install with: sudo rpm -i $RPM_FILE"

# Cleanup
rm -rf "$WORK_DIR"
