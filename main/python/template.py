pkgname = "python"
_majver = "3.10"
pkgver = f"{_majver}.0"
pkgrel = 0
build_style = "gnu_configure"
configure_args = [
    "--enable-shared", "--enable-ipv6", "--enable-loadable-sqlite-extensions",
    "--with-computed-gotos", "--with-system-ffi", "--with-system-expat",
    "--with-readline=editline", "--without-ensurepip"
]
# bmake has broken cross build (unsupported stuff in PYTHON_FOR_BUILD)
make_cmd = "gmake"
make_check_target = "quicktest"
# disable tests that disagree with our build environment or musl
make_check_args = [
    "EXTRATESTOPTS="
    "-i test_chown_* "
    "-i test_getspnam_exception "
    "-i test_find_library_with_* "
    "-i test_localtime_daylight_*_dst_true "
    "-i test__locale "
    "-i test_c_locale_coercion "
    "-i test_cmd_line "
    "-i test_locale "
    "-i test_os "
    "-i test_re "
    "-i test_readline "
    "-i test_threading "
    "-i test_unicodedata "
]
hostmakedepends = ["pkgconf", "gmake"]
makedepends = [
    "libffi-devel", "openssl-devel", "libbz2-devel", "libedit-devel",
    "zlib-devel", "liblzma-devel", "libexpat-devel", "sqlite-devel",
    "linux-headers"
]
checkdepends = ["ca-certificates", "iana-etc"]
depends = ["ca-certificates"]
pkgdesc = "Python programming language"
maintainer = "q66 <q66@chimera-linux.org>"
license = "Python-2.0"
url = "https://python.org"
source = f"https://python.org/ftp/python/{pkgver}/Python-{pkgver}.tar.xz"
sha256 = "5a99f8e7a6a11a7b98b4e75e0d1303d3832cada5534068f69c7b6222a7b1b002"

pycompile_dirs = [f"usr/lib/python{_majver}"]

if self.cross_build:
    hostmakedepends += ["python"]

def init_configure(self):
    bigend = "yes" if (self.profile().endian == "big") else "no"
    self.configure_args.append("ax_cv_c_float_words_bigendian=" + bigend)

def pre_configure(self):
    self.rm("Modules/_ctypes/darwin", recursive = True)
    self.rm("Modules/_ctypes/libffi_osx", recursive = True)

def do_install(self):
    self.make.invoke(
        ["install", "maninstall"], ["DESTDIR=" + str(self.chroot_destdir)]
    )
    self.install_license("LICENSE")

    self.rm(self.destdir / "usr/bin/2to3", force = True)
    for f in (self.destdir / "usr/bin").glob("idle*"):
        f.unlink()

    lbase = self.destdir / ("usr/lib/python" + _majver)

    self.rm(lbase / "idlelib", recursive = True)
    self.rm(lbase / "tkinter", recursive = True)
    self.rm(lbase / "turtledemo", recursive = True)
    self.rm(lbase / "test", recursive = True)
    self.rm(lbase / "lib2to3/tests", recursive = True)

    (lbase / "turtle.py").unlink(missing_ok = True)

    # remove references to the install(1) wrapper
    def subst_wdir(f):
        import os
        if not f.is_file():
            return
        with open(f) as ifile:
            with open(f.with_suffix(".new"), "w") as ofile:
                for ln in ifile:
                    ln = ln.replace(
                        self.env["CBUILD_STATEDIR"] + "/wrappers", "/usr/bin"
                    )
                    ofile.write(ln)
        os.rename(f.with_suffix(".new"), f)

    for f in lbase.glob("_sysconfigdata_*_*.py"):
        subst_wdir(f)
    for f in lbase.glob("config-*"):
        subst_wdir(f / "Makefile")
        for ff in f.glob("libpython*.a"):
            self.mv(ff, self.destdir / "usr/lib")

    self.install_link("pydoc" + _majver, "usr/bin/pydoc")
    self.install_link("python" + _majver, "usr/bin/python")
    self.install_link("python" + _majver + ".1", "usr/share/man/man1/python.1")

@subpackage("python-devel")
def _devel(self):
    self.depends = [f"{pkgname}={pkgver}-r{pkgrel}"]

    def install():
        import os
        self.take("usr/bin/python*-config")
        self.take("usr/lib/pkgconfig")
        self.take("usr/lib/*.a")
        self.take("usr/include")
        pypath = "usr/include/python" + _majver
        os.makedirs(self.parent.destdir / pypath)
        os.rename(
            self.destdir / pypath / "pyconfig.h",
            self.parent.destdir / pypath / "pyconfig.h"
        )

    return install
