#!/bin/bash

set -e

echo "Files diff"
a=$(unsquashfs -ls "$1"|sort|uniq)
b=$(unsquashfs -ls "$2"|sort|uniq)

diff -u <(echo "$a") <(echo "$b") || true

echo "Content diff"
tmp=$(mktemp -d)
tmp1=${tmp}/1
tmp2=${tmp}/2

trap "rm -rf $tmp" EXIT 

fakeroot unsquashfs -f -d "$tmp1" "$1"
fakeroot unsquashfs -f -d "$tmp2" "$2"
diff --no-dereference -uNr "$tmp1" "$tmp2" || true



