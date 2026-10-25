%global debug_package %{nil}
%global __strip /bin/true
%global _build_id_links none
%global __brp_check_rpaths %{nil}

Name:           voxtype
Version:        1.1.1
Release:        1%{?dist}
Summary:        Push-to-talk voice-to-text for Linux. Optimized for Wayland, works on X11 too
License:        MIT
URL:            https://voxtype.io
Source0:        https://github.com/peteonrails/voxtype/releases/download/v%{version}/voxtype-%{version}-1.x86_64.rpm

ExclusiveArch:  x86_64
BuildRequires:  cpio
BuildRequires:  rpm

AutoReqProv:    no
Requires:       alsa-lib
Requires:       curl
Requires:       glibc
Requires:       pipewire-alsa

%description
Push-to-talk voice-to-text for Linux. Optimized for Wayland, works on X11 too.

%prep
%setup -q -c -T
rpm2cpio %{SOURCE0} | cpio -idmv

%build

%install
rm -rf usr/lib/.build-id
mkdir -p %{buildroot}/etc %{buildroot}/usr
cp -a etc/voxtype %{buildroot}/etc/
cp -a usr/* %{buildroot}/usr/

%post
if command -v restorecon >/dev/null 2>&1; then
    restorecon %{_bindir}/voxtype 2>/dev/null || true
fi

%files
%config(noreplace) /etc/voxtype/config.toml
%{_bindir}/voxtype
%{_bindir}/voxtype-audio-bridge
%{_bindir}/voxtype-osd
/usr/lib/systemd/user/voxtype.service
/usr/lib/voxtype
%{_datadir}/voxtype
%{_datadir}/bash-completion/completions/voxtype
%{_datadir}/fish/vendor_completions.d/voxtype.fish
%{_datadir}/zsh/site-functions/_voxtype
%{_docdir}/voxtype

%changelog
* Sun Oct 25 2026 neir-copr - 1.1.1-1
- Repackage upstream release 1.1.1
