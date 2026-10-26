Name:           onedrive
Version:        2.5.12
Release:        1%{?dist}
Summary:        OneDrive Free Client written in D
License:        GPL-3.0-only
URL:            https://github.com/abraunegg/onedrive
Source0:        https://github.com/abraunegg/onedrive/archive/v%{version}/onedrive-v%{version}.tar.gz

ExclusiveArch:  %{ldc_arches}
BuildRequires:  dbus-devel
BuildRequires:  ldc
BuildRequires:  libcurl-devel
BuildRequires:  libnotify-devel
BuildRequires:  make
BuildRequires:  sqlite-devel
BuildRequires:  systemd
Requires(preun): systemd

%description
Free CLI client for Microsoft OneDrive written in D.

%prep
%setup -q -n onedrive-%{version}
sed -i 's/-o root -g users//g' Makefile.in
sed -i 's/-o root -g root//g' Makefile.in
sed -i "s|std\.c\.|core\.stdc\.|" src/sqlite.d
echo %{version} > version

%build
%configure --enable-notifications
export DFLAGS="%{_d_optflags}"
export PREFIX="%{_prefix}"
make DC=ldmd2 %{?_smp_mflags}

%install
%make_install PREFIX="%{_prefix}"
chmod a-x %{buildroot}/%{_mandir}/man1/%{name}*

%preun
%systemd_user_preun %{name}.service
%systemd_preun %{name}@.service

%files
%{_bindir}/%{name}
%{_userunitdir}/%{name}.service
%{_unitdir}/%{name}@.service
%{_mandir}/man1/%{name}.1.gz
%{_datadir}/icons/hicolor/scalable/places/onedrive.svg
%{_datadir}/icons/hicolor/scalable/apps/onedrive-notifications.svg
%{_docdir}/%{name}
%config(noreplace) %{_sysconfdir}/logrotate.d/onedrive

%changelog
* Sun Oct 25 2026 neir-copr - 2.5.12-1
- Package upstream release 2.5.12
