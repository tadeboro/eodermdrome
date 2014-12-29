#!/usr/bin/env python

from pyparsing import Suppress, Optional, CharsNotIn, Word, \
        QuotedString, ZeroOrMore, stringEnd
from program import Command, Program
from sys import argv

def parse(path):
    # Comments
    cmt = Suppress(Optional("," + CharsNotIn(",") + ","))

    # Graph characters and construction
    graphchars = "abcdefghijklmnopqrstuvwxyz"
    graph = Word(graphchars)

    # Input and output text
    text = QuotedString("(", endQuoteChar = ")", multiline = True)
    inout = Optional(text, None)

    # Command
    cmd = cmt + inout + cmt + graph + cmt + inout + cmt + graph + cmt
    cmd.setParseAction(lambda x, y, z: Command(*z))

    # Program
    prog = ZeroOrMore(cmd) + stringEnd
    prog.setParseAction(lambda x, y, z: Program(z))

    # Run parser
    return prog.parseFile(path)[0]

# Standalone parser invocation
if __name__ == "__main__":
    if len(argv) < 2:
        print("Usage: " + argv[0] + " FILE")
    else:
        parse(argv[1])
