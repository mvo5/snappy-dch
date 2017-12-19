#!/usr/bin/python3

import re
import subprocess


PKG="core"
TO_CHANNEL="edge"

output="""Rev.    Uploaded              Arch     Version                           Channels
3703    2017-12-11T08:38:43Z  arm64    16-2.30~rc3                       edge*, beta*
3702    2017-12-11T08:37:19Z  armhf    16-2.30~rc3                       edge*, beta*
3701    2017-12-11T08:30:30Z  ppc64el  16-2.30~rc3                       edge*, beta*
3700    2017-12-11T08:29:24Z  amd64    16-2.30~rc3                       edge*, beta*
3699    2017-12-11T08:29:20Z  i386     16-2.30~rc3                       edge*, beta*
3698    2017-12-11T08:29:21Z  s390x    16-2.30~rc3                       edge*, beta*
3697    2017-12-11T04:35:52Z  s390x    16-2.30~rc2+git469.69b980d        edge
3696    2017-12-11T04:30:30Z  armhf    16-2.30~rc2+git469.69b980d        edge
3695    2017-12-11T04:29:27Z  arm64    16-2.30~rc2+git469.69b980d        edge
3694    2017-12-11T04:24:32Z  amd64    16-2.30~rc2+git469.69b980d        edge
3693    2017-12-11T04:23:30Z  ppc64el  16-2.30~rc2+git469.69b980d        edge
3692    2017-12-11T04:23:27Z  i386     16-2.30~rc2+git469.69b980d        edge
3691    2017-12-10T04:34:17Z  arm64    16-2.30~rc2+git469.69b980d        edge
3690    2017-12-10T04:30:28Z  armhf    16-2.30~rc2+git469.69b980d        edge
3689    2017-12-10T04:25:27Z  ppc64el  16-2.30~rc2+git469.69b980d        edge
3688    2017-12-10T04:25:29Z  i386     16-2.30~rc2+git469.69b980d        edge
3687    2017-12-10T04:23:20Z  amd64    16-2.30~rc2+git469.69b980d        edge
3686    2017-12-10T04:22:18Z  s390x    16-2.30~rc2+git469.69b980d        edge
3685    2017-12-09T04:31:49Z  i386     16-2.30~rc2+git469.69b980d        edge
3684    2017-12-09T04:30:33Z  s390x    16-2.30~rc2+git469.69b980d        edge
3683    2017-12-09T04:30:35Z  armhf    16-2.30~rc2+git469.69b980d        edge
3682    2017-12-09T04:30:35Z  arm64    16-2.30~rc2+git469.69b980d        edge
3681    2017-12-09T04:24:20Z  ppc64el  16-2.30~rc2+git469.69b980d        edge
3680    2017-12-09T04:23:45Z  amd64    16-2.30~rc2+git469.69b980d        edge
3679    2017-12-08T04:32:19Z  s390x    16-2.30~rc2+git469.69b980d        edge
3678    2017-12-08T04:30:28Z  arm64    16-2.30~rc2+git469.69b980d        edge
3677    2017-12-08T04:28:18Z  armhf    16-2.30~rc2+git469.69b980d        edge
3676    2017-12-08T04:24:24Z  ppc64el  16-2.30~rc2+git469.69b980d        edge
3675    2017-12-08T04:23:19Z  i386     16-2.30~rc2+git469.69b980d        edge
3674    2017-12-08T04:22:19Z  amd64    16-2.30~rc2+git469.69b980d        edge
3673    2017-12-07T14:56:20Z  arm64    16-2.30~rc2+git469.69b980d        edge
3672    2017-12-07T14:54:19Z  armhf    16-2.30~rc2+git469.69b980d        edge
3671    2017-12-07T14:48:50Z  ppc64el  16-2.30~rc2+git469.69b980d        edge
3670    2017-12-07T14:46:20Z  s390x    16-2.30~rc2+git469.69b980d        edge
3669    2017-12-07T14:45:28Z  amd64    16-2.30~rc2+git469.69b980d        edge
3668    2017-12-07T14:44:18Z  i386     16-2.30~rc2+git469.69b980d        edge
3667    2017-12-07T04:35:51Z  s390x    16-2.30~rc2+git469.69b980d        edge
3666    2017-12-07T04:29:30Z  arm64    16-2.30~rc2+git469.69b980d        edge"""

def find_arches_and_move_forward(li):
    arches = set()
    # skip header
    for line in li[:]:
        arch = re.split('\s+', line)[2]
        if arch in arches:
            return arches
        arches.add(arch)
        li.pop(0)


def revert_previous_edge_versions(li, arches):
    processed_arches=set()
    for line in li[:]:
        arch = re.split('\s+', line)[2]
        rev = re.split('\s+', line)[0]
        if arch in processed_arches:
            continue
        print("# {}".format(re.sub(r' +', ' ', line)))
        print("snapcraft release {} {} {}".format(PKG, rev, TO_CHANNEL))
        print("")
        processed_arches.add(arch)
        if len(arches) == len(processed_arches):
            return
        li.pop(0)
    raise Exception("cannot find all arches in revert_previous_edge_versions")
        
        
if __name__ == "__main__":
    output = subprocess.check_output(["snapcraft", "list-revisions", PKG], universal_newlines=True)
    arches=set()
    li = output.split("\n")
    # skip header
    li.pop(0)
    arches = find_arches_and_move_forward(li)
    revert_previous_edge_versions(li, arches)
