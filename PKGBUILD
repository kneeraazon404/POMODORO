# Maintainer: kneeraazon <kneeraazon@gmail.com>
pkgname=pomodoro
pkgver=2.0.0
pkgrel=1
pkgdesc="POMODORO – focus timer with goal and task tracking"
arch=('any')
url="https://github.com/kneeraazon/POMODORO"
license=('MIT')
depends=('python' 'noto-fonts')
makedepends=('python-pip')
optdepends=('python-pillow: app window icon')
source=()
sha256sums=()

_srcdir="$(readlink -f "$(dirname "$BASH_SOURCE[0]")")"

build() {
    pip install --quiet --target "$srcdir/vendor" customtkinter pillow
}

package() {
    install -d "$pkgdir/opt/$pkgname"
    cp -r "$_srcdir/app"     "$pkgdir/opt/$pkgname/"
    cp    "$_srcdir/main.py" "$pkgdir/opt/$pkgname/"
    cp -r "$_srcdir/assets"  "$pkgdir/opt/$pkgname/"
    cp -r "$srcdir/vendor"   "$pkgdir/opt/$pkgname/"

    install -d "$pkgdir/usr/bin"
    cat > "$pkgdir/usr/bin/$pkgname" <<'EOF'
#!/usr/bin/env bash
export PYTHONPATH="/opt/pomodoro/vendor:$PYTHONPATH"
exec python /opt/pomodoro/main.py "$@"
EOF
    chmod 755 "$pkgdir/usr/bin/$pkgname"

    install -Dm644 "$_srcdir/assets/pomodoro.desktop" \
        "$pkgdir/usr/share/applications/$pkgname.desktop"

    install -Dm644 "$_srcdir/assets/icon.png" \
        "$pkgdir/usr/share/pixmaps/$pkgname.png"
}
