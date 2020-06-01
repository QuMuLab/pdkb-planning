
import os, time

from pdkb.test.utils import read_file, write_file, run_command, parse_output_ipc

from pdkb.rml import parse_rml, Literal
from pdkb.kd45 import PDKB, project
from pdkb.actions import Action
from pdkb.pddl.grounder import GroundProblem
import pdkb


def parse_ma_cond(dcond):
    pos_der_cond = []
    neg_der_cond = []
    if isinstance(dcond, pdkb.pddl.formula.And):
        prims = dcond.args
    elif isinstance(dcond, pdkb.pddl.formula.Primitive):
        prims = [dcond]
    else:
        assert False, "Bad type? %s" % str(type(dcond))

    for prim in prims:
        if isinstance(prim, pdkb.pddl.formula.Not):
            neg_der_cond.append(str(prim2rml(prim)).replace('$agent$', '?'))
        else:
            pos_der_cond.append(str(prim2rml(prim)).replace('$agent$', '?'))

    return (pos_der_cond, neg_der_cond)


def prim2rml(prim, parse = True):
    rml = ''
    if isinstance(prim, pdkb.pddl.formula.Not):
        rml += str(prim.args[0].agent_list)
        rml += {True: '!', False: ''}[prim.args[0].negated_rml]
        rml += prim.args[0].dump()[1:-1].replace(' ', '_')
    else:
        rml += str(prim.agent_list)
        rml += {True: '!', False: ''}[prim.negated_rml]
        rml += prim.dump()[1:-1].replace(' ', '_')
    if parse:
        rml = parse_rml(rml)
    return rml


def convert_action(action, depth, agents, props, akprops):

    if str(action.dcond) == '(always)':
        act = Action(action.name, depth, agents, props, akprops, True)

    elif str(action.dcond) == '(never)':
        act = Action(action.name, depth, agents, props, akprops, False)

    elif action.dcond:
        act = Action(action.name, depth, agents, props, akprops, parse_ma_cond(action.dcond))

    else:
        assert False, "Error for action %s. You need to specify the type of derived condition ('always', 'never', or 'custom')." % action.name


    assert isinstance(action.precondition, pdkb.pddl.formula.And)
    for pre in action.precondition.args:
        act.add_pre(prim2rml(pre), negate=isinstance(pre, pdkb.pddl.formula.Not))

    def get_arg_list(form, objtype):
        if isinstance(form, objtype):
            return form.args
        else:
            return [form]

    #print dir(action)
    #['dcond', 'dump', 'effect', 'export', 'is_equal', 'name', 'observe', 'parameters', 'precondition']
    #['agent_list', 'args', 'dump', 'enforce_normalize', 'export', 'is_equal', 'name', 'normalize', 'predicate', 'to_ground']

    for nondet_eff in get_arg_list(action.effect, pdkb.pddl.formula.Oneof):

        act.new_nondet_effect()

        for eff in get_arg_list(nondet_eff, pdkb.pddl.formula.And):

            condp = PDKB(depth, agents, props)
            condn = PDKB(depth, agents, props)

            if isinstance(eff, pdkb.pddl.formula.When):
                for l in get_arg_list(eff.condition, pdkb.pddl.formula.And):
                    if isinstance(l, pdkb.pddl.formula.Not):
                        condn.add_rml(prim2rml(l))
                    else:
                        condp.add_rml(prim2rml(l))

                lit = prim2rml(eff.result)

                if isinstance(eff.result, pdkb.pddl.formula.Not):
                    act.add_neg_effect(condp, condn, lit)
                else:
                    act.add_pos_effect(condp, condn, lit)

            else:
                if isinstance(eff, pdkb.pddl.formula.Not):
                    act.add_neg_effect(condp, condn, prim2rml(eff))
                else:
                    act.add_pos_effect(condp, condn, prim2rml(eff))
    return act


def parse_problem(prob, domain):

    assert prob.task in list(PROBLEM_TYPES.keys()), "Error: Bad problem type: %s" % prob.task

    return PROBLEM_TYPES[prob.task](prob, domain)


