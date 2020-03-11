
from pdkb.kd45 import PDKB
from pdkb.actions import CondEff
from pdkb.rml import Belief, neg, parse_rml

def commonly_known_effect(condeff, agents, depth, props, akprops, posneg, schema, negated=False):

    if (schema is False) or (condeff.depth >= depth):
        return []

    condeffs = []

    if schema is True:
        schema = [[],[]]

    if condeff.ma_cond:
        schema[0].extend(condeff.ma_cond[0])
        schema[1].extend(condeff.ma_cond[1])

    for ag in agents:

        # We can't remove belief we don't have.
        # E.g., (-) p -> B1 q and (-) p -> !B1 q together state that
        #       when p holds, we're not sure if 1 believes q or not.
        #       When introspecting for agent 1, it doesn't make sense
        #       to try and consider (+) B1 p -> !B1 !B1 q as that would
        #       make (+) B1 p -> B1 q, which when projected would be
        #       (+) p -> q. Definitely an undesired result.
        #if ag == condeff.eff.agent and isinstance(condeff.eff, Not) and negated:
        if ag == condeff.eff.agent and negated:
            #print "Warning: Ignoring the commonly known extension for the following conditional effect:\n%s" % str(condeff)
            continue

        condp = PDKB(depth, agents, props)
        condn = PDKB(depth, agents, props)

        for rml in condeff.condp:
            if rml.is_lit() and rml.is_ak(akprops):
                condp.add_rml(rml)
            else:
                condp.add_rml(Belief(ag, rml).merge_modalities())
        for rml in condeff.condn:
            if rml.is_lit() and rml.is_ak(akprops):
                condp.add_rml(neg(rml))
            else:
                condp.add_rml(neg(Belief(ag, rml)).merge_modalities())

        for rmlscheme in schema[0]:
            rml = parse_rml(ag.join(rmlscheme.split('?')))
            if rml.is_lit() and rml.is_ak(akprops):
                condp.add_rml(rml)
            else:
                condp.add_rml(Belief(ag, rml).merge_modalities())
        for rmlscheme in schema[1]:
            rml = parse_rml(ag.join(rmlscheme.split('?')))
            if rml.is_lit() and rml.is_ak(akprops):
                condp.add_rml(rml)
            else:
                condp.add_rml(neg(Belief(ag, rml)).merge_modalities())

        if condeff.eff.is_ak(akprops):
            new_eff = condeff.eff
        else:
            new_eff = Belief(ag, condeff.eff).merge_modalities()

        if negated:
            new_eff = neg(new_eff)

        # Only add the new conditional effect if it is different (this may not
        #  be the case if there was some introspection removed)
        new_cond = CondEff(condp, condn, new_eff, condeff.ma_cond, ('commonly_known', posneg, condeff))
        if new_cond != condeff:
            condeffs.append((True, new_cond))

    return condeffs

def positive_mutual_awareness(condeff, act):
    return commonly_known_effect(condeff, act.agents, act.depth, act.props, act.akprops, 'pos', act.derived_cond)

def negative_mutual_awareness(condeff, act):
    return commonly_known_effect(condeff, act.agents, act.depth, act.props, act.akprops, 'neg', act.derived_cond, True)

COMPILERS_POS = [positive_mutual_awareness]
COMPILERS_NEG = [negative_mutual_awareness]
