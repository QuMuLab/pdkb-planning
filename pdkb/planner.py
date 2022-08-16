
import os, sys, time, pickle


from .actions import *
from .problems import *
from .translator import *

def cleanup():
    os.system('rm -f pdkb-domain.pddl')
    os.system('rm -f pdkb-problem.pddl')
    os.system('rm -f pdkb-plan.txt')
    os.system('rm -f pdkb-plan.out')
    os.system('rm -f pdkb-plan.out.err')
    os.system('rm -f execution.details')


def solve(pdkbddl_file, old_planner=False):

    print()

    t_start = time.time()
    parse_and_preprocess(pdkbddl_file)

    print("Solving problem...", end=' ')
    sys.stdout.flush()
    problem.solve(old_planner)
    print("done!")

    print("\nTime: %f s" % (time.time() - t_start))

    problem.output_solution()

    print()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("\nUsage: python planner.py <pdkbddl file> [--keep-files] [--old-planner]\n")
        sys.exit(1)

    solve(sys.argv[1], old_planner=('--old-planner' in sys.argv))

    if len(sys.argv) < 3 or '--keep-files' != sys.argv[2]:
        cleanup()
