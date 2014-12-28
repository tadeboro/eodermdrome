#!/usr/bin/env python3

import graphviz as gv
import sys

def log(msg):
    if debug:
        print(msg)

class Command:
    def __init__(self, input, match, output, replace):
        self.input = input
        self.match = LabeledGraph(match)
        self.output = output
        self.replace = LabeledGraph(replace)
        self.map = self.match.get_mapping(self.replace)
        self.match.open = set(self.map.keys())
        self.replace.open = set(self.map.values())

class Program:
    def __init__(self):
        self.g = Graph("thequickbrownfoxjumpsoverthelazydog")
        self.commands = []

    def add_cmd(self, cmd):
        self.commands.append(cmd)

    def run(self, input):
        self.g.render("exec0")
        counter = 1
        moved = True
        output = ""
        while moved:
            moved = False
            for index, cmd in enumerate(self.commands):
                log("TRY EXEC: " + str(index))
                # Check if command can be executed
                if input[:len(cmd.input)] != cmd.input:
                    continue
                log("INPUT OK. TRY ISO ...")
                map = find_isomorphism (self.g, cmd.match)
                if not map:
                    continue
                # Execute command
                log("EXEC: " + str(index))
                input = input[len(cmd.input):]
                output += cmd.output
                new_map = self.g.remove_internals(cmd.match, map)
                log("NEW_MAP: " + str(new_map))
                log("CMD_MAP: " + str(cmd.map))
                rep_map = {cmd.map[k]: v for k, v in new_map.items()
                               if cmd.map.get(k, None) is not None}
                log("REP_MAP: " + str(rep_map))
                self.g.insert(cmd.replace, rep_map)
                self.g.render("exec" + str(counter))
                # Inform loop that we're still moving
                moved = True
                counter += 1
        return output

class Graph:
    def __init__(self, s):
        self.from_string(s)

    def from_string (self, s):
        self.edges = {}
        self.n_vertices = 0
        if len(s) == 0:
            return {}
        # First vertex is special
        l2i = {s[0]: 0}
        self.edges[0] = set()
        counter = 1
        ix = 0
        for i in range(1, len(s)):
            # Determine vertex id or generate new one
            iy = l2i.get(s[i], -1)
            if iy < 0:
                l2i[s[i]] = counter
                iy = counter
                counter = counter + 1
            # Add connection to graph
            self.add_edge(ix, iy)
            self.add_edge(iy, ix)
            # Move on
            ix = iy
        self.n_vertices = counter
        return l2i

    def add_edge(self, x, y):
        if x not in self.edges:
            self.edges[x] = set()
        self.edges[x].add(y)

    def get_edges(self):
        es = []
        for k, v in self.edges.items():
            es.extend([(k, b) for b in v])
        return es

    def deg(self, n):
        return len(self.edges[n])

    def render(self, fname):
        g = gv.Graph(format = "png", engine = "neato")
        g.graph_attr["overlap"] = "false"
        g.graph_attr["splines"] = "true"
        g.graph_attr["remincross"] = "true"
        for a, b in self.get_edges():
            if a < b:
                g.edge(str(a), str(b))
        g.render(fname + ".gv")

    def adjacencies(self, n):
        return self.edges[n]

    def has_edge(self, a, b):
        return b in self.edges[a]

    def insert(self, r, map):
        # Complete mapping
        n = self.n_vertices
        for i in range(r.n_vertices):
            if i not in map:
                map[i] = n
                n = n + 1
        self.n_vertices = n
        # Insert all connections
        for a, b in r.get_edges():
            self.add_edge(map[a], map[b])

    def remove_internals(self, subgraph, assignments):
        new_assignments = {}
        deleted = set()
        for s, g in enumerate(assignments):
            if s in subgraph.open:
                # Remove all connections between assigned nodes
                for e in subgraph.adjacencies(s):
                    if assignments[e] in self.edges[g]:
                        self.edges[g].remove(assignments[e])
                new_assignments[s] = g
            else:
                # Remove vertex g
                deleted.add(g)
                for x in self.edges[g]:
                    if g in self.edges[x]:
                        self.edges[x].remove(g)
                del self.edges[g]
        # Reenumerate graph and adjust assignments
        log("DELETED: " + str(deleted))
        j = self.n_vertices - 1
        self.n_vertices -= len(deleted)
        for i in range(self.n_vertices):
            log("POSSIBLE REPLACEMENT: " + str(i))
            if i in deleted:
                while j in deleted:
                    j -= 1
                log("DOING REPLACEMENT: " + str(j) + " -> " + str(i))
                # Replace destination in all edges
                for x in self.edges.values():
                    if j in x:
                        x.remove(j)
                        x.add(i)
                self.edges[i] = self.edges[j]
                del self.edges[j]
                for a, b in new_assignments.items():
                    if b == j:
                        new_assignments[a] = i
                j = j - 1
            i = i + 1
        return new_assignments

