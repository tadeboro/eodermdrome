#!/usr/bin/env python

from __future__ import print_function
from eodermdrome.parser import parse
from sys import argv, stdin

def usage(prog):
    print("USAGE: " + prog + " FNAME <<< 'INPUT DATA'")

def run(fname, debug):
    p = parse(fname)
    p.render = debug
    p.run("".join(stdin))

def main():
    if len(argv) < 2:
        usage(argv[0])
    else:
        run(argv[1], len(argv) > 2)

if __name__ == "__main__":
    main()
