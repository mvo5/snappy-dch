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
fakeroot tar cJf snapd_"$2".vendor.tar.xz snapd-"$2"
cp -a snapd_"$2".vendor.tar.xz "$cur"
