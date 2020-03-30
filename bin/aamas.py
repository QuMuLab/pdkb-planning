
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from pdkb.test.aamas import doit, checkit

if __name__ == '__main__':

    if len(sys.argv) < 2 or len(sys.argv) > 3 or sys.argv[1] not in ['run', 'assess']:
        print("\n Usage: python aamas.py [run|assess {filename}] \n")
        sys.exit(1)

    if 'run' == sys.argv[1]:
        doit()

    elif 'assess' == sys.argv[1]:
        if len(sys.argv) == 2:
            checkit('aamas.csv')
        else:
            checkit(sys.argv[2])
