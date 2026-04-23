#!/bin/bash
set -e

# Mark Core v2 systemd uninstallation script
# Run with sudo: sudo ./scripts/uninstall-systemd.sh

SYSTEMD_DIR="/etc/systemd/system"
ENVIRONMENT_CONF="/etc/mark-core-v2"

echo "Uninstalling Mark Core v2 backend..."

# Stop the service if running
echo "Stopping service..."
sudo systemctl stop mark-core-v2 || true

# Disable on boot
echo "Disabling on boot..."
sudo systemctl disable mark-core-v2 || true

# Remove systemd unit files
echo "Removing systemd unit files..."
sudo rm -f "$SYSTEMD_DIR/mark-core-v2.service"
sudo rm -f "$SYSTEMD_DIR/mark-core-v2.socket"

# Reload systemd daemon
echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

echo "Uninstallation complete!"
echo ""
echo "Note: Backend code in /opt/jarvis/backend, state in /var/lib/jarvis-mark, and logs in /var/log/jarvis were NOT removed."
echo "To remove them manually:"
echo "  sudo rm -rf /opt/jarvis/backend"
echo "  sudo rm -rf /var/lib/jarvis-mark"
echo "  sudo rm -rf /var/log/jarvis"
echo "  sudo rm -rf $ENVIRONMENT_CONF"
