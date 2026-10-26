%global debug_package %{nil}
%global __strip /bin/true
%global _build_id_links none
%global __brp_check_rpaths %{nil}

Name:           teams-for-linux
Version:        2.27.0
Release:        1%{?dist}
Summary:        Unofficial Microsoft Teams client for Linux using Electron
License:        GPL-3.0-or-later
URL:            https://github.com/IsmaelMartinez/teams-for-linux
Source0:        https://github.com/IsmaelMartinez/teams-for-linux/releases/download/v%{version}/teams-for-linux-%{version}.x86_64.rpm

ExclusiveArch:  x86_64
BuildRequires:  cpio
BuildRequires:  rpm

AutoReqProv:    no
Requires:       alsa-lib
Requires:       at-spi2-core
Requires:       gtk3
Requires:       libnotify
Requires:       libuuid
Requires:       libXScrnSaver
Requires:       libXtst
Requires:       mesa-libgbm
Requires:       nss
Requires:       xdg-utils

%description
Unofficial Microsoft Teams client for Linux using Electron. It uses the Web App
and wraps it as a standalone application using Electron.

%prep
%setup -q -c -T
rpm2cpio %{SOURCE0} | cpio -idmv

%build

%install
mkdir -p %{buildroot}/opt %{buildroot}%{_bindir} %{buildroot}%{_datadir}
cp -a opt/teams-for-linux %{buildroot}/opt/
cp -a usr/share/applications %{buildroot}%{_datadir}/
cp -a usr/share/icons %{buildroot}%{_datadir}/
ln -s /opt/teams-for-linux/teams-for-linux %{buildroot}%{_bindir}/teams-for-linux
chmod 0755 %{buildroot}/opt/teams-for-linux/teams-for-linux

%files
%attr(4755, root, root) /opt/teams-for-linux/chrome-sandbox
/opt/teams-for-linux
%{_bindir}/teams-for-linux
%{_datadir}/applications/teams-for-linux.desktop
%{_datadir}/icons/hicolor/*/apps/teams-for-linux.png

%changelog
* Sun Oct 25 2026 neir-copr - 2.27.0-1
- Repackage upstream release 2.27.0