class LabeledGraph(Graph):
    def __init__(self, s, store_labels = True):
        self.l2i = self.from_string(s)
        self.i2l = {v: k for k, v in self.l2i.items()}

    def render(self, fname):
        g = gv.Graph(format = "png", engine = "neato")
        g.graph_attr["overlap"] = "false"
        g.graph_attr["splines"] = "true"
        g.graph_attr["remincross"] = "true"
        for a, b in self.get_edges():
            if a < b:
                g.edge(self.i2l[a] + "(" + str(a) + ")",
                       self.i2l[b] + "(" + str(b) + ")")
        g.render(fname + ".gv")

    def get_mapping(self, g):
        map = {}
        for k, v in self.l2i.items():
            if k in g.l2i:
                map[v] = g.l2i[k]
        return map

def deep_copy(pas):
    result = []
    for i in range(len(pas)):
        result.append(pas[i][:])
    return result

def do_infeasible_removal(graph, subgraph, possible_assignments):
    for i in range(0, subgraph.n_vertices):
        for j in possible_assignments[i]:
            for x in subgraph.adjacencies(i):
                match = False
                for y in graph.adjacencies(j):
                    if y in possible_assignments[x]:
                        match = True
                        break
                if not match:
                    possible_assignments[i].remove(j)
                    return True
    return False

def update_possible_assignments(graph, subgraph, possible_assignments):
    while do_infeasible_removal(graph, subgraph, possible_assignments):
        pass

def search(graph, subgraph, assignments, possible_assignments):
    log("SEARCH: " + str(assignments))
    update_possible_assignments(graph, subgraph, possible_assignments)
    i = len(assignments)

    # Make sure that every edge between assigned vertices in the subgraph is
    # also an edge in the graph.
    for a, b in subgraph.get_edges():
        if a < i and b < i:
            e1 = assignments[a]
            e2 = assignments[b]
            if not graph.has_edge(e1, e2):
                return False

    # If all the vertices in the subgraph are assigned, then we are done.
    if i == subgraph.n_vertices:
        return True

    tmp_assignments = possible_assignments[i][:]
    for j in tmp_assignments:
        if j not in possible_assignments[i]:
            continue
        if j not in assignments and subgraph.deg(i) <= graph.deg(j):
            assignments.append(j)
            # Create a new set of possible assignments, where graph node j
            # is the only possibility for the assignment of subgraph node i.
            new_possible_assignments = deep_copy(possible_assignments)
            new_possible_assignments[i] = [j]
            if search(graph, subgraph, assignments, new_possible_assignments):
              return True
            assignments.pop()
        possible_assignments[i].remove(j)
        update_possible_assignments(graph, subgraph, possible_assignments)

def find_isomorphism(graph, subgraph):
    # Prepare initial available assignments
    possible_assignments = []
    degs = [graph.deg(i) for i in range(graph.n_vertices)]
    for i in range(subgraph.n_vertices):
        possible_assignments.append([])
        for j in range(graph.n_vertices):
            deg = subgraph.deg(i)
            if (i in subgraph.open and deg <= degs[j]) or deg == degs[j]:
                possible_assignments[i].append(j)
    # Start search
    assignments = []
    if search(graph, subgraph, assignments, possible_assignments):
        return assignments
    return None

def main():
    # Load program
    p = Program()
    p.add_cmd(Command("" , "thequickbrownfoxjumpsoverthelazydog",
                      "" , "abcahijikilihdefgd"))
    p.add_cmd(Command("1", "abcahdhijikil",
                      "" , "abcahijikilihmnonpnqnmd"))
    p.add_cmd(Command("" , "abcahijikilihmnonpnqnmd",
                      "1", "abcahdhijikil"))
    p.add_cmd(Command("0", "a",
                      "" , "a"))

    # Main loop
    out = p.run("110111")
    print(out)

if __name__ == "__main__":
    debug = len(sys.argv) > 1
    main()
