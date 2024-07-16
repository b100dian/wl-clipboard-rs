#
# spec file for package wl-clipboard-rs
#
# Copyright (c) 2024 SUSE LLC
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via https://bugs.opensuse.org/
#


Name:           wl-clipboard-rs
Version:        0.9.0
Release:        0
Summary:        Wayland Clipboard Utility in Rust
License:        Apache-2.0 AND MIT
URL:            https://github.com/YaLTeR/wl-clipboard-rs
Source0:        https://github.com/YaLTeR/wl-clipboard-rs/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1:        vendor.tar.xz
Source2:        cargo_config
BuildRequires:  cargo >= 1.61
BuildRequires:  cargo-packaging
BuildRequires:  cargo-auditable
BuildRequires:  pkgconfig
BuildRequires:  wayland-devel
BuildRequires:  zstd
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-cursor)
BuildRequires:  pkgconfig(wayland-protocols) >= 1.17
BuildRequires:  pkgconfig(wayland-server) >= 1.16
Recommends:     mailcap
Recommends:     xdg-utils
Conflicts:      wl-clipboard

%description
A safe Rust crate for working with the Wayland clipboard.

%define BUILD_DIR "$PWD"/target

%prep
%autosetup -a1 -n %{name}-%{version}/upstream
tar -xJf %{SOURCE1}
mkdir .cargo
cp %{SOURCE2} .cargo/config

%ifarch %arm32
%define SB2_TARGET armv7-unknown-linux-gnueabihf
%endif
%ifarch %arm64
%define SB2_TARGET aarch64-unknown-linux-gnu
%endif
%ifarch %ix86
%define SB2_TARGET i686-unknown-linux-gnu
%endif

%build
export CARGO_HOME="%{BUILD_DIR}/cargo"
export CARGO_BUILD_TARGET=%SB2_TARGET

# When cross-compiling under SB2 rust needs to know what arch to emit
# when nothing is specified on the command line. That usually defaults
# to "whatever rust was built as" but in SB2 rust is accelerated and
# would produce x86 so this is how it knows differently. Not needed
# for native x86 builds
export SB2_RUST_TARGET_TRIPLE=%SB2_TARGET
export RUST_HOST_TARGET=%SB2_TARGET

export RUST_TARGET=%SB2_TARGET
export TARGET=%SB2_TARGET
export HOST=%SB2_TARGET
export SB2_TARGET=%SB2_TARGET

%ifarch %arm32 %arm64
export CROSS_COMPILE=%SB2_TARGET

# This avoids a malloc hang in sb2 gated calls to execvp/dup2/chdir
# during fork/exec. It has no effect outside sb2 so doesn't hurt
# native builds.
export SB2_RUST_EXECVP_SHIM="/usr/bin/env LD_PRELOAD=/usr/lib/libsb2/libsb2.so.1 /usr/bin/env"
export SB2_RUST_USE_REAL_EXECVP=Yes
export SB2_RUST_USE_REAL_FN=Yes
export SB2_RUST_NO_SPAWNVP=Yes
%endif

export CC=gcc
export CXX=g++
export AR="ar"
export NM="gcc-nm"
export RANLIB="gcc-ranlib"
export PKG_CONFIG="pkg-config"

pushd wl-clipboard-rs-tools
CARGO_INCREMENTAL=0 %{cargo_build}

%install
pushd wl-clipboard-rs-tools
CARGO_INCREMENTAL=0 %{cargo_install}

# Removing unnecessary crate related files
find %{buildroot}%{_prefix} -type f \( -name ".crates.toml" -or -name ".crates2.json" \) -delete -print

%files
%{_bindir}/wl-copy
%{_bindir}/wl-paste
%{_bindir}/wl-clip
%license LICENSE-APACHE LICENSE-MIT
%doc README.md CHANGELOG.md doc/index.html

%changelog
