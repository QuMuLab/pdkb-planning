
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from pdkb.test.rand_pdkbs import test0, test1, test2, test3, test4, test5, test6, test7, test8, test9, test10, test11, test12, test13, test14
from pdkb.test.utils import parse_test_pdkb, test_random_pdkb

if __name__ == '__main__':
    if len(sys.argv) > 2:
        assert 'test' == sys.argv[1]
        if sys.argv[2] == 'test_all':
            test6()
            test7()
            test8()
            test9()
            test10()
            test11()
            test12()
            test13()
            test14()
        else:
            [test0, test1, test2, test3, test4, test5, test6, test7, test8, test9, test10, test11, test12, test13,test14][int(sys.argv[2])]()
    elif len(sys.argv) > 1:
        parse_test_pdkb(sys.argv[1])
    else:
        test_random_pdkb(3, 2, 'pq', 5)
