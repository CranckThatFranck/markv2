#!/bin/bash
set -e

# Build an RPM package for mark-core-v2
# Usage: ./build-rpm.sh

PACKAGE_NAME="mark-core-v2"
VERSION="0.1.0"
RELEASE="1"
RPM_FILE="${PACKAGE_NAME}-${VERSION}-${RELEASE}.el7.x86_64.rpm"

echo "Building RPM package..."

# Create RPM build directories
WORK_DIR=$(mktemp -d)
mkdir -p "$WORK_DIR/BUILD"
mkdir -p "$WORK_DIR/RPMS"
mkdir -p "$WORK_DIR/SOURCES"
mkdir -p "$WORK_DIR/SPECS"
mkdir -p "$WORK_DIR/SRPMS"

# Copy spec file
cp packaging/rpm/mark-core-v2.spec "$WORK_DIR/SPECS/"

# Create source tarball
tar czf "$WORK_DIR/SOURCES/${PACKAGE_NAME}-${VERSION}.tar.gz" \
    --exclude='.git' \
    --exclude='.venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.mark-runtime' \
    --exclude='packaging' \
    .

# Build RPM
cd "$WORK_DIR"
rpmbuild -ba --define "_topdir $WORK_DIR" "SPECS/${PACKAGE_NAME}.spec"

# Copy result to current directory
cp "$WORK_DIR/RPMS"/*/*.rpm . || cp "$WORK_DIR/RPMS"/*/*.noarch.rpm . 2>/dev/null || true

echo "RPM created: $RPM_FILE (or similar)"
echo "Install with: sudo rpm -i $RPM_FILE"

# Cleanup
rm -rf "$WORK_DIR"
