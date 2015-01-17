#!/usr/bin/env python

import graphviz as gv

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
        g.graph_attr["size"] = "12,12!"
        g.graph_attr["dpi"] = "100"
        g.node_attr["shape"]= "point"
        g.edge_attr["len"]= "0.3"
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

    def reenumerate(self, deleted, assignments):
        # Reenumerate graph and adjust assignments
        j = self.n_vertices - 1
        self.n_vertices -= len(deleted)
        for i in range(self.n_vertices):
            if i in deleted:
                while j in deleted:
                    j -= 1
                # Replace destination in all edges
                for x in self.edges.values():
                    if j in x:
                        x.remove(j)
                        x.add(i)
                self.edges[i] = self.edges[j]
                del self.edges[j]
                for a, b in assignments.items():
                    if b == j:
                        assignments[a] = i
                j = j - 1
        return assignments

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
        return self.reenumerate(deleted, new_assignments)

    def do_infeasible_removal(self, needle, candidates):
        for i in range(0, needle.n_vertices):
            for j in candidates[i]:
                for x in needle.adjacencies(i):
                    match = False
                    for y in self.adjacencies(j):
                        if y in candidates[x]:
                            match = True
                            break
                    if not match:
                        candidates[i].remove(j)
                        return True
        return False

    def update_candidates(self, needle, candidates):
        while self.do_infeasible_removal(needle, candidates):
            pass

    def search(self, needle, assignments, candidates):
        # If all the vertices in the subgraph are assigned, then we are done.
        i = len(assignments)
        if i == needle.n_vertices:
            return True

        # Copy candidates, since we mutate it in recursive calls and this
        # could mess-up the loop iterator
        tmp = candidates[i][:]
        for j in tmp:
            # This is needed since previous calls could have removed this
            # candidate from set
            if j not in candidates[i]:
                continue
            # Cannot assign same destination vertex to 2 source vertices
            if j not in assignments:
                assignments.append(j)
                # Create a new set of possible assignments, where graph node j
                # is the only possibility for the assignment of subgraph node i.
                new_candidates = [list(l) for l in candidates]
                new_candidates[i] = [j]
                if self.search(needle, assignments, new_candidates):
                  return True
                assignments.pop()
            candidates[i].remove(j)
            self.update_candidates(needle, candidates)

    def get_initial_candidates(self, needle):
        # Prepare initial cadidates (candidates[i] list holds list of possible
        # assignments of needle vertex i to haystack vertices). Initial
        # candidates are selected based on simple criteria:
        #   * candidates, assigned to open nodes, must have degree equal or
        #     greater than source vertex
        #   * candidates, assigned to closed nodes, must have degree equal to
        #     source vertex
        candidates = []
        degs = [self.deg(i) for i in range(self.n_vertices)]
        for i in range(needle.n_vertices):
            candidates.append([])
            for j in range(self.n_vertices):
                deg = needle.deg(i)
                if (i in needle.open and deg <= degs[j]) or deg == degs[j]:
                    candidates[i].append(j)
        return candidates

    def find_isomorphism(self, needle):
        candidates = self.get_initial_candidates(needle)
        self.update_candidates(needle, candidates)
        # Start search. assignments list will hold constructed isomorphism,
        # where needle vertex i is mapped to haystack vertex assignment[i].
        assignments = []
        if self.search(needle, assignments, candidates):
            return assignments
        return None

# Subclass of graph that maintains label to id mapping
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
