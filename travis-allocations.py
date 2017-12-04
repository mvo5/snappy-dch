#!/usr/bin/python3

import datetime
import re
import sys


class AllocInfo:
    def __init__(self, system):
        self.system = system
        self._start_times = []
        self.spread_machines = {}
    

def scan(fname):
    alloc_map = {}
    with open(fname) as fp:
        for line in fp:
            # look for alloc matches
            alloc_match = re.search(r"([0-9]{4}-[0-9]{2}-[0-9]{2}) ([0-9]{2}:[0-9]{2}:[0-9]{2}) Allocating linode:([a-z0-9.-]+)...", line)
            if alloc_match:
                start_time = datetime.datetime.strptime("{} {}".format(alloc_match.group(1), alloc_match.group(2)), "%Y-%m-%d %H:%M:%S")
                system = alloc_match.group(3)
                if not system in alloc_map:
                    alloc_map[system] = AllocInfo(system)
                alloc_map[system]._start_times.append(start_time)
            # look for address obtain
            addr_match = re.search(r"([0-9]{4}-[0-9]{2}-[0-9]{2}) ([0-9]{2}:[0-9]{2}:[0-9]{2}) Obtaining address of linode:([a-z0-9.-]+) \((.*)\)...", line)
            if addr_match:
                addr_time = datetime.datetime.strptime("{} {}".format(addr_match.group(1), addr_match.group(2)), "%Y-%m-%d %H:%M:%S")
                system = addr_match.group(3)
                spread_machine = addr_match.group(4)
                ai = alloc_map[system]
                start_time = ai._start_times.pop()
                start_to_addr = addr_time - start_time
                ai.spread_machines[spread_machine] = start_to_addr
    return alloc_map


if __name__ == "__main__":
    alloc_map = scan(sys.argv[1])
    for system, ai in alloc_map.items():
        print("system: {}".format(system))
        for spread_name, start_to_addr in ai.spread_machines.items():
            print(" {}: {}".format(spread_name, start_to_addr))
        missing = len(ai._start_times)
        if missing > 0:
            print(" WARNING: failed to allocate {} machines".format(missing))
        print("")
            
