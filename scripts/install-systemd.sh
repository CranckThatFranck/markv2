#!/bin/bash
set -e

# Mark Core v2 systemd installation script
# Run as root: sudo ./scripts/install-systemd.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
BACKEND_DIR="/opt/jarvis/backend"
STATE_DIR="/var/lib/jarvis-mark/estado"
LOG_DIR="/var/log/jarvis"
SYSTEMD_DIR="/etc/systemd/system"
ENVIRONMENT_DIR="/etc/mark-core-v2"

if [ "${EUID}" -ne 0 ]; then
    echo "This script must run as root."
    exit 1
fi

echo "Installing Mark Core v2 backend as systemd service..."

# Create necessary directories
echo "Creating directories..."
mkdir -p "$BACKEND_DIR"
mkdir -p "$STATE_DIR"
mkdir -p "$LOG_DIR"
mkdir -p "$ENVIRONMENT_DIR"

# Create jarvis user if it doesn't exist
if ! id -u jarvis > /dev/null 2>&1; then
    echo "Creating jarvis user..."
    useradd --system --home /var/lib/jarvis-mark --no-create-home jarvis
fi

# Copy backend code
echo "Copying backend code to $BACKEND_DIR..."
rsync -a --delete \
    --exclude='.git' \
    --exclude='.venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.mark-runtime' \
    --exclude='.vscode' \
    "${REPO_ROOT}/" "$BACKEND_DIR/"

echo "Creating virtual environment in $BACKEND_DIR/.venv..."
python3 -m venv "$BACKEND_DIR/.venv"
"$BACKEND_DIR/.venv/bin/pip" install --upgrade pip setuptools wheel
"$BACKEND_DIR/.venv/bin/pip" install -r "$BACKEND_DIR/requirements-backend.txt"

# Set ownership
echo "Setting ownership..."
chown -R jarvis:jarvis /opt/jarvis
chown -R jarvis:jarvis /var/lib/jarvis-mark
chown -R jarvis:jarvis "$LOG_DIR"

# Copy systemd unit files
echo "Installing systemd unit files..."
install -m 0644 "${REPO_ROOT}/systemd/mark-core-v2.service" "$SYSTEMD_DIR/mark-core-v2.service"
install -m 0644 "${REPO_ROOT}/systemd/mark-core-v2.environment" "$ENVIRONMENT_DIR/mark-core-v2.environment"

# Copy environment template if not exists
if [ ! -f "$ENVIRONMENT_DIR/environment" ]; then
    install -m 0640 "${REPO_ROOT}/systemd/mark-core-v2.environment" "$ENVIRONMENT_DIR/environment"
fi

# Reload systemd daemon
echo "Reloading systemd daemon..."
systemctl daemon-reload

echo "Installation complete!"
echo ""
echo "Next steps:"
echo "  1. Review and update environment config: sudo nano $ENVIRONMENT_DIR/environment"
echo "  2. Start the service: sudo systemctl start mark-core-v2"
echo "  3. Enable on boot: sudo systemctl enable mark-core-v2"
echo "  4. Check status: sudo systemctl status mark-core-v2"
echo "  5. View logs: sudo journalctl -u mark-core-v2 -f"
