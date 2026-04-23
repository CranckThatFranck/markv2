#!/bin/bash
set -e

# Mark Core v2 systemd uninstallation script
# Run as root: sudo ./scripts/uninstall-systemd.sh

SYSTEMD_DIR="/etc/systemd/system"
ENVIRONMENT_DIR="/etc/mark-core-v2"

if [ "${EUID}" -ne 0 ]; then
    echo "This script must run as root."
    exit 1
fi

echo "Uninstalling Mark Core v2 backend..."

# Stop the service if running
echo "Stopping service..."
systemctl stop mark-core-v2 || true

# Disable on boot
echo "Disabling on boot..."
systemctl disable mark-core-v2 || true

# Remove systemd unit files
echo "Removing systemd unit files..."
rm -f "$SYSTEMD_DIR/mark-core-v2.service"

# Reload systemd daemon
echo "Reloading systemd daemon..."
systemctl daemon-reload

echo "Uninstallation complete!"
echo ""
echo "Note: Backend code in /opt/jarvis/backend, state in /var/lib/jarvis-mark, and logs in /var/log/jarvis were NOT removed."
echo "To remove them manually:"
echo "  sudo rm -rf /opt/jarvis/backend"
echo "  sudo rm -rf /var/lib/jarvis-mark"
echo "  sudo rm -rf /var/log/jarvis"
echo "  sudo rm -rf $ENVIRONMENT_DIR"
