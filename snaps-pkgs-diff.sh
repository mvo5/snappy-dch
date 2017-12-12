#!/bin/bash

set -e

echo "Packages diff of snap $1 and $2"

tmp=$(mktemp -d)
tmp1=${tmp}/a
tmp2=${tmp}/b

#trap "rm -rf $tmp" EXIT 

unsquashfs -n -d "$tmp1" "$1" /usr/share/snappy/dpkg.list >/dev/null
unsquashfs -n -d "$tmp2" "$2" /usr/share/snappy/dpkg.list >/dev/null
diff -u0 \
     <(cat $tmp1/usr/share/snappy/dpkg.list | tr -s ' ' | cut -d' ' -f2,3) \
     <(cat $tmp2/usr/share/snappy/dpkg.list | tr -s ' ' | cut -d' ' -f2,3) \
     | egrep -v '^(---|\+\+\+)' | sed 's/^@@.*//g'


echo "Package changelogs diff"

rm -rf $tmp/{a,b}
unsquashfs -n -d "$tmp1" "$1" /usr/share/doc/*/changelog.Debian.gz >/dev/null
unsquashfs -n -d "$tmp2" "$2" /usr/share/doc/*/changelog.Debian.gz >/dev/null
find $tmp -type l -name "changelog.Debian.gz" | xargs rm -f
find $tmp -type f -name "changelog.Debian.gz" | xargs gzip -d
(cd $tmp ; diff -u0 -N -r "a" "b" | grep -v "^-")
