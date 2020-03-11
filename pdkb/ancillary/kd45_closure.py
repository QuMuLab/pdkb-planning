
from pdkb.actions import CondEff
from pdkb.kd45 import kd_closure
from pdkb.rml import neg

def close_literal(condeff, act):
    to_ret = []
    to_close = [condeff.eff]
    seen = set()
    while to_close:
        rml = to_close.pop(0)
        if rml not in seen:
            seen.add(rml)
            to_ret.append((True, CondEff(condeff.condp.copy(), condeff.condn.copy(), rml, condeff.ma_cond, ('closure', 'pos', condeff))))
            to_close.extend(kd_closure(rml))
    return to_ret


def unclose_literal(condeff, act):
    # unclose just follows the above process but uses the contrapositive
    to_ret = []
    to_close = [neg(condeff.eff)]
    seen = set()
    while to_close:
        rml = to_close.pop(0)
        if rml not in seen:
            seen.add(rml)
            to_ret.append((False, CondEff(condeff.condp.copy(), condeff.condn.copy(), neg(rml), condeff.ma_cond, ('unclosure', 'neg', condeff))))
            to_close.extend(kd_closure(rml))
    return to_ret


COMPILERS_POS = [close_literal]
COMPILERS_NEG = [unclose_literal]
