%global debug_package %{nil}
%global __strip /bin/true
%global _build_id_links none
%global __brp_check_rpaths %{nil}

Name:           powershell
Version:        7.6.9
Release:        1%{?dist}
Summary:        PowerShell - Cross-platform automation and configuration tool/framework
License:        MIT
URL:            https://github.com/PowerShell/PowerShell
Source0:        https://github.com/PowerShell/PowerShell/releases/download/v%{version}/powershell-%{version}-1.rh.x86_64.rpm

ExclusiveArch:  x86_64
BuildRequires:  cpio
BuildRequires:  rpm

AutoReqProv:    no
Requires:       libicu
Requires:       openssl-libs

%description
PowerShell is an automation and configuration management platform.
It consists of a cross-platform command-line shell and associated scripting language.

%prep
%setup -q -c -T
rpm2cpio %{SOURCE0} | cpio -idmv

%build

%install
mkdir -p %{buildroot}/opt %{buildroot}%{_bindir} %{buildroot}%{_mandir}/man1
cp -a opt/microsoft %{buildroot}/opt/
cp -a usr/bin/pwsh %{buildroot}%{_bindir}/
cp -a usr/share/man/man1/pwsh.1.gz %{buildroot}%{_mandir}/man1/

%post
if [ ! -f /etc/shells ]; then
    echo "%{_bindir}/pwsh" > /etc/shells
else
    grep -q "^%{_bindir}/pwsh$" /etc/shells || echo "%{_bindir}/pwsh" >> /etc/shells
fi

%postun
if [ "$1" = 0 ] && [ -f /etc/shells ]; then
    sed -i '\#^%{_bindir}/pwsh$#d' /etc/shells
fi

%files
/opt/microsoft/powershell
%{_bindir}/pwsh
%{_mandir}/man1/pwsh.1*

%changelog
* Sun Oct 25 2026 neir-copr - 7.6.9-1
- Repackage upstream release 7.6.9

* Sun Oct 25 2026 neir-copr - 7.6.8-1
- Repackage upstream release 7.6.8
