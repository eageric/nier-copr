%global debug_package %{nil}
%global __strip /bin/true
%global _build_id_links none
%global __brp_check_rpaths %{nil}

Name:           nushell
Version:        0.116.1
Release:        1%{?dist}
Summary:        A new type of shell
License:        MIT
URL:            https://www.nushell.sh/
Source0:        https://github.com/nushell/nushell/releases/download/%{version}/nu-%{version}-x86_64-unknown-linux-gnu.tar.gz

ExclusiveArch:  x86_64
BuildRequires:  tar
BuildRequires:  gzip

AutoReqProv:    no
Provides:       nu = %{version}-%{release}

%description
Nushell (or Nu for short) is a modern shell written in Rust that takes a structured, data-oriented approach to pipelines and command-line workflows.

%prep
%setup -q -n nu-%{version}-x86_64-unknown-linux-gnu

%build

%install
mkdir -p %{buildroot}%{_bindir}
install -m 0755 nu %{buildroot}%{_bindir}/nu
for plugin in nu_plugin_*; do
    if [ -f "${plugin}" ]; then
        install -m 0755 "${plugin}" %{buildroot}%{_bindir}/"${plugin}"
    fi
done

%post
if [ ! -f /etc/shells ]; then
    echo "%{_bindir}/nu" > /etc/shells
else
    grep -q "^%{_bindir}/nu$" /etc/shells || echo "%{_bindir}/nu" >> /etc/shells
fi

%postun
if [ "$1" = 0 ] && [ -f /etc/shells ]; then
    sed -i '\#^%{_bindir}/nu$#d' /etc/shells
fi

%files
%license LICENSE
%doc README.txt
%{_bindir}/nu
%{_bindir}/nu_plugin_*

%changelog
* Sun Oct 25 2026 neir-copr - 0.116.1-1
- Repackage upstream release 0.116.1
