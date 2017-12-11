#!/bin/sh

set -e

PKG=core
FROM_CHANNEL=edge
TO_CHANNEL=beta

for revno in $(snapcraft status core|grep "$FROM_CHANNEL"|tr -s " "|cut -f4 -d' '); do
    echo snapcraft release $PKG $revno ${TO_CHANNEL}
done
