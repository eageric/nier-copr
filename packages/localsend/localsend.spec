%global debug_package %{nil}
%global __strip /bin/true
%global _build_id_links none
%global __brp_check_rpaths %{nil}

Name:           localsend
Version:        1.18.2
Release:        1%{?dist}
Summary:        An open-source cross-platform alternative to AirDrop
License:        Apache-2.0
URL:            https://localsend.org/
Source0:        https://github.com/localsend/localsend/releases/download/v%{version}/LocalSend-%{version}-linux-x86-64.deb

ExclusiveArch:  x86_64
BuildRequires:  binutils
BuildRequires:  tar
BuildRequires:  xz
BuildRequires:  zstd

AutoReqProv:    no
Requires:       gtk3
Requires:       (libayatana-appindicator-gtk3 or libappindicator-gtk3)
Requires:       xdg-user-dirs

%description
LocalSend is a free, open-source app that allows you to securely share files and messages with nearby devices over your local network without needing an internet connection.

%prep
%setup -q -c -T
ar x %{SOURCE0}
tar -xf data.tar.*

%build

%install
mkdir -p %{buildroot}/opt %{buildroot}%{_bindir} %{buildroot}%{_datadir}
cp -a opt/localsend_app %{buildroot}/opt/
cp -a usr/share/applications %{buildroot}%{_datadir}/
cp -a usr/share/icons %{buildroot}%{_datadir}/
ln -s /opt/localsend_app/localsend_app %{buildroot}%{_bindir}/localsend_app
ln -s /opt/localsend_app/localsend_app %{buildroot}%{_bindir}/localsend
chmod 0755 %{buildroot}/opt/localsend_app/localsend_app

%files
/opt/localsend_app
%{_bindir}/localsend_app
%{_bindir}/localsend
%{_datadir}/applications/localsend_app.desktop
%{_datadir}/icons/hicolor/*/apps/localsend_app.png

%changelog
* Sun Oct 25 2026 neir-copr - 1.18.2-1
- Repackage upstream release 1.18.2
