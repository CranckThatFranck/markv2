#!/bin/bash
set -e

# Install the minimum host prerequisites for building and running the
# packaged Mark Core v2 backend on Ubuntu.

if [ "${EUID}" -ne 0 ]; then
    echo "This script must run as root."
    exit 1
fi

apt-get update
apt-get install -y \
    python3.12 \
    python3.12-venv \
    python3-tk \
    rsync \
    fakeroot \
    dpkg-dev

echo "Ubuntu prerequisites installed."
