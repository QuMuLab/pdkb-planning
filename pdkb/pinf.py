
from .kd45 import *
from .rml import *

class INF:

    @classmethod
    def PDKB2INF(cls, kb):
        return INF(kb.rmls, kb.agents)

    def size(self):
        total = 0
        for ag in self.B:
            if self.B[ag]:
                total += self.B[ag].size() + 1
            total += sum([inf.size() for inf in self.D[ag]])
            if len(self.D[ag]) > 0:
                total += 1

        return total + len(self.props)

    def __init__(self, kb, agents):

        # PDKB2INF from AAMAS paper

        P = set([x for x in kb if x.is_lit()])
        Bs = set([x for x in kb if isinstance(x, Belief)])
        Ds = kb - (P | Bs)

        B = {}
        D = {}

        for ag in agents:
            B[ag] = set([rml.rml for rml in [x for x in Bs if x.agent == ag]])
            D[ag] = set([rml.rml for rml in [x for x in Ds if x.agent == ag]])

        self.props = P

        self.B = {}

        for ag in agents:
            if 0 == len(B[ag]):
                self.B[ag] = False
            else:
                self.B[ag] = INF(B[ag], agents)

        self.D = {}
        for ag in agents:
            self.D[ag] = [INF(set([rml]), agents) for rml in (B[ag] | D[ag])]


    def query(self, rml):

        if rml.is_lit():
            return rml in self.props

        elif isinstance(rml, Belief):
            if self.B[rml.agent]:
                return self.B[rml.agent].query(rml.rml)
            else:
                return False

        else:
            for p in self.D[rml.agent]:
                if p.query(rml.rml):
                    return True

        return False
        
