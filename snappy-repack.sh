#!/bin/sh

set -e

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "need tar and version"
    exit 1
fi

cur="$(pwd)"
tmpdir="$(mktemp -d)"
cleanup() {
    rm -rf "$tmpdir"
}
trap cleanup EXIT

cp -a "$1" "$tmpdir"

cd "$tmpdir"
tar xf "$tmpdir/$(basename "$1")"

new=snapd-"$2"
mv snappy.upstream snapd-"$2"

# full
fakeroot tar cJf snapd_"$2".vendor.tar.xz snapd-"$2"
cp -a snapd_"$2".vendor.tar.xz "$cur"

# and one without vendor tree
fakeroot tar -c --exclude 'snapd-*/vendor/*' -J -f snapd_"$2".no-vendor.tar.xz snapd-"$2"
cp -a snapd_"$2".no-vendor.tar.xz "$cur"

# and one with only vendor tree
fakeroot tar -c -J -f snapd_"$2".only-vendor.tar.xz snapd-"$2"/vendor/
cp -a snapd_"$2".only-vendor.tar.xz "$cur"
