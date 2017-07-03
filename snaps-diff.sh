#!/bin/bash

set -e

echo "Files diff"
a=$(unsquashfs -ls "$1"|sort|uniq)
b=$(unsquashfs -ls "$2"|sort|uniq)

diff -u <(echo "$a") <(echo "$b") || true

echo "Content diff"
tmp1=$(mktemp -d)
tmp2=$(mktemp -d)

fakeroot unsquashfs -f -d "$tmp1" "$1"
fakeroot unsquashfs -f -d "$tmp2" "$2"
diff --no-dereference -uNr "$tmp1" "$tmp2" || true



