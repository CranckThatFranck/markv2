# Packaging for Mark Core v2

This directory contains the minimum operational packaging for the Mark Core v2 backend service and the frontend v2 desktop client.

The packaged service runs with:

- code in `/opt/jarvis/backend`
- `uvicorn` from `/opt/jarvis/backend/.venv/bin/uvicorn`
- persistent runtime data in `/var/lib/jarvis-mark/estado`
- persistent logs in `/var/log/jarvis`
- environment file in `/etc/mark-core-v2/environment`
- generated artifacts in `packaging/dist/`

## Dist Directory

Predictable artifact location:

- backend `.deb`: `packaging/dist/mark-core-v2_0.1.0-1_all.deb`
- backend `.rpm`: `packaging/dist/mark-core-v2-0.1.0-1.x86_64.rpm`
- frontend `.deb`: `packaging/dist/mark-core-v2-frontend_0.1.0-1_all.deb`
- frontend `.rpm`: `packaging/dist/mark-core-v2-frontend-0.1.0-1.noarch.rpm`

The current build scripts keep these files on disk; they are not deleted at the end of the build.

## Host Prerequisites

Versioned helper scripts:

- `scripts/install-prereqs-ubuntu.sh`
- `scripts/install-prereqs-fedora.sh`

Use them before building or installing on fresh hosts that do not already provide Python 3.12, Tkinter, and the required packaging tools.

## Frontend Packages

The packaged frontend installs:

- code in `/opt/jarvis/frontend`
- virtualenv in `/opt/jarvis/frontend/.venv`
- launcher in `/usr/bin/mark-core-v2-frontend`
- desktop entry in `/usr/share/applications/mark-core-v2-frontend.desktop`
- icon in `/usr/share/icons/hicolor/scalable/apps/mark-core-v2-frontend.svg`

The frontend package does not install or own the backend service. It assumes an already reachable backend, defaulting to `ws://127.0.0.1:8000/ws`, but the host remains configurable inside the app.

### Frontend Debian Package

**Files:**
- `frontend/deb/control`
- `frontend/deb/postinst`
- `frontend/deb/prerm`
- `frontend/bin/mark-core-v2-frontend`
- `frontend/desktop/mark-core-v2-frontend.desktop`
- `frontend/assets/mark-core-v2-frontend.svg`
- `build-frontend-deb.sh`

**Build:**
```bash
cd packaging
bash build-frontend-deb.sh
```

**Result:** `dist/mark-core-v2-frontend_0.1.0-1_all.deb`

**Validated locally:** `dpkg-deb --info packaging/dist/mark-core-v2-frontend_0.1.0-1_all.deb`

**Validated locally:** real install with `sudo dpkg -i packaging/dist/mark-core-v2-frontend_0.1.0-1_all.deb`, launcher execution via `/usr/bin/mark-core-v2-frontend`, and frontend operation from the installed path with `sync_state`, provider/model switch, `google_ai`, `vertex_ai`, and reconnect.

**Install:**
```bash
sudo dpkg -i packaging/dist/mark-core-v2-frontend_0.1.0-1_all.deb
mark-core-v2-frontend
```

### Frontend RPM Package

**Files:**
- `frontend/rpm/mark-core-v2-frontend.spec`
- `build-frontend-rpm.sh`

**Build:**
```bash
cd packaging
bash build-frontend-rpm.sh
```

**Result:** `dist/mark-core-v2-frontend-0.1.0-1.noarch.rpm`

Validated on this Ubuntu host with local `rpmbuild`, so no container or Podman wrapper was needed here.

**Inspect locally:**
```bash
rpm -qpi packaging/dist/mark-core-v2-frontend-0.1.0-1.noarch.rpm
```

**Install on RPM hosts:**
```bash
sudo rpm -i packaging/dist/mark-core-v2-frontend-0.1.0-1.noarch.rpm
mark-core-v2-frontend
```

## Debian Package

**Files:**
- `deb/control` - binary package metadata
- `deb/postinst` - creates `jarvis`, prepares directories, creates `/opt/jarvis/backend/.venv`, installs dependencies, reloads systemd
- `deb/prerm` - stops/disables the service before removal
- `build-deb.sh` - stages the repo and builds the package

**Build:**
```bash
cd packaging
bash build-deb.sh
```

**Result:** `dist/mark-core-v2_0.1.0-1_all.deb`

**Validated locally:** `dpkg-deb --info packaging/dist/mark-core-v2_0.1.0-1_all.deb`

**Validated locally:** real reinstall with `sudo dpkg -i packaging/dist/mark-core-v2_0.1.0-1_all.deb` followed by `systemctl start/status`, `curl /health`, and WebSocket `execute_task`.

**Install:**
```bash
sudo dpkg -i packaging/dist/mark-core-v2_0.1.0-1_all.deb
sudo systemctl start mark-core-v2
```

## RPM Package

**Files:**
- `rpm/mark-core-v2.spec` - RPM spec file
- `build-rpm.sh` - prepares source tarball and calls local `rpmbuild`

**Build:**
```bash
cd packaging
bash build-rpm.sh
```

**Result:** `dist/mark-core-v2-0.1.0-1.x86_64.rpm`

Validated on this Ubuntu host with local `rpmbuild`, so no container or Podman wrapper is required here.

**Install:**
```bash
sudo rpm -i packaging/dist/mark-core-v2-0.1.0-1.x86_64.rpm
sudo systemctl start mark-core-v2
```

## Installation Flow (Both)

1. Package installed to `/opt/jarvis/backend`
2. Systemd unit file copied to `/etc/systemd/system/mark-core-v2.service`
3. Environment file installed at `/etc/mark-core-v2/environment`
4. `jarvis` system user created if needed
5. Directories created: `/var/lib/jarvis-mark/estado` and `/var/log/jarvis`
6. A fresh runtime virtualenv is created in `/opt/jarvis/backend/.venv` on package install
7. Service ready for `systemctl daemon-reload`, `start`, `stop`, `restart`, `status`, and `enable`

## What The Packages Do Not Install Automatically

The Ubuntu `.deb` service and frontend packages still depend on host-level prerequisites:

- Debian/Ubuntu install path needs `python3.12` and `python3.12-venv`
- Debian/Ubuntu frontend path also needs `python3-tk`
- Ubuntu build hosts also need packaging tools such as `fakeroot`, `dpkg-dev`, and `rsync`

If those are missing, use `scripts/install-prereqs-ubuntu.sh` before building or installing on Ubuntu.

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

For the backend service, the file referenced by `GOOGLE_APPLICATION_CREDENTIALS` must be readable by the `jarvis` user when `vertex_ai` is used through `systemd`.

## Uninstallation

```bash
# Debian
sudo dpkg --remove mark-core-v2

# RPM
sudo rpm -e mark-core-v2
```

Both will stop the service and remove systemd units automatically.
