#!/usr/bin/python


import subprocess
import sys
import textwrap

class Commit():
    def __init__(self, raw):
        self._raw = raw
    def author(self):
        return self._find_tag("Author")
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

    
def commits(lines):
    commit = ""
    for line in output.split("\n"):
        if line.startswith("commit ") and commit:
            stanza = commit
            commit = ""
            yield Commit(stanza)
        commit += line + "\n"

        
def filter(body):
    out = ""
    closes = []
    for line in body.split("\n"):
        line = line.strip()
        if "Closes:" in line:
            print(line, line.split("Closes:")[1])
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
        if not ":" in line:
            continue
        out += line + ",".join(closes) + "\n"
    return out


if __name__ == "__main__":
    since = sys.argv[1]
    output = subprocess.check_output(
        ["git", "log", "--merges", "{}..".format(since)])

    changes = ""
    for commit in commits(output):
        change =  filter(commit.body())
        if change:
            changes += change 

    wrapper = textwrap.TextWrapper(initial_indent="    - ", subsequent_indent="      ", width=72)
    for line in changes.split("\n"):
        #print("    - {}".format(line))
        print("\n".join(wrapper.wrap(line)))
