import os
import sys
import time
import pickle

from .actions import *
from .problems import *


def parse_and_preprocess(pdkbddl_file):
    """
    Parses and preprocess a PDKBDDL file.
    Returns a PDKB problem object that can be translated into PDDL.
    """
    if not os.path.isdir('.problem-cache'):
        os.mkdir('.problem-cache')

    print("Parsing problem...", end=' ')
    sys.stdout.flush()
    problem = parse_pdkbddl(pdkbddl_file)
    print("done!")

    print("Preprocessing problem...", end=' ')
    sys.stdout.flush()
    prob_hash = hash(pickle.dumps(problem))
    fname = ".problem-cache/%s" % str(prob_hash)
    if os.path.isfile(fname) and not os.path.isfile('.nocache'):
        problem = pickle.load(open(fname, 'r'))
        print("done! (from cache)")
    else:
        problem.preprocess()
        with open(fname, 'wb') as f:
            pickle.dump(problem, f, 2)
        print("done!")

    return problem


def translate(pdkbddl_file, pddl_domain_file, pddl_problem_file):
    t_start = time.time()
    problem = parse_and_preprocess(pdkbddl_file)
    print("\n\nCond effs (orig): %d (%d)" %
          (problem.comp_cond_count, problem.orig_cond_count))
    write_file(pddl_domain_file, problem.domain.pddl())
    write_file(pddl_problem_file, problem.pddl())
    print("\nTime: %f s" % (time.time() - t_start))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("\nUsage: python translator.py <pdkbddl file>\n\
Creates a PDDL domain and problem file next to the original PDKBDDL file.\n")
        sys.exit(1)

    pdkbddl_file = sys.argv[1]
    pddl_domain_file = pdkbddl_file.replace('.pdkbddl', '-domain.pddl')
    pddl_problem_file = pdkbddl_file.replace('.pdkbddl', '-problem.pddl')
    translate(pdkbddl_file, pddl_domain_file, pddl_problem_file)
