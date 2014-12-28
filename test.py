import graphviz as gv
import sys

def log(msg):
    if debug:
        print(msg)

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

    def render(self, fname):
        g = gv.Graph(format = "png", engine = "dot")
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

    def remove_internals(self, assignments):
        new_assignments = {}
        destinations = frozenset(assignments)
        deleted = set()
        for s, g in enumerate(assignments):
            if self.edges[g] <= destinations:
                # Remove vertex g
                deleted.add(g)
                for x in self.edges[g]:
                    if g in self.edges[x]:
                        self.edges[x].remove(g)
                del self.edges[g]
            else:
                # Remove all connections between assigned nodes
                self.edges[g] -= destinations
                new_assignments[s] = g
        # Reenumerate graph and adjust assignments
        log("DELETED: " + str(deleted))
        j = self.n_vertices - 1
        self.n_vertices -= len(deleted)
        for i in range(self.n_vertices):
            log("POSSIBLE REPLACEMENT: " + str(i))
            if i in deleted:
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
        g = gv.Graph(format = "png", engine = "dot")
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
                for y in range(0, graph.n_vertices):
                    if y in possible_assignments[x] and graph.has_edge(j,y):
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
        if j not in assignments:
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
    assignments = []
    possible_assignments = []
    for i in range(subgraph.n_vertices):
        possible_assignments.append(list(range(graph.n_vertices)))
    if search(graph, subgraph, assignments, possible_assignments):
        return assignments
    return None

def main():
    # Test 1
    g = Graph("abcdedfgfbhihd")
    s = LabeledGraph("abcdaec")
    r = LabeledGraph("acbcd")

    g.render("xxx0")
    s2r_map = s.get_mapping(r)
    log(s2r_map)
    mapping = find_isomorphism(g, s)
    log(mapping)
    new_mapping = g.remove_internals(mapping)
    log(new_mapping)
    log(g.n_vertices)
    rep_mapping = {s2r_map[k]: v for k, v in new_mapping.items() if s2r_map.get(k, None)}
    log(rep_mapping)
    g.insert(r, rep_mapping)
    g.render("xxx1")

    # Test 2
    #g = Graph("abcade")
    #s = LabeledGraph("dabca")
    #r = LabeledGraph("deabca")

    #g.render("test0")
    #s2r_map = s.get_mapping(r)
    #log(s2r_map)
    #for i in range(1, 6):
    #    mapping = find_isomorphism(g, s)
    #    log(mapping)
    #    new_mapping = g.remove_internals(mapping)
    #    log(new_mapping)
    #    log(g.n_vertices)
    #    rep_mapping = {s2r_map[k]: v for k, v in new_mapping.items()}
    #    log(rep_mapping)
    #    g.insert(r, rep_mapping)
    #    g.render("test" + str(i))

if __name__ == "__main__":
    debug = len(sys.argv) > 1
    main()
