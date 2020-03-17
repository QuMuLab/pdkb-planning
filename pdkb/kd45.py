from itertools import product, combinations

from pdkb.kripke import Structure, World
from pdkb.rml import RML, Belief, Possible, Literal, neg
from pdkb.kb import KB
from pdkb.axiom_systems import KD, KD45, KT, S5, AxiomSystem

class PDKB(KB):

    def __init__(self, depth, agents, props):
        self.rmls = set()
        self.depth = depth
        self.agents = agents
        self.props = props
        self._all_rmls = False

    def __iter__(self):
        for rml in self.rmls:
            yield rml

    def reset(self):
        self.rmls = set()
        self._all_rmls = False

    def size(self):
        return sum([(1+rml.get_depth()) for rml in self.rmls])

    def copy(self):
        to_ret = PDKB(self.depth, self.agents, self.props)
        to_ret.rmls = self.rmls.copy()
        return to_ret

    @property
    def all_rmls(self):
        if not self._all_rmls:

            self._all_rmls = set()
            to_add = set(self.props) | set(map(neg, self.props))

            self._all_rmls.update(to_add)

            for i in range(1, self.depth+1):

                prev_added = to_add.copy()
                to_add = set()

                for ag in self.agents:
                    to_add.update(set([Belief(ag, rml) for rml in prev_added] + \
                                      [Possible(ag, rml) for rml in prev_added]))

                self._all_rmls.update(to_add)

        return self._all_rmls

    def add_rml(self, rml):
        assert isinstance(rml, RML)
        self.rmls.add(rml)

    def remove_rml(self, rml):
        assert isinstance(rml, RML)
        self.rmls.remove(rml)

    def expand(self, rmls):
        assert all(isinstance(rml, RML) for rml in rmls)
        to_add = closure_set_of_rmls(rmls)
        self.rmls |= to_add

    def contract(self, rmls):
        assert all(isinstance(rml, RML) for rml in rmls)
        self.rmls -= rmls

    # Remove set of RMLs and anything that implies them.
    def remove(self, rmls):
        assert all(isinstance(rml, RML) for rml in rmls)
        to_remove = set([rml for rml in self.rmls if any (rml.entails_rml(removal) for removal in rmls)])
        self.contract(to_remove)

    # Add a new set of RMLs, removing any RMLs that contradict
    def update(self, rmls):
        assert all(isinstance(rml, RML) for rml in rmls)
        #negated_rmls = negate_set_of_rmls(rmls)
        to_remove = {rml for rml in self.rmls if any(newrml.inconsistent(rml) for newrml in rmls)}
        self.remove(to_remove)
        self.expand(rmls)

    def query(self, rml):
        # pre: knowledge base is closed
        assert isinstance(rml, RML)
        return rml in self.rmls

    def logically_reduce(self):
        to_remove = set()
        for rml in self.rmls:
            to_remove |= (set(kd_closure(rml)) - set([rml]))
        self.rmls -= to_remove

    def logically_close(self):
        new_rmls = set()
        for rml in self.rmls:
            new_rmls |= set(kd_closure(rml))
        self.rmls |= new_rmls

    def close_omniscience(self):
        for rml in self.all_rmls:
            if isinstance(rml, Possible) and neg(rml) not in self.rmls:
                self.add_rml(rml)

    def merge_modalities(self):
        self.rmls = set([rml.merge_modalities() for rml in self.rmls])

    def perspectival_view(self, allow_repeat=False):

        def no_repeats(rml):
            if rml.is_lit():
                return True
            elif rml.agent == rml.rml.agent:
                return False
            else:
                return no_repeats(rml.rml)

        if allow_repeat:
            all_rmls = self.all_rmls
        else:
            all_rmls = list(filter(no_repeats, self.all_rmls))

        CW = set()
        for rml in all_rmls:
            if rml in self.rmls:
                CW.add(Belief(0, rml))
            else:
                CW.add(Possible(0, neg(rml)))
        return CW

    def is_consistent(self):
        # Check if there is anything obviously inconsistent
        for rml in self.rmls:
            if neg(rml) in self.rmls:
                for r in self.rmls:
                    if r == neg(rml):
                        #print "%s <=/=> %s" % (rml, r)
                        pass
                return False

        return True

    def is_omniscient(self):
        for rml in self.all_rmls:
            if (rml not in self.rmls) and (neg(rml) not in self.rmls):
                return False
        return True



    # Debugging tool: restrict kb to only those that share the same literal as rml
    def restrict(self, rml):
        to_remove = []
        for rml2 in self.rmls:
            if not rml.literal == rml2.literal:
                to_remove.append(rml2)
        for item in to_remove:
            self.rmls.remove(item)

    def generate_kripke(self, compressed = False, debug = False):

        if debug:
            prefix = ' '
        else:
            prefix = ''

        self.compressed = compressed

        # Make sure we're closed, reduced, and consistent
        self.logically_close()
        self.merge_modalities()
        assert self.is_consistent(), "Error: Trying to generate the kripke structure of an inconsistent PDKB"

        # Use the closed world assumption for our structure
        CW = self.perspectival_view()

        # Create our structure
        M = Structure(self.agents, True)
        M.root = World({})
        M.add_world(M.root)

        next_worlds = self._generate_kripke(M, CW, prefix)

        for w in next_worlds:
            M.connect(M.root, w, 0)

        return M

    def _generate_kripke(self, M, rmls, DEBUG = ''):

        if DEBUG:
            DEBUG += '  '

        if DEBUG:
            print("\n\n%sGenerating for rmls: %s" % (DEBUG, str(rmls)))

        if 0 == len(rmls):
            return set()

        assert all([not rml.is_lit() for rml in rmls])

        cur_ag = list(rmls)[0].agent

        assert all([cur_ag == rml.agent for rml in rmls])

        all_new_worlds = set()

        # Split the rmls into universal belief (B \phi) and existential (P \phi)
        #  and strip the initial modal operator
        universal_rmls = set([rml.rml for rml in [x for x in rmls if isinstance(x, Belief)]])
        existential_rmls = set([rml.rml for rml in (rmls - universal_rmls)])

        assert all([cur_ag != rml.agent for rml in [x for x in universal_rmls | existential_rmls if not x.is_lit()]])

        # lits will be the literals that must hold in all worlds
        lits = set([x for x in universal_rmls if x.is_lit()])
        props = set([x.get_prop() for x in lits])
        universal_rmls -= lits

        # The existential lits must not disagree with lits
        ex_lits = set([x for x in existential_rmls if x.is_lit()])
        assert all([neg(lit) not in lits for lit in ex_lits]), \
               "Error: Tried an existential literal with conflicting belief. E.g., Bp & P!p"
        existential_rmls -= ex_lits

        # We can safely remove every existential rml that will be covered by
        #  some universal rml
        existential_rmls -= universal_rmls

        for rml in existential_rmls:
            if neg(rml) in universal_rmls:
                print("%s!!Warning!! Inconsistent existential rml: %s" % (DEBUG, str(rml)))

        if DEBUG:
            print("%sAgent: %s" % (DEBUG, str(cur_ag)))
            print("%sLits: %s" % (DEBUG, str(lits)))
            print("%sUniversal RMLs: %s" % (DEBUG, str(universal_rmls)))
            print("%sExistential RMLs: %s" % (DEBUG, str(existential_rmls)))

        if self.compressed or len(props) == len(self.props):
            w = World({lit.get_prop(): (not lit.negated) for lit in lits})
            lit_worlds = set([w])
            M.add_world(w)
            all_new_worlds.add(w)
        else:
            lit_worlds = generate_all_worlds(set(self.props) - props)
            for w in lit_worlds:
                for p in props:
                    w[p] = (p in lits)
                M.add_world(w)
                all_new_worlds.add(w)

        # Handle the universals by default
        next_agents = set([rml.agent for rml in universal_rmls])
        next_worlds = {}
        for next_ag in next_agents:

            new_worlds = self._generate_kripke(M, filter_agent(universal_rmls, next_ag), DEBUG)

            if DEBUG:
                print("%sNew worlds for universal rmls, are: %s" % (DEBUG, str(new_worlds)))

            next_worlds[next_ag] = new_worlds
            for w2 in new_worlds:
                for w1 in all_new_worlds:
                    M.connect(w1, w2, next_ag)

        # Make sure to clone the canonical world when using it!!!
        canon_world = list(lit_worlds)[0]

        # Handle the existentials
        for rml in existential_rmls:
            w = canon_world.clone()
            M.add_world(w)
            all_new_worlds.add(w)
            new_worlds = self._generate_kripke(M, set([rml]) | filter_agent(universal_rmls, rml.agent), DEBUG)

            if DEBUG:
                print("%sNew worlds for existential rml, %s, are: %s" % (DEBUG, str(rml), str(new_worlds)))

            for w2 in new_worlds:
                M.connect(w, w2, rml.agent)

            for ag in next_worlds:
                if ag != rml.agent:
                    for w2 in next_worlds[ag]:
                        M.connect(w, w2, ag)

        if not self.compressed:
            M.make_equiv(all_new_worlds, cur_ag)

        return all_new_worlds

    def relevant_output(self):
        newRMLs = set()
        for rml in self.rmls:
            if not isinstance(rml, Possible):
                newRMLs.add(rml)
            elif (Possible(rml.agent, rml.rml.negate()) not in self.rmls) and \
                   (Belief(rml.agent, rml.rml) not in self.rmls):
                    newRMLs.add(rml)

        return "  " + "\n  ".join(sorted(map(str, newRMLs)))

    def __str__(self):
        return "PDKB:\n%s" % "  " + "\n  ".join(sorted(map(str, self.rmls)))

    def __len__(self):
        return len(self.rmls)



