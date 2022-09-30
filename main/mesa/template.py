pkgname = "mesa"
pkgver = "22.2.0"
pkgrel = 0
build_style = "meson"
configure_args = [
    "-Dglvnd=false",
    "-Dosmesa=true",
    "-Dgbm=enabled",
    "-Degl=enabled",
    "-Dgles1=enabled",
    "-Dgles2=enabled",
    "-Ddri3=enabled",
    "-Dllvm=enabled",
    "-Dlmsensors=enabled",
    "-Dshared-glapi=enabled",
    "-Dplatforms=x11,wayland",
    "-Dglx=dri",
    "-Dcpp_std=gnu++14",
    "-Ddefault_library=shared",
]
hostmakedepends = [
    "meson", "pkgconf", "flex", "glslang-progs", "bison",
    "wayland-protocols", "wayland-progs", "python-mako"
]
makedepends = [
    "llvm-devel",
    "clang-devel",
    # base driver/platform stuff
    "libdrm-devel",
    # wayland
    "wayland-protocols",
    "wayland-devel",
    # x11
    "libxshmfence-devel", "libxext-devel", "libxxf86vm-devel",
    "libxdamage-devel", "libxfixes-devel", "libx11-devel",
    "libxcb-devel", "libxv-devel", "libxvmc-devel", "libxrandr-devel",
    # misc libs
    "libarchive-devel", "libsensors-devel", "libexpat-devel", "libxml2-devel",
    "ncurses-devel", "libzstd-devel", "zlib-devel", "lua5.4-devel",
    "libffi-devel", "elftoolchain-devel",
    # video accel
    "libva-devel",
    "libvdpau-devel",
]
pkgdesc = "Mesa 3D Graphics Library"
maintainer = "q66 <q66@chimera-linux.org>"
license = "MIT"
url = "https://www.mesa3d.org"
source = f"https://mesa.freedesktop.org/archive/{pkgname}-{pkgver}.tar.xz"
sha256 = "b1f9c8fd08f2cae3adf83355bef4d2398e8025f44947332880f2d0066bdafa8c"
# cba to deal with cross patching nonsense
options = ["!cross"]

_have_llvm = False

# llvmpipe only properly supports a few archs
match self.profile().arch:
    case "x86_64" | "aarch64" | "ppc64le":
        _have_llvm = True
    case _:
        configure_args += ["-Ddraw-use-llvm=false"]

_gallium_drivers = ["swrast"]
_vulkan_drivers = []

if _have_llvm:
    _vulkan_drivers += ["swrast"]

# these are good assumptions on all targets we support for now
_have_nvidia = True
_have_amd = True
_have_hwdec = True
_have_virgl = True

# these change with platforms
_have_intel = False
_have_vmware = False
_have_nine = False
_have_arm = False
_have_opencl = False
_have_vulkan = False
_have_zink = False

match self.profile().arch:
    case "x86_64":
        _have_intel = True
        _have_vmware = True
        _have_nine = True
    case "aarch64":
        _have_arm = True
    case "ppc64le":
        configure_args += ["-Dpower8=true"]
    case "ppc64":
        configure_args += ["-Dpower8=false"]

_have_opencl = _have_amd or _have_intel
_have_vulkan = _have_amd or _have_intel or _have_arm
_have_zink = _have_vulkan

if _have_amd:
    _gallium_drivers += ["r300", "r600", "radeonsi"]
    if _have_vulkan:
        _vulkan_drivers += ["amd"]

if _have_intel:
    _gallium_drivers += ["crocus", "iris", "i915"]
    if _have_vulkan:
        _vulkan_drivers += ["intel"]

if _have_nvidia:
    _gallium_drivers += ["nouveau"]
    if _have_arm:
        _gallium_drivers += ["tegra"]

if _have_arm:
    _gallium_drivers += [
        "kmsro", "v3d", "vc4", "freedreno", "etnaviv", "lima", "panfrost"
    ]
    if _have_vulkan:
        _vulkan_drivers += ["broadcom", "freedreno", "panfrost"]

if _have_virgl:
    _gallium_drivers += ["virgl"]

if _have_nine:
    configure_args += ["-Dgallium-nine=true"]

if _have_vmware:
    _gallium_drivers += ["svga"]
    configure_args += ["-Dgallium-xa=enabled"]
else:
    configure_args += ["-Dgallium-xa=disabled"]

if _have_opencl:
    makedepends += ["libclc"]
    configure_args += ["-Dgallium-opencl=icd"]

