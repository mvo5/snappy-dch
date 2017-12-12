#!/bin/bash

set -e

echo "Packages diff of snap $1 and $2"

tmp=$(mktemp -d)
tmp1=${tmp}/1
tmp2=${tmp}/2

trap "rm -rf $tmp" EXIT 

unsquashfs -n -d "$tmp1" "$1" /usr/share/snappy/dpkg.list >/dev/null
unsquashfs -n -d "$tmp2" "$2" /usr/share/snappy/dpkg.list >/dev/null
diff -u0 \
     <(cat $tmp1/usr/share/snappy/dpkg.list | tr -s ' ' | cut -d' ' -f2,3) \
     <(cat $tmp2/usr/share/snappy/dpkg.list | tr -s ' ' | cut -d' ' -f2,3) \
     | egrep -v '^(---|\+\+\+)' | sed 's/^@@.*//g'




