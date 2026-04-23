#!/bin/bash
set -e

# Install the minimum host prerequisites for building and running the
# packaged Mark Core v2 backend on Fedora.

if [ "${EUID}" -ne 0 ]; then
    echo "This script must run as root."
    exit 1
fi

dnf install -y \
    python3.12 \
    python3.12-pip \
    python3-tkinter \
    rsync \
    rpm-build

echo "Fedora prerequisites installed."
