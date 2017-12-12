#!/usr/bin/python
#
# no python3 on lillypilly

import glob
import gzip
import os
import re
import shutil
import subprocess
import sys
import tempfile

import pprint

class tmpdir:
    def __enter__(self):
        self.tmp = tempfile.mkdtemp()
        return self.tmp
    def __exit__(self, *args):
        shutil.rmtree(self.tmp)


class Change:
    def __init__(self, old_version, new_version, diff, changelogs):
        self.old_version = old_version
        self.new_version = new_version
        self.pkg_changes = diff
        self.changelogs = changelogs
    def __repr__(self):
        return "<Change old=%s new=%s>" % (self.old_version, self.new_version)


def unsquashfs(tmp, snap, data):
    with open(os.devnull, "w") as devnull:
        subprocess.check_call(
            ["unsquashfs", "-f", "-d", tmp, snap, data], stdout=devnull)
    

def core_version(snap):
    version = "unknown"
    with tmpdir() as tmp:
        unsquashfs(tmp, snap, "/usr/lib/snapd/info")
        with open(os.path.join(tmp, "usr/lib/snapd/info")) as fp:
            for line in fp.readlines():
                line = line.strip()
                if line.startswith("VERSION="):
                    version = line.split("=")[1]
    return version


def core_debs(snap):
    pkgs = {}
    with tmpdir() as tmp:
        unsquashfs(tmp, snap, "/usr/share/snappy/dpkg.list")
        with open(os.path.join(tmp, "usr/share/snappy/dpkg.list")) as fp:
            for line in fp.readlines():
                line = line.strip()
                if not line.startswith("ii"):
                    continue
                l = re.split(r'\s+',line)
                name = l[1]
                ver = l[2]
                pkgs[name] = ver
    return pkgs


def debs_delta(debs_a, debs_b):
    diff = {}
    # in a but not in b
    for name in debs_a:
        if not name in debs_b:
            diff[name] = (debs_a[name], "")
    # in b but not in a
    for name in debs_b:
        if not name in debs_a:
            diff[name] = ("", debs_b[name])
    # in both
    for name in debs_a:
        if name in debs_b and debs_a[name] != debs_b[name]:
            diff[name] = (debs_a[name], debs_b[name])
    return diff


def changelog_until(changelog_path, old_version):
    lines = []
    with gzip.open(changelog_path) as changelog:
        for line in changelog:
            line = line.rstrip()
            # FIXME: make this smater
            if "("+old_version+")" in line:
                break
            lines.append(line)
    return "\n".join(lines)
    

def deb_changelogs(new_snap, pkg_changes):
    changelogs = {}
    with tmpdir() as tmp:
        unsquashfs(tmp, new_snap, "/usr/share/doc/*/changelog*")
        for name in pkg_changes:
            old_ver, new_ver = pkg_changes[name]
            for chglogname in ["changelog.Debian.gz", "changelog.gz"]:
                changelog_path = os.path.join(
                    tmp,"usr/share/doc",name, chglogname)
                if not os.path.exists(changelog_path) or os.path.islink(changelog_path):
                    continue
                if not name in changelogs:
                    changelogs[name] = []
                changelogs[name] = changelog_until(changelog_path, old_ver)
                break
    return changelogs
        
        
def snap_changes(old_snap, new_snap):
    old_ver = core_version(old_snap)
    new_ver= core_version(new_snap)
    diff = debs_delta(core_debs(old_snap), core_debs(new_snap))
    changelogs = deb_changelogs(new_snap, diff)
    return Change(old_ver, new_ver, diff, changelogs)


def all_snap_changes(archive_dir):
    all_changes = {}
    snaps=sorted(glob.glob(archive_dir+"/*.snap"))
    for i in range(len(snaps)-1):
        a = snaps[i]
        b = snaps[i+1]
        all_changes[(a,b)] = snap_changes(a,b)
    return all_changes


def render_text(changes):
    for chg in changes.values():
        print("old: %s" % chg.old_version)
        print("new: %s" % chg.new_version)
        print("\n")
        print("pkg_changes:")
        for deb, ver in sorted(chg.pkg_changes.items()):
            print(" %s: %s -> %s" % (deb, ver[0], ver[1]))
        print("\n")
        print("changelogs:")
        for name, changelog in chg.changelogs.items():
            print("%s" % changelog)
            print("\n\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Need directory with snap packages as first arg")
        sys.exit(1)
    
    archive_dir = sys.argv[1]
    all_changes = all_snap_changes(archive_dir)

    render_text(all_changes)
