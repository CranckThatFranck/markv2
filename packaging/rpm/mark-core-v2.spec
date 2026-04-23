Name: mark-core-v2
Version: 0.1.0
Release: 1%{?dist}
Summary: Mark Core v2 Backend Service
License: Proprietary
URL: https://github.com/CranckThatFranck/markv2
Source0: mark-core-v2-0.1.0.tar.gz

Requires: python3.12

%description
Mark Core v2 is a new backend core that operates as a systemd service.
It provides WebSocket-based agent execution with provider fallback,
credential management, and structured logging.

%prep
%setup -q

%build
python3.12 -m venv .venv
.venv/bin/pip install -U pip setuptools wheel
.venv/bin/pip install -r requirements-backend.txt

%install
mkdir -p %{buildroot}/opt/jarvis/backend
mkdir -p %{buildroot}/etc/systemd/system
mkdir -p %{buildroot}/var/lib/jarvis-mark
mkdir -p %{buildroot}/var/log/jarvis

cp -r . %{buildroot}/opt/jarvis/backend/
cp systemd/mark-core-v2.service %{buildroot}/etc/systemd/system/
cp systemd/mark-core-v2.socket %{buildroot}/etc/systemd/system/

%post
# Create jarvis user if it doesn't exist
id -u jarvis > /dev/null 2>&1 || useradd --system --home /var/lib/jarvis-mark --no-create-home jarvis

# Set ownership
chown -R jarvis:jarvis /opt/jarvis/backend
chown -R jarvis:jarvis /var/lib/jarvis-mark
chown -R jarvis:jarvis /var/log/jarvis

# Reload systemd
systemctl daemon-reload

echo "Mark Core v2 installed successfully!"
echo "To start the service: systemctl start mark-core-v2"
echo "To enable on boot: systemctl enable mark-core-v2"

%preun
systemctl stop mark-core-v2 || true
systemctl disable mark-core-v2 || true

%files
/opt/jarvis/backend
/etc/systemd/system/mark-core-v2.service
/etc/systemd/system/mark-core-v2.socket
%dir /var/lib/jarvis-mark
%dir /var/log/jarvis

%changelog
* Wed Apr 23 2026 CranckThatFranck
- Initial release of Mark Core v2