def read_pdkbddl_file(fname):

    lines = read_file(fname)

    found = True
    count = 0
    while found:
        count += 1
        if count > 100:
            assert False, "Error: Already attempted at least 100 imports. Did you recursively import something?"

        found = False
        include_indices = []

        for i in range(len(lines)):
            if lines[i].find('{include') == 0:
                include_indices.append(i)
                found = True

        for index in reversed(include_indices):
            new_file = os.path.join(os.path.split(fname)[0], lines[index].split(':')[1][:-1])
            lines = lines[:index] + read_pdkbddl_file(new_file) + lines[index+1:]

    # Strip out the comments and empty lines
    lines = [x for x in lines if x != '']
    lines = [x for x in lines if x[0] != ';']
    lines = [x.split(';')[0] for x in lines]

    # Convert the [] and <> notation to nested B's
    def replace_modal(left, right, sym, line):
        new_line = ''
        bracket_count = 0
        negate = ''
        for c in line:

            if negate != '' and c != left:
                new_line += '!'
                negate = ''

            if c == left:
                new_line += "(%s%s{" % (negate, sym)
                bracket_count += 1
                negate = ''
            elif c == right:
                new_line += '}'
            elif c == '!':
                negate = '!'
            else:
                new_line += c

            if c == ')':
                while bracket_count:
                    new_line += ')'
                    bracket_count -= 1

        return new_line

    def replace_belief(line):
        return replace_modal('[', ']', 'B', line)
    def replace_possible(line):
        return replace_modal('<', '>', 'P', line)
    def replace_alwaysknow(line):
        assert '%' not in line, "Error: Custom character % must be avoided"
        assert '&' not in line, "Error: Custom character & must be avoided"
        return replace_modal('&', '%', 'AK', line.replace('{AK}','&%'))

    for func in [replace_belief, replace_possible, replace_alwaysknow]:
        lines = list(map(func, lines))

    return lines


def parse_pdkbddl(pdkbddl_file):

    lines = read_pdkbddl_file(pdkbddl_file)

    prob_index = -1
    for i in range(len(lines)):
        if '(define (problem' in lines[i]:
            assert -1 == prob_index
            prob_index = i
    assert prob_index != -1, "Error: No problem type defined"

    prob = GroundProblem(lines[:prob_index], lines[prob_index:])

    fluents = [x for x in prob.fluents if not x.always_known]
    akfluents = [x for x in prob.fluents if x.always_known]

    props = [parse_rml('_'.join(str(p)[1:-1].split())) for p in fluents]
    akprops = [parse_rml('_'.join(str(p)[1:-1].split())) for p in akfluents]

    domain = Domain(prob.agents, props, akprops,
                    [convert_action(a, prob.depth, prob.agents, props, akprops) for a in prob.operators],
                    prob.depth, prob.types, prob.domain_name)

    return parse_problem(prob, domain)


class Problem(object):

    def __init__(self):
        self.domain = None

    def parse_parts(self, prob):
        self.parse_projection(prob)
        self.parse_init(prob)
        self.parse_goal(prob)

    def parse_projection(self, prob):
        assert 'projection' in dir(prob)
        self.agent_projection = list(reversed(prob.projection))

    def parse_init(self, prob):

        self.init = PDKB(self.domain.depth, self.domain.agents, self.domain.props)

        assume_closed = False
        if prob.init_type == 'complete':
            assume_closed = True

        assert isinstance(prob.init, pdkb.pddl.formula.And)

        for prim in prob.init.args:
            init_rmls = [prim2rml(prim, False)]
            for t in prob.types:
                going = True
                while going:
                    new_init_rmls = []
                    going = False
                    for old_init_rml in init_rmls:
                        if "$%s$" % t not in old_init_rml:
                            new_init_rmls.append(old_init_rml)
                        else:
                            going = True
                            for v in prob.type_to_obj[t]:
                                # Only do a single split so we can reuse the same variable type
                                lside = old_init_rml[:old_init_rml.index("$%s$" % t)]
                                rside = old_init_rml[old_init_rml.index("$%s$" % t)+len("$%s$" % t):]
                                new_init_rmls.append(lside + v + rside)
                    init_rmls = new_init_rmls
            for rml_line in init_rmls:
                self.init.add_rml(parse_rml(rml_line))

        # Close the initial state
        self.init.logically_close()

        if assume_closed:
            self.init.close_omniscience()

        assert self.init.is_consistent(), "Error: Inconsistent initial state"


    def parse_goal(self, prob):

        self.goal = PDKB(self.domain.depth, self.domain.agents, self.domain.props)

        assert isinstance(prob.goal, pdkb.pddl.formula.And)

        for g in prob.goal.args:
            self.goal.add_rml(prim2rml(g))


