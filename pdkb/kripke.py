from functools import reduce


class Structure:
    def __init__(self, agents, univ_outgoing=False):
        self.agents = [0] + agents
        self.worlds = set()
        self.R = {a: {} for a in self.agents}
        self.root = None
        self.debug_checks = False
        self.assume_universal = univ_outgoing

    def add_world(self, w):
        self.worlds.add(w)
        for ag in self.agents:
            self.R[ag][w] = set()

    def connect(self, w1, w2, ag):
        assert w1 in self.worlds, "Error: World %s doesn't exist" % str(w1)
        assert w2 in self.worlds, "Error: World %s doesn't exist" % str(w2)
        assert ag in self.agents, "Error: Agent %s doesn't exist" % str(ag)

        self.R[ag][w1].add(w2)

    def make_equiv(self, worlds, ag):
        assert worlds <= self.worlds, "Error: Making an equivalence of worlds that don't exist"

        for w1 in worlds:
            for w2 in worlds:
                self.R[ag][w1].add(w2)

    def worlds_accessible(self, nesting = []):
        worlds = set([self.root])
        for ag in nesting:
            worlds = reduce(lambda x,y: x+y, [self.R[ag][w] for w in worlds])
        return worlds

    def assess_rml(self, rml, w = None):
        from .rml import neg, Belief, Possible
        if not w:
            w = self.root
        if rml.is_lit():
            if rml.negated:
                return (neg(rml) in w.valuation) and not w.valuation[neg(rml)]
            else:
                return (rml in w.valuation) and w.valuation[rml]
        elif isinstance(rml, Belief):
            if 0 == len(self.R[rml.agent][w]) and self.assume_universal:
                return False
            return all([self.assess_rml(rml.rml, w2) for w2 in self.R[rml.agent][w]])
        elif isinstance(rml, Possible):
            if 0 == len(self.R[rml.agent][w]) and self.assume_universal:
                return True
            return any([self.assess_rml(rml.rml, w2) for w2 in self.R[rml.agent][w]])
        else:
            assert False, "Error: Unknown rml type to assess: %s" % str(rml)

    def generate_dot(self, fname, compress=False):
        import networkx as nx
        G = nx.DiGraph()

        w2i = {}
        i2w = {}
        i = 1

        def node_label(w,p):
            if w[p]:
                return str(p)
            else:
                return "!%s" % str(p)

        for w in self.worlds:
            w2i[w] = i
            i2w[i] = w
            G.add_node(i, label=','.join([node_label(w, p) for p in w.valuation]))
            i += 1

        for ag in self.R:
            for w1 in self.R[ag]:
                for w2 in self.R[ag][w1]:
                    G.add_edge(w2i[w1], w2i[w2], label=str(ag))

        if compress:
            leaves = [x for x in G.nodes() if 0 == G.out_degree(x)]

            G2 = nx.DiGraph()
            i2h = {}

            for n in leaves:
                nhash = hash(str(i2w[n].valuation))
                i2h[n] = nhash
                if nhash not in G2:
                    G2.add_node(nhash, label = G.node[n]['label'])

            done = set(leaves)
            remaining = set(G.nodes()) - done
            changed = True

            while changed:

                changed = False
                new_nodes = [x for x in remaining if set(G.successors(x)) <= done]

                if len(new_nodes) > 0:

                    for n in new_nodes:
                        hash_str = "%s: %s" % (str(i2w[n].valuation), '/'.join(sorted(map(str, [i2h[s] for s in G.successors(n)]))))
                        #print "Hash string for node %d: <<%s>>" % (n, hash_str)
                        nhash = hash(hash_str)
                        i2h[n] = nhash
                        if nhash not in G2:
                            G2.add_node(nhash, label = G.node[n]['label'])
                            for s in G.successors(n):
                                G2.add_edge(nhash, i2h[s], label = G[n][s]['label'])

                    changed = True
                    done |= set(new_nodes)
                    remaining -= set(new_nodes)

            if 0 != len(remaining):
                print("Warning: Didn't map every node")

            nx.write_dot(G2, fname)

        else:
            nx.write_dot(G, fname)

    def is_serial(self):

        # If we assume that every world lacking an outgoing edge for
        #  a particular agent goes to the universal kripke structure,
        #  then the model is trivially serial
        if self.assume_universal:
            return True

        for ag in self.R:
            for w in self.worlds:
                if w not in self.R[ag] or 0 == len(self.R[ag][w]):
                    print("Failed serial check because of agent %s and world %s" % (str(ag), str(w)))
                    return False
        return True

    def is_euclidean(self):
        for ag in self.R:
            for w1 in self.R[ag]:
                for w2 in self.R[ag][w1]:
                    if w2 not in self.R[ag]:
                        if self.debug_checks:
                            print("Failed euclidean check because of agent %s, source %s, and missing target source %s" % (str(ag), str(w1), str(w2)))
                        return False
                    for w3 in self.R[ag][w1]:
                        if w3 not in self.R[ag][w2]:
                            if self.debug_checks:
                                print("Failed euclidean check because of agent %s, source %s, successor w2 %s, and successor w3 %s" % (str(ag), str(w1), str(w2), str(w3)))
                            return False
        return True

    def is_transitive(self):
        for ag in self.R:
            for w1 in self.R[ag]:
                for w2 in self.R[ag][w1]:
                    if w2 not in self.R[ag]:
                        continue
                    for w3 in self.R[ag][w2]:
                        if w3 not in self.R[ag][w1]:
                            if self.debug_checks:
                                print("Failed transitive check because of agent %s, w1 %s, w2 %s, and w3 %s" % (str(ag), str(w1), str(w2), str(w3)))
                            return False
        return True

    def is_reflexive(self):
        for ag in self.R:
            for w1 in self.R[ag]:
                if w1 not in self.R[ag][w1]:
                    if self.debug_checks:
                        print("Failed reflexive check because of agent %s and world %s" % (str(ag), str(w1)))
                    return False
        return True

    def is_symmetric(self):
        for ag in self.R:
            for w1 in self.R[ag]:
                for w2 in self.R[ag][w1]:
                    if w1 not in self.R[ag][w2]:
                        if self.debug_checks:
                            print("Failed symmetric check because of agent %s, w1 %s, and w2 %s" % (str(ag), str(w1), str(w2)))
                        return False
        return True

    def is_kd45(self):
        return self.is_serial() and self.is_transitive() and self.is_euclidean()

    
    def get_stats(self):
        toRet = str(self)
        properties = []
        if self.is_serial():
            properties.append('serial')
        if self.is_reflexive():
            properties.append('reflexive')
        if self.is_symmetric():
            properties.append('symmetric')
        if self.is_transitive():
            properties.append('transitive')
        if self.is_euclidean():
            properties.append('euclidean')

        if properties:
            toRet += "Properties: %s\n\n" % ', '.join(properties)
        else:
            toRet += "Properties: None\n\n"

        toRet += "KD45n: %s\n\n" % str(self.is_kd45())

        return toRet

    def __str__(self):
        return "<Kripke Structure (%d worlds)>" % len(self.worlds)
    
    def __repr__(self):
        return str(self)
    
    def dump(self):

        print(self.get_stats())

        w2i = {}
        i2w = {}
        i = 1

        print("Worlds:")
        for w in self.worlds:
            w2i[w] = i
            i2w[i] = w
            print(" %d: %s" % (i, str(w)))
            i += 1
        
        print()
        
        for ag in self.R:
            print("Accessability for agent %s:" % str(ag))
            for w1 in self.R[ag]:
                for w2 in self.R[ag][w1]:
                    print("%d --> %d" % (w2i[w1], w2i[w2]))

        return toRet


class World:
    def __init__(self, val):
        self.valuation = val

    def __getitem__(self, key):
        return self.valuation[key]

    def __setitem__(self, key, val):
        assert val in [True, False]
        self.valuation[key] = val

    def __str__(self):
        return str(self.valuation)

    def __repr__(self):
        return str(self)

    def clone(self):
        return World({k: self[k] for k in self.valuation})