########################
# Helper functions
####################

def closure(rml):
    assert isinstance(rml, RML)

    to_ret = set([rml])
    for closure_function in CLOSURE[AxiomSystem.SYSTEM]:
        next_closure = set()
        for rml in to_ret:
            next_closure |= set(closure_function(rml))
        to_ret |= next_closure

    return to_ret

# Closure of the D axiom: Belief(phi) ==> Diamond(phi)
def kd_closure(rml):
    assert isinstance(rml, RML)

    if isinstance(rml, Literal):
        return [rml]
    elif isinstance(rml, Belief):
        return [Possible(rml.agent, newrml) for newrml in kd_closure(rml.rml)] + \
               [Belief(rml.agent, newrml) for newrml in kd_closure(rml.rml)]
    else:
        return [Possible(rml.agent, newrml) for newrml in kd_closure(rml.rml)]

# Closure of the T axiom: Belief(phi) ==> phi
def kt_closure(rml):
    assert isinstance(rml, RML)

    if isinstance(rml, Belief):
        kt_subclosure = [newrml for newrml in kt_closure(rml.rml)]
        return kt_subclosure + [Belief(rml.agent, newrml) for newrml in kt_subclosure]
    elif isinstance(rml, Possible):
        kt_subclosure = [newrml for newrml in kt_closure(rml.rml)]
        return [Possible(rml.agent, newrml) for newrml in kt_subclosure]
    else:
        return [rml]