class ValidGeneration(Problem):
    def __init__(self, prob, domain):
        self.domain = domain
        self.parse_parts(prob)

    def preprocess(self):

        # Project the initial state
        new_init = PDKB(self.init.depth, self.init.agents, self.init.props)
        rmls = self.init.rmls
        for ag in self.agent_projection:
            rmls = project(rmls, ag)
        new_init.rmls = rmls
        self.init = new_init

        self.orig_cond_count = 0
        self.comp_cond_count = 0

        # Expand and project the action's effects with derived conditional effects
        for act in self.domain.actions:

            self.orig_cond_count += sum([len(act.effs[i][0]) + len(act.effs[i][1]) for i in range(len(act.effs))])
            act.expand()
            self.comp_cond_count += sum([len(act.effs[i][0]) + len(act.effs[i][1]) for i in range(len(act.effs))])

            for ag in self.agent_projection:
                act.project_effects(ag)

            if self.agent_projection:
                # We project the precondition separately since we are in the
                #  perspective of the final agent
                act.project_pre(self.agent_projection[-1])

    def solve(self, old_planner=False):

        print("\n\nCond effs (orig): %d (%d)" % (self.comp_cond_count, self.orig_cond_count))

        # Write the pddl files
        write_file('pdkb-domain.pddl', self.domain.pddl())
        write_file('pdkb-problem.pddl', self.pddl())

        # Solve the problem
        planner_path = os.path.dirname(os.path.abspath(__file__))
        
        # chosen_planner = 'bfws' # Can use bfs_f, siw, siw-then-bfsf, or bfws
        # planner_options = '--k-M-BFWS 2 --max_novelty 1' # make sure they make sense with the planner choice
        # planner_cmd = "%s/planners/%s --domain pdkb-domain.pddl --problem pdkb-problem.pddl --output pdkb-plan.txt %s" % (planner_path, chosen_planner, planner_options)
        
        if old_planner:
            planner_cmd = "%s/planners/siw-then-bfsf --domain pdkb-domain.pddl --problem pdkb-problem.pddl --output pdkb-plan.txt" % planner_path
        else:
            planner_cmd = "python3 %s/planners/staged_bfws.py pdkb-domain.pddl pdkb-problem.pddl pdkb-plan.txt" % planner_path

        t0 = time.time()
        run_command(planner_cmd,
                    output_file = 'pdkb-plan.out',
                    MEMLIMIT = "2000000",
                    TIMELIMIT = "1800")
        print("\nPlan Time: %.5f\n" % (time.time() - t0))
        self.plan = parse_output_ipc('pdkb-plan.txt')

        print("Plan Length: %d\n" % len(self.plan.actions))


    def output_solution(self):
        print("\n  --{ Plan }--\n")
        index = 1
        for a in self.plan.actions:
            print("%d. %s" % (index, str(a)))
            index += 1

    def pddl(self):
        to_ret =  "(define (problem %s-prob)\n\n" % self.domain.name
        to_ret += "    (:domain %s)\n\n" % self.domain.name
        to_ret += "    (:init\n"
        for (key, rml) in sorted([(str(r), r) for r in self.init]):
            to_ret += "        (%s)\n" % rml.pddl()
        to_ret += "    )\n\n"
        to_ret += "    (:goal (and\n"
        for (key, rml) in sorted([(str(r), r) for r in self.goal]):
            to_ret += "        (%s)\n" % rml.pddl()
        to_ret += "    ))\n"
        to_ret += ')'

        return to_ret


