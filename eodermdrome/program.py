#!/usr/bin/env python

from __future__ import print_function
from eodermdrome.graph import Graph, LabeledGraph

class Command:
    def __init__(self, input, match, output, replace):
        # Copy parameters
        self.input = input
        self.matchs = match
        self.output = output
        self.replaces = replace
        # Build graphs and maps
        self.match = LabeledGraph(match)
        self.replace = LabeledGraph(replace)
        self.map = self.match.get_mapping(self.replace)
        self.match.open = set(self.map.keys())
        self.replace.open = set(self.map.values())

    def __str__(self):
        res = ""
        if self.input:
            res += "(" + self.input + ") "
        res += self.matchs + " "
        if self.output:
            res += "(" + self.output + ") "
        res += self.replaces
        return res

class Program:
    def __init__(self, commands = [], render = False):
        self.g = Graph("thequickbrownfoxjumpsoverthelazydog")
        self.commands = commands
        self.render = render

    def __str__(self):
        return "\n".join(map(str, self.commands))

    def add_cmd(self, cmd):
        self.commands.append(cmd)

    def exec_cmd(self, cmd, input, cntr):
        # Check if command can be executed
        if cmd.input and input[:len(cmd.input)] != cmd.input:
            return (False, input)
        map = self.g.find_isomorphism (cmd.match)
        if not map:
            return (False, input)
        # Execute command
        if cmd.input:
            input = input[len(cmd.input):]
        if cmd.output:
            print(cmd.output, end = "", flush = True)
        new_map = self.g.remove_internals(cmd.match, map)
        rep_map = {cmd.map[k]: v for k, v in new_map.items()
                       if cmd.map.get(k, None) is not None}
        self.g.insert(cmd.replace, rep_map)
        if self.render:
            self.g.render("exec" + str(cntr))
        return (True, input)

    def run(self, input):
        counter = 1
        # Execute commands until no action is possible
        runf = True
        while runf:
            runf = False
            for cmd in self.commands:
                f, input = self.exec_cmd(cmd, input, counter)
                runf = runf or f
                counter += 1 if f else 0
