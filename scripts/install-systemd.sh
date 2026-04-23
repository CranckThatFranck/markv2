#!/bin/bash
set -e

# Mark Core v2 systemd installation script
# Run with sudo: sudo ./scripts/install-systemd.sh

BACKEND_DIR="/opt/jarvis/backend"
STATE_DIR="/var/lib/jarvis-mark"
LOG_DIR="/var/log/jarvis"
SYSTEMD_DIR="/etc/systemd/system"
ENVIRONMENT_CONF="/etc/mark-core-v2"

echo "Installing Mark Core v2 backend as systemd service..."

# Create necessary directories
echo "Creating directories..."
sudo mkdir -p "$BACKEND_DIR"
sudo mkdir -p "$STATE_DIR"
sudo mkdir -p "$LOG_DIR"
mkdir -p "$ENVIRONMENT_CONF"

# Create jarvis user if it doesn't exist
if ! id -u jarvis > /dev/null 2>&1; then
    echo "Creating jarvis user..."
    sudo useradd --system --home /var/lib/jarvis-mark --no-create-home jarvis
fi

# Copy backend code
echo "Copying backend code to $BACKEND_DIR..."
sudo cp -r . "$BACKEND_DIR" 2>/dev/null || echo "Note: Some files may already exist"

# Set ownership
echo "Setting ownership..."
sudo chown -R jarvis:jarvis "$BACKEND_DIR"
sudo chown -R jarvis:jarvis "$STATE_DIR"
sudo chown -R jarvis:jarvis "$LOG_DIR"

# Copy systemd unit files
echo "Installing systemd unit files..."
sudo cp systemd/mark-core-v2.service "$SYSTEMD_DIR/"
sudo cp systemd/mark-core-v2.socket "$SYSTEMD_DIR/"
sudo cp systemd/mark-core-v2.environment "$ENVIRONMENT_CONF/"

# Copy environment template if not exists
if [ ! -f "$ENVIRONMENT_CONF/environment" ]; then
    sudo cp systemd/mark-core-v2.environment "$ENVIRONMENT_CONF/environment"
fi

# Set permissions
sudo chmod 644 "$SYSTEMD_DIR/mark-core-v2.service"
sudo chmod 644 "$SYSTEMD_DIR/mark-core-v2.socket"
sudo chmod 644 "$ENVIRONMENT_CONF/mark-core-v2.environment"
sudo chmod 640 "$ENVIRONMENT_CONF/environment"

# Reload systemd daemon
echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

echo "Installation complete!"
echo ""
echo "Next steps:"
echo "  1. Review and update environment config: sudo nano $ENVIRONMENT_CONF/environment"
echo "  2. Start the service: sudo systemctl start mark-core-v2"
echo "  3. Enable on boot: sudo systemctl enable mark-core-v2"
echo "  4. Check status: sudo systemctl status mark-core-v2"
echo "  5. View logs: sudo journalctl -u mark-core-v2 -f"
