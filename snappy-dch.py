#!/usr/bin/python3


import subprocess
import sys
import textwrap
import re

seen = set()

class Commit():
    def __init__(self, raw):
        self._raw = raw
    def author(self):
        return self._find_tag("Author")
    def merge(self):
        return self._find_tag("Merge")
    def body(self):
        body = ""
        for line in self._raw.split("\n"):
            if line.startswith(" "):
                body += line.strip() + "\n"
        return body
    def _find_tag(self, tag):
        for line in self._raw.split("\n"):
            l = line.split(":", 1)
            if l[0] == tag:
                return l[1].strip()
        return ""
    def __str__(self):
        return self._raw
    def commit(self):
        return self._raw.split("\n")[0]
    
    
def commits(lines):
    commit = ""
    for line in lines.split("\n"):
        if line.startswith("commit ") and commit:
            stanza = commit
            commit = ""
            yield Commit(stanza)
        commit += line + "\n"
    yield Commit(commit)

        
def find_closed_bugs(commit):
    if commit.merge() == "":
        return ""
    start, end = commit.merge().split()
    output = subprocess.check_output(
        ["git", "log", "{}..{}".format(start, end)], universal_newlines=True)
    bugs = []
    for change in commits(output):
        seen.add(change.commit())
        for line in change.body().split("\n"):
            if re.search(r'LP[:]*#', line):
                bugs.append(line)
    return "\n".join(bugs)

        
def filter(body):
    out = ""
    closes = []
    seen = set()
    for line in body.split("\n"):
        line = line.strip()
        if "Closes:" in line:
            closes.append(line.split("Closes:")[1])
            continue
        if not line:
            continue
        if line.startswith("Merge branch"):
            continue
        if line.startswith("Merge pull"):
            continue
        if line.startswith("Merge remote"):
            continue
        if line.startswith("Signed-off-by:"):
            continue
        if not ":" in line:
            continue
        # skip duplicates
        if line in seen:
            continue
        seen.add(line)
        out += line + ",".join(closes)
    return out


if __name__ == "__main__":
    since = sys.argv[1]
    output = subprocess.check_output(
        ["git", "log", "{}..".format(since)], universal_newlines=True)

    changes = ""
    for commit in commits(output):
        if commit.commit() in seen:
            continue
        change =  filter(commit.body())
        if change:
            closed_bugs = find_closed_bugs(commit)
            if closed_bugs:
                change += " (" + closed_bugs + ")"
            changes += change + "\n"

    wrapper = textwrap.TextWrapper(initial_indent="    - ", subsequent_indent="      ", width=72)
    for line in changes.split("\n"):
        #print("    - {}".format(line))
        print(("\n".join(wrapper.wrap(line))))
        pass
