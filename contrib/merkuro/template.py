pkgname = "merkuro"
pkgver = "24.05.0"
pkgrel = 0
build_style = "cmake"
make_check_args = ["-E", "akonadi-sqlite-.*"]
make_check_wrapper = ["wlheadless-run", "--"]
hostmakedepends = [
    "cmake",
    "extra-cmake-modules",
    "gettext",
    "ninja",
    "pkgconf",
]
makedepends = [
    "akonadi-calendar-devel",
    "akonadi-contacts-devel",
    "akonadi-devel",
    "gpgme-devel",
    "kcalendarcore-devel",
    "kcalutils-devel",
    "kconfigwidgets-devel",
    "kcontacts-devel",
    "kcoreaddons-devel",
    "kdbusaddons-devel",
    "ki18n-devel",
    "kiconthemes-devel",
    "kidentitymanagement-devel",
    "kio-devel",
    "kirigami-addons-devel",
    "kirigami-devel",
    "kitemmodels-devel",
    "kmailtransport-devel",
    "kmime-devel",
    "kwindowsystem-devel",
    "kxmlgui-devel",
    "libplasma-devel",
    "mailcommon-devel",
    "messagelib-devel",
    "mimetreeparser-devel",
    "qqc2-desktop-style-devel",
    "qt6-qtdeclarative-devel",
    "qt6-qtsvg-devel",
]
depends = [
    "kdepim-runtime",
    "kirigami-addons",
    "qt6-qt5compat",
    "qt6-qtlocation",
]
checkdepends = ["xwayland-run"] + depends
pkgdesc = "KDE calendar with cloud sync"
maintainer = "Jami Kettunen <jami.kettunen@protonmail.com>"
license = "LGPL-3.0-only AND GPL-3.0-or-later"
url = "https://apps.kde.org/merkuro.calendar"
source = f"$(KDE_SITE)/release-service/{pkgver}/src/merkuro-{pkgver}.tar.xz"
sha256 = "eb632e5a181eafd7f0712531b1accaf755d81c80eb9bf8fedd8c59fd4305cae2"