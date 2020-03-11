
import os, sys, time, pickle


from actions import *
from problems import *

def cleanup():
    os.system('rm -f pdkb-domain.pddl')
    os.system('rm -f pdkb-problem.pddl')
    os.system('rm -f pdkb-plan.txt')
    os.system('rm -f pdkb-plan.out')
    os.system('rm -f pdkb-plan.out.err')
    os.system('rm -f execution.details')


def solve(pdkbddl_file):

    print

    if not os.path.isdir('.problem-cache'):
        os.mkdir('.problem-cache')

    t_start = time.time()

    print "Parsing problem...",
    sys.stdout.flush()
    problem = parse_pdkbddl(pdkbddl_file)
    print "done!"

    print "Preprocessing problem...",
    sys.stdout.flush()
    prob_hash = hash(pickle.dumps(problem))
    fname = ".problem-cache/%s" % str(prob_hash)
    if os.path.isfile(fname) and not os.path.isfile('.nocache'):
        problem = pickle.load(open(fname, 'r'))
        print "done! (from cache)"
    else:
        problem.preprocess()
        pickle.dump(problem, open(fname, 'w'), 2)
        print "done!"

    print "Solving problem...",
    sys.stdout.flush()
    problem.solve()
    print "done!"

    print "\nTime: %f s" % (time.time() - t_start)

    problem.output_solution()

    print


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "\nUsage: python planner.py <pdkbddl file> [--keep-files]\n"
        sys.exit(1)

    solve(sys.argv[1])

    if len(sys.argv) < 3 or '--keep-files' != sys.argv[2]:
        cleanup()
