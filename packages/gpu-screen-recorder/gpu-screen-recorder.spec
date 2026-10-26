Name:           gpu-screen-recorder
Version:        6.1.5
Release:        1%{?dist}
Summary:        A shadowplay-like screen recorder for Linux
License:        GPL-3.0-only
URL:            https://git.dec05eba.com/gpu-screen-recorder
Source0:        https://dec05eba.com/snapshot/gpu-screen-recorder.git.%{version}.tar.gz

ExclusiveArch:  x86_64 aarch64
BuildRequires:  gcc
BuildRequires:  meson
BuildRequires:  pkgconfig(dbus-1)
BuildRequires:  pkgconfig(egl)
BuildRequires:  pkgconfig(gl)
BuildRequires:  pkgconfig(libavcodec)
BuildRequires:  pkgconfig(libavfilter)
BuildRequires:  pkgconfig(libavformat)
BuildRequires:  pkgconfig(libavutil)
BuildRequires:  pkgconfig(libcap)
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(libpipewire-0.3)
BuildRequires:  pkgconfig(libpulse)
BuildRequires:  pkgconfig(libspa-0.2)
BuildRequires:  pkgconfig(libswresample)
BuildRequires:  pkgconfig(libva)
BuildRequires:  pkgconfig(libva-drm)
BuildRequires:  pkgconfig(vulkan)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-egl)
BuildRequires:  pkgconfig(wayland-scanner)
BuildRequires:  pkgconfig(x11)
BuildRequires:  pkgconfig(xcomposite)
BuildRequires:  pkgconfig(xdamage)
BuildRequires:  pkgconfig(xfixes)
BuildRequires:  pkgconfig(xrandr)
BuildRequires:  systemd-rpm-macros
BuildRequires:  vulkan-headers

Recommends:     libva-intel-media-driver
Recommends:     mesa-va-drivers

%description
A shadowplay-like screen recorder for Linux that records directly on the GPU
with minimal performance impact. Supports X11, Wayland (via KMS or xdg-desktop-portal),
AMD, Intel, and NVIDIA GPUs.

%prep
%setup -q -c

%build
%meson \
    -Dcapabilities=false \
    -Dsystemd=true \
    -Dnvidia_suspend_fix=true \
    -Dportal=true \
    -Dapp_audio=true
%meson_build

%install
%meson_install

%post
%systemd_user_post gpu-screen-recorder.service

%preun
%systemd_user_preun gpu-screen-recorder.service

%files
%license LICENSE
%doc README.md
%{_bindir}/gpu-screen-recorder
%{_bindir}/gsr-cli
%caps(cap_sys_admin=ep) %{_bindir}/gsr-kms-server
%{_includedir}/gsr/plugin.h
%{_prefix}/lib/modprobe.d/gsr-nvidia.conf
%{_userunitdir}/gpu-screen-recorder.service
%{_datadir}/gpu-screen-recorder/
%{_mandir}/man1/gpu-screen-recorder.1*
%{_mandir}/man1/gsr-cli.1*
%{_mandir}/man1/gsr-kms-server.1*

%changelog
* Sun Oct 25 2026 neir-copr - 6.1.5-1
- Package upstream release 6.1.5
