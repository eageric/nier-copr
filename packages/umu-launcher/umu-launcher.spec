%global debug_package %{nil}
%global __strip /bin/true
%global _build_id_links none
%global __brp_check_rpaths %{nil}
%global __brp_python_bytecompile %{nil}

Name:           umu-launcher
Version:        1.4.4
Release:        1%{?dist}
Summary:        A tool for launching non-Steam games with Proton
License:        GPL-3.0-only
URL:            https://github.com/Open-Wine-Components/umu-launcher
Source0:        https://github.com/Open-Wine-Components/umu-launcher/releases/download/%{version}/umu-launcher-%{version}.fc44.x86_64.rpm

ExclusiveArch:  x86_64
BuildRequires:  cpio
BuildRequires:  rpm

Requires:       python3
Requires:       python3-pyzstd
Requires:       python3-urllib3
Requires:       python3-xlib

%description
Unified Linux Wine Game Launcher. A tool for launching non-Steam games with Proton.

%prep
%setup -q -c -T
rpm2cpio %{SOURCE0} | cpio -idmv

%build

%install
rm -rf usr/lib/.build-id
mkdir -p %{buildroot}/usr
cp -a usr/* %{buildroot}/usr/

%files
%{_bindir}/umu-run
%{_prefix}/lib/python3*/site-packages/umu
%{_prefix}/lib/python3*/site-packages/umu_launcher-*.dist-info
%{_mandir}/man1/umu.1*
%{_mandir}/man5/umu.5*

%changelog
* Sun Oct 25 2026 neir-copr - 1.4.4-1
- Repackage upstream release 1.4.4
