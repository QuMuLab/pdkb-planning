
from pdkb.rml import neg
from pdkb.kd45 import PDKB
from pdkb.actions import CondEff

def uncertain_changes(condeff, act):
    empty = PDKB(act.depth, act.agents, act.props)
    condn = PDKB(act.depth, act.agents, act.props)

    # Can't have an uncertain firing if there is no condition required
    if len(condeff.condp.rmls) == 0:
        return []

    for rml in condeff.condn.rmls:
        condn.add_rml(rml)

    for rml in condeff.condp.rmls:
        condn.add_rml(neg(rml))

    return [(False, CondEff(empty, condn, neg(condeff.eff), condeff.ma_cond, ('uncertain_firing', 'pos', condeff)))]


COMPILERS_POS = [uncertain_changes]
COMPILERS_NEG = []