if _have_hwdec:
    configure_args += [
        "-Dgallium-vdpau=enabled", "-Dgallium-va=enabled",
        "-Dgallium-xvmc=enabled"
    ]
else:
    configure_args += [
        "-Dgallium-vdpau=disabled", "-Dgallium-va=disabled",
        "-Dgallium-xvmc=disabled"
    ]

if _have_vulkan:
    makedepends += ["vulkan-loader"]
    configure_args += [
        "-Dvulkan-layers=device-select,overlay" + (
            ",intel-nullhw" if _have_intel else ""
        )
    ]

if _have_zink:
    _gallium_drivers += ["zink"]

configure_args += ["-Dgallium-drivers=" + ",".join(_gallium_drivers)]
configure_args += ["-Dvulkan-drivers=" + ",".join(_vulkan_drivers)]

def post_install(self):
    self.install_license("docs/license.rst")

@subpackage("libglapi")
def _glapi(self):
    self.pkgdesc = "Free implementation of the GL API (shared library)"

    return ["usr/lib/libglapi.so.*"]

@subpackage("libgbm")
def _gbm(self):
    self.pkgdesc = "Generic Buffer Management (shared library)"

    return ["usr/lib/libgbm.so.*"]

@subpackage("libgbm-devel")
def _gbm_devel(self):
    self.pkgdesc = "Generic Buffer Management (development files)"

    return [
        "usr/include/gbm.h",
        "usr/lib/libgbm.so",
        "usr/lib/pkgconfig/gbm.pc",
    ]

@subpackage("libosmesa")
def _osmesa(self):
    self.pkgdesc = "Mesa off-screen interface (shared library)"

    return ["usr/lib/libOSMesa.so.*"]

@subpackage("libgles1")
def _gles1(self):
    self.pkgdesc = "Free implementation of OpenGL ES 1.x API (shared library)"

    return ["usr/lib/libGLESv1_CM.so.*"]

@subpackage("libgles2")
def _gles2(self):
    self.pkgdesc = "Free implementation of OpenGL ES 2.x API (shared library)"

    return ["usr/lib/libGLESv2.so.*"]

@subpackage("libegl")
def _gles2(self):
    self.pkgdesc = "Free implementation of the EGL API (shared library)"

    return ["usr/lib/libEGL.so.*"]

@subpackage("libgl")
def _gles2(self):
    self.pkgdesc = "Free implementation of the OpenGL API (shared library)"

    return ["usr/lib/libGL.so.*"]

@subpackage("libxatracker", _have_vmware)
def _xatracker(self):
    self.pkgdesc = "X acceleration library (shared library)"

    return ["usr/lib/libxatracker*.so.*"]

@subpackage("mesa-opencl", _have_opencl)
def _opencl(self):
    self.pkgdesc = "Mesa implementation of OpenCL"

    return [
        "etc/OpenCL",
        "usr/lib/gallium-pipe",
        "usr/lib/libMesaOpenCL.so.*",
    ]

@subpackage("mesa-vaapi", _have_hwdec)
def _dri(self):
    self.pkgdesc = "Mesa VA-API drivers"

    return ["usr/lib/dri/*_drv_video.so"]

@subpackage("mesa-vdpau", _have_hwdec)
def _dri(self):
    self.pkgdesc = "Mesa VA-API drivers"

    return ["usr/lib/vdpau/libvdpau_*"]

@subpackage("mesa-xvmc", _have_hwdec)
def _dri(self):
    self.pkgdesc = "MesaXvMC drivers"

    return ["usr/lib/libXvMC*"]

@subpackage("mesa-dri")
def _dri(self):
    self.pkgdesc = "Mesa graphics drivers"
    self.depends += [f"mesa={pkgver}-r{pkgrel}"]

    return ["usr/lib/dri"]

@subpackage("mesa-vulkan")
def _vulkan(self):
    self.pkgdesc = "Mesa Vulkan drivers"
    self.depends += [f"mesa={pkgver}-r{pkgrel}"]
    self.install_if = [f"mesa-dri={pkgver}-r{pkgrel}", "vulkan-loader"]

    return [
        "usr/bin/mesa-overlay-control.py",
        "usr/lib/libvulkan_*.so",
        "usr/lib/libVkLayer_*.so",
        "usr/share/vulkan/explicit_layer.d/VkLayer_*.json",
        "usr/share/vulkan/implicit_layer.d/VkLayer_*.json",
        "usr/share/vulkan/icd.d/*_icd*.json",
    ]

@subpackage("mesa-devel")
def _devel(self):
    self.depends += ["libgbm-devel"]

    return self.default_devel()