def negate_set_of_rmls(rmls):
    assert all(isinstance(rml, RML) for rml in rmls)
    return set([rml.negate() for rml in rmls])

def closure_set_of_rmls(rmls):
    assert all(isinstance(rml, RML) for rml in rmls)
    rmls_closure = set()
    for rml in rmls:
        rmls_closure |= set(closure(rml))
    return rmls_closure

def kd_closure_set_of_rmls(rmls):
    return closure_set_of_rmls(rmls, kd_closure)

def generate_all_worlds(props):
    props = list(props)
    worlds = set()
    for vals in product([True, False], repeat=len(props)):
        v = {props[i]: vals[i] for i in range(len(props))}
        worlds.add(World(v))
    return worlds


def filter_agent(rmls, ag):
    def projectable(rml):
        return not rml.is_lit() and ag == rml.agent
    return set(filter(projectable, rmls))


def project(rmls, ag):
    return set([rml.rml for rml in filter_agent([x for x in rmls if isinstance(x, Belief)], ag)])

CLOSURE = dict([(KD, [kd_closure]),
                (KT, [kt_closure, kd_closure]),
                (KD45, [kd_closure]),
                (S5, [kt_closure, kd_closure])
                ])

if __name__ == '__main__':

    print("\n----\n")

    l1 = Literal('p')
    l2 = Belief(2, Belief(1, l1))
    l3 = Belief(2, neg(Belief(1, neg(l1))))
    l4 = neg(l3)
    print("%s -> %s" % (str(l2), str(list(map(str, kd_closure(l2))))))
    print("%s -> %s" % (str(l3), str(list(map(str, kd_closure(l3))))))

    print("\n----\n")

    kb = PDKB(2, [1,2], list(map(Literal, ['p', 'q'])))
    kb.add_rml(l2)
    print(kb)
    kb.logically_close()
    print(kb)

    print("\n----\n")

    kb.add_rml(l4)
    print(kb)
    kb.logically_close()
    print(kb)
    kb.logically_close()
    print(kb)
    print(kb.is_consistent())

    print("\n----\n")

    kb = PDKB(2, [1,2], list(map(Literal, ['p', 'q'])))
    kb.add_rml(Belief(1, Literal('p')))
    kb.add_rml(Belief(2, Literal('q')))
    kb.add_rml(Belief(1, Belief(2, Literal('q'))))
    print(kb)
    print("\n...projecting on agent 1\n")
    print(project(kb.rmls, 1))

    print("\n----\n")

    kb = PDKB(1, [1], list(map(Literal, ['p', 'q'])))
    kb.add_rml(Belief(1, Literal('p')))
    kb.add_rml(Belief(1, neg(Literal('q'))))
    M = kb.generate_kripke()
    print(M)
    M.generate_dot("graph.dot")

    print("\n----\n")
