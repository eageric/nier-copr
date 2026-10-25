%global debug_package %{nil}
%global __strip /bin/true
%global _build_id_links none
%global __brp_check_rpaths %{nil}

Name:           caprine
Version:        2.61.0
Release:        1%{?dist}
Summary:        Elegant Facebook Messenger desktop app
License:        MIT
URL:            https://github.com/sindresorhus/caprine
Source0:        https://github.com/sindresorhus/caprine/releases/download/v%{version}/caprine_%{version}_amd64.deb

ExclusiveArch:  x86_64
BuildRequires:  binutils
BuildRequires:  tar
BuildRequires:  xz
BuildRequires:  zstd

AutoReqProv:    no
Requires:       alsa-lib
Requires:       at-spi2-core
Requires:       gtk3
Requires:       libnotify
Requires:       libsecret
Requires:       libuuid
Requires:       libXScrnSaver
Requires:       libXtst
Requires:       mesa-libgbm
Requires:       nss
Requires:       xdg-utils
Recommends:     libappindicator-gtk3

%description
Caprine is an unofficial and privacy-focused Facebook Messenger app with many useful features.

%prep
%setup -q -c -T
ar x %{SOURCE0}
tar -xf data.tar.*

%build

%install
mkdir -p %{buildroot}/opt %{buildroot}%{_bindir} %{buildroot}%{_datadir}
cp -a opt/Caprine %{buildroot}/opt/
cp -a usr/share/applications %{buildroot}%{_datadir}/
cp -a usr/share/icons %{buildroot}%{_datadir}/
ln -s /opt/Caprine/caprine %{buildroot}%{_bindir}/caprine
chmod 0755 %{buildroot}/opt/Caprine/caprine

%files
%attr(4755, root, root) /opt/Caprine/chrome-sandbox
/opt/Caprine
%{_bindir}/caprine
%{_datadir}/applications/caprine.desktop
%{_datadir}/icons/hicolor/*/apps/caprine.png

%changelog
* Sun Oct 25 2026 neir-copr - 2.61.0-1
- Repackage upstream release 2.61.0
