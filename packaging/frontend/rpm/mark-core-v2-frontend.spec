Name:           mark-core-v2-frontend
Version:        0.1.0
Release:        1%{?dist}
Summary:        Minimal desktop frontend for Mark Core v2
License:        MIT
BuildArch:      noarch
Requires:       python3.12
Requires:       python3-tkinter
Source0:        %{name}-%{version}.tar.gz

%description
Minimal Linux desktop frontend for the Mark Core v2 backend. The frontend
connects to the existing WebSocket v2 protocol, shows sync_state, history,
provider/model state, and can execute tasks.

%prep
%setup -q

%build

%install
mkdir -p %{buildroot}/opt/jarvis/frontend/src
mkdir -p %{buildroot}/usr/bin
mkdir -p %{buildroot}/usr/share/applications
mkdir -p %{buildroot}/usr/share/icons/hicolor/scalable/apps

cp -a src/frontend %{buildroot}/opt/jarvis/frontend/src/
cp -a requirements-frontend.txt %{buildroot}/opt/jarvis/frontend/
install -m 0755 packaging/frontend/bin/mark-core-v2-frontend %{buildroot}/usr/bin/mark-core-v2-frontend
install -m 0644 packaging/frontend/desktop/mark-core-v2-frontend.desktop \
    %{buildroot}/usr/share/applications/mark-core-v2-frontend.desktop
install -m 0644 packaging/frontend/assets/mark-core-v2-frontend.svg \
    %{buildroot}/usr/share/icons/hicolor/scalable/apps/mark-core-v2-frontend.svg

%post
python3.12 -m venv /opt/jarvis/frontend/.venv
/opt/jarvis/frontend/.venv/bin/pip install --upgrade pip >/dev/null
/opt/jarvis/frontend/.venv/bin/pip install -r /opt/jarvis/frontend/requirements-frontend.txt
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database /usr/share/applications >/dev/null 2>&1 || true
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -q /usr/share/icons/hicolor >/dev/null 2>&1 || true
fi

%preun
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database /usr/share/applications >/dev/null 2>&1 || true
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -q /usr/share/icons/hicolor >/dev/null 2>&1 || true
fi

%files
/opt/jarvis/frontend
/usr/bin/mark-core-v2-frontend
/usr/share/applications/mark-core-v2-frontend.desktop
/usr/share/icons/hicolor/scalable/apps/mark-core-v2-frontend.svg

%changelog
* Thu Apr 23 2026 CranckThatFranck <franck.oliver@outlook.com.br> - 0.1.0-1
- Initial frontend package
