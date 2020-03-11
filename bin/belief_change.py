
import sys, os

from pdkb.test.belief_change import doit, checkit

from pdkb.axiom_systems import AxiomSystem, KD, KT

AXIOM_SYSTEMS = [KD, KT]

if __name__ == '__main__':

    if len(sys.argv) < 2 or len(sys.argv) > 3 or sys.argv[1] not in ['run', 'assess']:
        print "\n Usage: python belief-change.py [run|assess] \n"
        sys.exit(1)

    file_basename = 'belief_change'
    if len(sys.argv) == 3:
        file_basename = sys.argv[2]

    if 'run' == sys.argv[1]:
        for axiom_system in AXIOM_SYSTEMS:
            AxiomSystem.SYSTEM = axiom_system

            filename = ('%s_%s.csv' % (file_basename, AxiomSystem.SYSTEM))
            doit(filename)

    elif 'assess' == sys.argv[1]:
        checkit(file_basename)
