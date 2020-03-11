
from pdkb.actions import CondEff
from pdkb.rml import neg

def negated_changes(condeff, act):
    return [(False, CondEff(condeff.condp.copy(),
                            condeff.condn.copy(),
                            neg(condeff.eff),
                            condeff.ma_cond,
                            ('negation-removal', 'pos', condeff)))]

COMPILERS_POS = [negated_changes]
COMPILERS_NEG = []
