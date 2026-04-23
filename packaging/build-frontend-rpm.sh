#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
DIST_DIR="${SCRIPT_DIR}/dist"
PACKAGE_NAME="mark-core-v2-frontend"
VERSION="0.1.0"
RELEASE="1"

echo "Building RPM package for ${PACKAGE_NAME}..."
mkdir -p "$DIST_DIR"

if ! command -v rpmbuild >/dev/null 2>&1; then
    echo "rpmbuild not found. Install rpm-build to generate the .rpm artifact."
    exit 1
fi

WORK_DIR="$(mktemp -d)"
SOURCE_ROOT="$WORK_DIR/${PACKAGE_NAME}-${VERSION}"
mkdir -p "$WORK_DIR/BUILD" "$WORK_DIR/RPMS" "$WORK_DIR/SOURCES" "$WORK_DIR/SPECS" "$WORK_DIR/SRPMS"
mkdir -p "$SOURCE_ROOT/src" "$SOURCE_ROOT/packaging/frontend/assets" \
    "$SOURCE_ROOT/packaging/frontend/bin" "$SOURCE_ROOT/packaging/frontend/desktop"

cp "$SCRIPT_DIR/frontend/rpm/mark-core-v2-frontend.spec" "$WORK_DIR/SPECS/"
mkdir -p "$SOURCE_ROOT/src/frontend"
rsync -a \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    "$REPO_ROOT/src/frontend/" "$SOURCE_ROOT/src/frontend/"
cp "$REPO_ROOT/requirements-frontend.txt" "$SOURCE_ROOT/"
cp "$SCRIPT_DIR/frontend/assets/mark-core-v2-frontend.svg" "$SOURCE_ROOT/packaging/frontend/assets/"
cp "$SCRIPT_DIR/frontend/bin/mark-core-v2-frontend" "$SOURCE_ROOT/packaging/frontend/bin/"
cp "$SCRIPT_DIR/frontend/desktop/mark-core-v2-frontend.desktop" "$SOURCE_ROOT/packaging/frontend/desktop/"

tar czf "$WORK_DIR/SOURCES/${PACKAGE_NAME}-${VERSION}.tar.gz" -C "$WORK_DIR" "${PACKAGE_NAME}-${VERSION}"

cd "$WORK_DIR"
rpmbuild -ba --define "_topdir $WORK_DIR" "SPECS/mark-core-v2-frontend.spec"

cp "$WORK_DIR/RPMS"/*/*.rpm "$DIST_DIR/" || cp "$WORK_DIR/RPMS"/*/*.noarch.rpm "$DIST_DIR/" 2>/dev/null || true

RPM_OUTPUT="$(find "$DIST_DIR" -maxdepth 1 -type f -name "${PACKAGE_NAME}-${VERSION}-${RELEASE}*.rpm" | sort | tail -n 1)"
echo "RPM created: ${RPM_OUTPUT:-<not found>}"
echo "Install with: sudo rpm -i ${RPM_OUTPUT:-$DIST_DIR/${PACKAGE_NAME}-${VERSION}-${RELEASE}.noarch.rpm}"

rm -rf "$WORK_DIR"
