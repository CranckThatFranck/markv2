# Packaging for Mark Core v2

This directory contains scripts and configurations to build Debian (.deb) and RPM (.rpm) packages for Mark Core v2 backend service.

## Debian Package

**Files:**
- `deb/control` - Package metadata and dependencies
- `deb/postinst` - Post-installation script (creates jarvis user, directories)
- `deb/prerm` - Pre-removal script (stops service gracefully)
- `build-deb.sh` - Build script

**Build:**
```bash
cd packaging
bash build-deb.sh
```

**Result:** `mark-core-v2_0.1.0-1_all.deb`

**Install:**
```bash
sudo dpkg -i mark-core-v2_0.1.0-1_all.deb
sudo systemctl start mark-core-v2
```

## RPM Package

**Files:**
- `rpm/mark-core-v2.spec` - RPM spec file
- `build-rpm.sh` - Build script

**Build:**
```bash
cd packaging
bash build-rpm.sh
```

**Result:** `mark-core-v2-0.1.0-1.el7.x86_64.rpm` (or similar)

**Install:**
```bash
sudo rpm -i mark-core-v2-0.1.0-1.el7.x86_64.rpm
sudo systemctl start mark-core-v2
```

## Installation Flow (Both)

1. Package installed to `/opt/jarvis/backend`
2. Systemd unit files copied to `/etc/systemd/system/`
3. `jarvis` system user created (if needed)
4. Directories created: `/var/lib/jarvis-mark`, `/var/log/jarvis`
5. Permissions set correctly for unprivileged execution
6. Service ready to start via `systemctl start/enable mark-core-v2`

## Environment Configuration

After installation, optionally configure environment variables:

```bash
sudo nano /etc/mark-core-v2/environment
```

Supported variables:
- `GOOGLE_API_KEY`
- `GOOGLE_APPLICATION_CREDENTIALS`
- `VERTEXAI_PROJECT`
- `VERTEXAI_LOCATION`

## Uninstallation

```bash
# Debian
sudo dpkg --remove mark-core-v2

# RPM
sudo rpm -e mark-core-v2
```

Both will stop the service and remove systemd units automatically.
