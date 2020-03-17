
from itertools import product, combinations

from pdkb.rml import RML, Belief, Possible, Literal, neg, entails
from pdkb.kb import KB
from pdkb.kd45 import negate_set_of_rmls
from pdkb.axiom_systems import KD, KD45, KT, S5, AxiomSystem

class IndexedPDKB(KB):
    def __init__(self, depth, agents, props):
        self.lookup = {}
        self.depth = depth
        self.agents = agents
        self.props = props

    def __iter__(self):
        for key in self.lookup:
            for rml in self.lookup[key]:
                yield rml

    def reset(self):
        self.lookup = {}

    def size(self):
        total = 0
        for key in self.lookup:
            total += 1 + len(key) + sum([(1+rml.get_depth()) for rml in self.lookup[key]])
        return total

    def copy(self):
        to_ret = IndexedPDKB(self.depth, self.agents, self.props)
        for key in self.lookup:
            to_ret.expand(self.lookup[key])
        return to_ret

    def add_rml(self, rml):
        assert isinstance(rml, RML)
        self.expand(set([rml]))
        
    def remove_rml(self, rml):
        assert isinstance(rml, RML)
        self.contract(set([rml]))

    def expand(self, rmls):
        assert all(isinstance(rml, RML) for rml in rmls)
        for rml in rmls:
            if not self.query(rml):
                index = rml.index
                if index not in self.lookup:
                    self.lookup[index] = set()

                # Remove stuff implied by rml
                to_remove = set()
                for q in self.lookup[index]:
                    if rml.entails_rml(q):
                        to_remove.add(q)
                self.lookup[index] -= to_remove
                self.lookup[index].add(rml)
        
    def contract(self, rmls):
        assert all(isinstance(rml, RML) for rml in rmls)
        for rml in rmls:
            index = rml.index
            if index in self.lookup and rml in self.lookup[index]:
                self.lookup[index].remove(rml)

    def remove(self, rmls):
        assert all(isinstance(rml, RML) for rml in rmls)

        prime_implicates = self.all_prime_implicates(rmls)
        implicates = set()
        for (p, q) in prime_implicates:
            implicates |= sub_lattice(p, q)
        children = lattice_children_set_of_rmls(implicates) - implicates
        self.contract(implicates)
        self.expand(children)
        return children

    def update(self, rmls):
        assert all(isinstance(rml, RML) for rml in rmls)
        # remove any prime implicate that is inconsistent with a new rml
        to_remove = set()
        for rml in rmls:
            if rml.index in self.lookup:
                to_remove |= {oldrml for oldrml in self.lookup[rml.index] if (oldrml.inconsistent(rml))}

        while len(to_remove) > 0:
            children = self.remove(to_remove)
            to_remove = {child for child in children if any(child.inconsistent(rml) for rml in rmls)}
        self.expand(rmls)

    def rmls(self):
        rmls = set()
        for key in self.lookup:
            rmls |= self.lookup[key]
        return rmls

    def query(self, rml):
        index = rml.index
        if index not in self.lookup:
            return False
        for rml2 in self.lookup[index]:
            if rml.proposition == rml2.proposition and rml2.entails_rml(rml):
                return True
        return False

    # Query assuming the axiom T: Box(phi) ==> phi
    def query_t(self, rml):
        return self.query_t_bound(rml, self.depth)

    def query_t_bound(self, rml, depth):
        if self.query(rml):
            return True
        elif depth == 0:
            return False
        else:
            return any(self.query_t_bound(Belief(a, rml), depth - 1) for a in self.agents)

    # Return the set of implicates of rmls from an indexed KB
    def all_prime_implicates(self, rmls):
        implicates = set()
        for q in rmls:
            index = q.index
            if index in self.lookup:
                for p in self.lookup[index]:
                    if p.entails_rml(q):
                        implicates.add((p,q))
        return implicates

    def is_consistent(self):
        # Check if there is anything obviously inconsistent
        for key in self.lookup:
            for rml1 in self.lookup[key]:
                for rml2 in self.lookup[key]:
                    if rml1.inconsistent(rml2):
                        print("inconsistent indexed_kb(%s, %s)" % (rml1, rml2))
                        return False
        return True

    # Debugging tool: restrict kb to only those that share the same literal as rml
    def restrict(self, rml):
        for key in self.lookup:
            to_remove = []
            for rml2 in self.lookup[key]:
                if not rml.literal == rml2.literal:
                    to_remove.append(rml2)
            for item in to_remove:
                self.lookup[key].remove(item)

    def __str__(self):
        return "IndexedPDKB: %s" % str(self.lookup)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

####################
# Helper functions
####################


# Calculate all 'children' of an RML, as defined by its lattice
def lattice_children(rml):
    assert isinstance(rml, RML)

    to_set = set()
    for children_function in CHILDREN[AxiomSystem.SYSTEM]:
        to_set |= children_function(rml)
    return to_set

def kd_lattice_children(rml):
    assert isinstance(rml, RML)

    to_ret = set()
    if isinstance(rml, Belief):
        to_ret = set([Possible(rml.agent, rml.rml)])
        to_ret |= set([Belief(rml.agent, newrml) for newrml in kd_lattice_children(rml.rml)])
    elif isinstance(rml, Possible):
        to_ret |= set([Possible(rml.agent, newrml) for newrml in kd_lattice_children(rml.rml)])

    return to_ret

def kt_lattice_children(rml):
    assert isinstance(rml, RML)

    to_ret = set()
    if isinstance(rml, Belief):
        to_ret = set([Belief(rml.agent, newrml) for newrml in kt_lattice_children(rml.rml)])
        to_ret.add(rml.rml)
    elif isinstance(rml, Possible):
        to_ret = set([Possible(rml.agent, newrml) for newrml in kt_lattice_children(rml.rml)])
    return to_ret

# Calculate all 'children' of a set of RMLs, as defined by its lattice
def lattice_children_set_of_rmls(rmls):

    to_ret = set()
    for rml in rmls:
        to_ret |= lattice_children(rml)

    return to_ret

# Calcuate the set between rmlp and rmlq on the lattice
def sub_lattice(upper, lower):
    assert upper.entails_rml(lower)

    lattice = set([upper])
    children = lattice_children(upper)
    for child in children:
        if child.entails_rml(lower):
            lattice |= sub_lattice(child, lower)
    return lattice

CHILDREN = dict([(KD, [kd_lattice_children]), 
                 (KT, [kt_lattice_children, kd_lattice_children]),
                 (KD45, [kd_lattice_children]),
                 (S5, [kt_lattice_children, kd_lattice_children]),
                 ])

def is_minimal(rmls):

    for p in rmls:
        for q in rmls:
            assert (not p.entails_rml(q)) or p == q, "%s entails %s" % (p, q)

            
    