class ValidAssessment(Problem):
    def __init__(self, prob, domain):
        self.domain = domain
        self.parse_parts(prob)

        assert 'plan' in dir(prob), "Error: Must provide a plan for ValidAssessment"
        self.actions = prob.plan

    def preprocess(self):

        # Project the initial state
        new_init = PDKB(self.init.depth, self.init.agents, self.init.props)
        rmls = self.init.rmls
        for ag in self.agent_projection:
            rmls = project(rmls, ag)
        new_init.rmls = rmls
        self.init = new_init

        # Expand and project the action's effects with derived conditional effects
        for act in self.domain.actions:
            act.expand()
            for ag in self.agent_projection:
                act.project_effects(ag)

            if self.agent_projection:
                # We project the precondition separately since we are in the
                #  perspective of the final agent
                act.project_pre(self.agent_projection[-1])

    # Parameter may be passed in if the "old planner" is requested.
    def solve(self, _=None):

        # Write the domain pddl file in case we want to debug
        write_file('pdkb-domain.pddl', self.domain.pddl())

        # Map the actions we need to refer to from the provided plan
        self.act_map = {}
        for act in self.domain.actions:
            self.act_map[act.name] = act
        for a in self.actions:
            assert a in self.act_map, "%s not in %s" % (str(a), str(sorted(set(self.act_map.keys()))))

        # Simulate the plan
        current_state = self.init
        self.executable = True
        for a in self.actions:
            if not self.act_map[a].applicable(current_state):
                self.first_fail = a
                self.failed_state = current_state
                self.executable = False
                break
            current_state = self.act_map[a].apply(current_state)[0]

        # Check that the goal holds / store the result
        if self.executable:
            self.final_state = current_state
            self.goal_holds = (self.goal.rmls <= self.final_state.rmls)
            self.goal_violation = (self.goal.rmls - self.final_state.rmls)
        else:
            self.final_state = None
            self.goal_holds = False

    def output_solution(self, relevant=True):
        print()
        print("Assessed the following plan:")
        print("\n".join(self.actions))

        print()
        print("Executable: %s" % str(self.executable))
        print("Goal holds: %s" % str(self.goal_holds))

        if not self.executable:
            print("First failed action: %s" % self.first_fail)
            print("\nFailed state:")
            if relevant:
                print(self.failed_state.relevant_output())
            else:
                print(self.failed_state)

        if self.final_state:
            print("\nFinal state:")
            if relevant:
                print(self.final_state.relevant_output())
            else:
                print(self.final_state)

            if not self.goal_holds:
                print("\nMissing RMLs from goal:")
                print(self.goal_violation)

        print()


class PlausibleGeneration(Problem):
    def __init__(self, prob, domain):
        self.domain = domain

    def solve(self):
        raise NotImplementedError

    def output_solution(self):
        raise NotImplementedError


class PlausibleAssessment(Problem):
    def __init__(self, prob, domain):
        self.domain = domain

    def solve(self):
        raise NotImplementedError

    def output_solution(self):
        raise NotImplementedError


class Domain:

    def __init__(self, agents, props, akprops, actions, depth, types, name='pdkb-planning'):
        self.agents = agents
        self.props = props
        self.akprops = akprops
        self.actions = actions
        self.depth = depth
        self.name = name
        self.types = types

    def pddl(self):

        pdkb = PDKB(self.depth, self.agents, self.props)
        akpdkb = PDKB(0, [], self.akprops)

        to_ret =  "(define (domain %s)\n\n" % self.name
        to_ret += "    (:requirements :strips :conditional-effects)\n\n"
        to_ret += "    (:predicates\n"

        PROPS = pdkb.all_rmls | akpdkb.all_rmls
        assert 0 == len(pdkb.all_rmls & akpdkb.all_rmls), "Error: Detected overlap in regular fluents and always known fluents"

        print("\n\n# Agents: %d" % len(self.agents))
        print("# Props: %d" % len(PROPS))
        print("# Acts: %d" % len(self.actions))
        print("# Effs: %d" % sum([a.num_effs() for a in self.actions]))
        print("Depth: %d" % self.depth)

        for (key, rml) in sorted([(str(r), r) for r in PROPS]):
            to_ret += "        (%s)\n" % rml.pddl()

        to_ret += "    )\n\n"

        for (key, act) in sorted([(a.name, a) for a in self.actions]):
            to_ret += "%s\n\n" % act.pddl()

        to_ret += ')'

        return to_ret


PROBLEM_TYPES = {'valid_generation': ValidGeneration,
                 'valid_assessment': ValidAssessment,
                 'plausible_generation': PlausibleGeneration,
                 'plausible_assessment': PlausibleAssessment}
