# Packaging for Mark Core v2

This directory contains the minimum operational packaging for the Mark Core v2 backend service.

The packaged service runs with:

- code in `/opt/jarvis/backend`
- `uvicorn` from `/opt/jarvis/backend/.venv/bin/uvicorn`
- persistent runtime data in `/var/lib/jarvis-mark/estado`
- persistent logs in `/var/log/jarvis`
- environment file in `/etc/mark-core-v2/environment`

## Debian Package

**Files:**
- `deb/control` - binary package metadata
- `deb/postinst` - creates `jarvis`, prepares directories, reloads systemd
- `deb/prerm` - stops/disables the service before removal
- `build-deb.sh` - stages the repo, creates `.venv`, and builds the package

**Build:**
```bash
cd packaging
bash build-deb.sh
```

**Result:** `mark-core-v2_0.1.0-1_all.deb`

**Validated locally:** `dpkg-deb --info packaging/mark-core-v2_0.1.0-1_all.deb`

**Install:**
```bash
sudo dpkg -i packaging/mark-core-v2_0.1.0-1_all.deb
sudo systemctl start mark-core-v2
```

## RPM Package

**Files:**
- `rpm/mark-core-v2.spec` - RPM spec file
- `build-rpm.sh` - prepares source tarball and calls `rpmbuild`

**Build:**
```bash
cd packaging
bash build-rpm.sh
```

**Result:** `mark-core-v2-0.1.0-1...rpm` in `packaging/`

If `rpmbuild` is missing, the script exits with a clear message instead of pretending to succeed.

**Install:**
```bash
sudo rpm -i mark-core-v2-0.1.0-1.el7.x86_64.rpm
sudo systemctl start mark-core-v2
```

## Installation Flow (Both)

1. Package installed to `/opt/jarvis/backend`
2. Systemd unit file copied to `/etc/systemd/system/mark-core-v2.service`
3. Environment file installed at `/etc/mark-core-v2/environment`
4. `jarvis` system user created if needed
5. Directories created: `/var/lib/jarvis-mark/estado` and `/var/log/jarvis`
6. Service ready for `systemctl daemon-reload`, `start`, `stop`, `restart`, `status`, and `enable`

## Environment Configuration

After installation, optionally configure environment variables:

```bash
sudo nano /etc/mark-core-v2/environment
```

Supported variables:
- `MARK_STATE_DIR`
- `MARK_LOG_DIR`
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
