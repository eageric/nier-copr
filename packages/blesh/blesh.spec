%global debug_package %{nil}
%global upstream_version 0.4.0-devel3

Name:           blesh
Version:        0.4.0~devel3
Release:        1%{?dist}
Summary:        Bash Line Editor - a full-featured line editor written in pure Bash
License:        BSD-3-Clause
URL:            https://github.com/akinomyoga/ble.sh
Source0:        https://github.com/akinomyoga/ble.sh/releases/download/v%{upstream_version}/ble-%{upstream_version}.tar.xz

BuildArch:      noarch
BuildRequires:  tar
BuildRequires:  xz

Requires:       bash
Provides:       ble.sh = %{version}-%{release}

%description
Bash Line Editor (ble.sh) is a command line editor written in pure Bash
which replaces the default GNU Readline with syntax highlighting, enhanced
completion, and vim/emacs editing modes.

To enable ble.sh in interactive shells, source %{_datadir}/blesh/ble.sh
in your ~/.bashrc.

%prep
%setup -q -n ble-%{upstream_version}

%build

%install
mkdir -p %{buildroot}%{_datadir}/blesh
cp -a ble.sh lib keymap contrib %{buildroot}%{_datadir}/blesh/
if [ -d doc ]; then
    mkdir -p %{buildroot}%{_docdir}/blesh
    cp -a doc/* %{buildroot}%{_docdir}/blesh/
fi
if [ -d licenses ]; then
    cp -a licenses %{buildroot}%{_datadir}/blesh/
fi

%files
%{_datadir}/blesh

%changelog
* Sun Oct 25 2026 neir-copr - 0.4.0~devel3-1
- Repackage upstream release 0.4.0-devel3
