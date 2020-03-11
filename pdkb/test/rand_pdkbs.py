

import os, sys, random

from pdkb.kd45 import PDKB, project, kd_closure, closure_set_of_rmls, kt_closure, KD, KT, KD45, S5, CLOSURE

from pdkb.indexed_kd45 import IndexedPDKB, sub_lattice

from pdkb.rml import RML, Belief, Possible, Literal, neg

from pdkb.axiom_systems import AxiomSystem

from pdkb.test.utils import random_rml, random_pdkb, parse_test_pdkb, test_kripke

from krrt.utils import read_file, write_file, get_file_list


def test0():
    test_files = get_file_list('examples/', match_list=['.pdkb'])
    for f in test_files:
        print "\n Testing file: %s" % f
        parse_test_pdkb(f)
        print "***"
        print "*******************************************" * 2
        print "*******************************************" * 2
        print "***\n"

def test1():
    print "\n----\n"

    l1 = Literal('p')
    l2 = Belief(2, Belief(1, l1))
    l3 = Belief(2, neg(Belief(1, neg(l1))))
    l4 = neg(l3)

    l5 = neg(Belief(1, neg(Belief(2, l1))))
    l6 = neg(Belief(1, neg(Belief(2, Possible(3, Belief(4, l1))))))

    print "KD closure operation:"
    print "%s -> %s" % (str(l2), str(map(str, kd_closure(l2))))
    print "%s -> %s" % (str(l3), str(map(str, kd_closure(l3))))

    print "\n----\n"

    kb = PDKB(2, [1,2], map(Literal, ['p', 'q']))
    kb.add_rml(l2)
    print "Initial KB:"
    print kb
    print "\nClosing..."
    kb.logically_close()
    print kb

    print "\n----\n"

    kb.add_rml(l4)
    print "Initial Closed KB:"
    kb.logically_close()
    print kb
    print "\nConsistent: %s" % str(kb.is_consistent())

    print "\n----\n"

    kb = PDKB(2, [1,2], map(Literal, ['p', 'q']))
    kb.add_rml(Belief(1, Literal('p')))
    kb.add_rml(Belief(2, Literal('q')))
    kb.add_rml(Belief(1, Belief(2, Literal('q'))))
    kb.add_rml(neg(Belief(1, Literal('q'))))
    print "Initial KB:"
    print kb
    print "\n...projecting on agent 1\n"
    print project(kb.rmls, 1)

    print "\n----\n"

    


def test2():

    kb = PDKB(1, [1], map(Literal, ['p', 'q']))

    l1 = neg(Literal('p'))
    l2 = Belief(1, Literal('p'))
    l3 = Belief(1, neg(Literal('q')))

    kb.add_rml(l1)
    kb.add_rml(l2)
    kb.add_rml(l3)

    test_kripke(kb, [l1, l2, l3])

def test3():
    kb = PDKB(1, [1], map(Literal, ['p', 'q']))

    l1 = Literal('p')
    l2 = Belief(1, Literal('q'))

    kb.add_rml(l1)
    kb.add_rml(l2)

    test_kripke(kb, [l1, l2])

def test4():
    kb = PDKB(1, [1,2], map(Literal, ['p', 'q', 'r']))

    rmls = [
        Literal('p'),
        Belief(1, Literal('q')),
        Belief(2, neg(Literal('q')))
    ]

    for rml in rmls:
        kb.add_rml(rml)

    test_kripke(kb, rmls)

def test5():
    kb = PDKB(2, [1,2], map(Literal, ['p', 'q']))

    rmls = [
        Literal('p'),
        Belief(1, Literal('q')),
        Belief(1, Belief(2, neg(Literal('q'))))
    ]

    for rml in rmls:
        kb.add_rml(rml)

    test_kripke(kb, rmls)


def test6():
    print "-- START TEST 6 --"

    for axiom_system in [KD, KT]:
        AxiomSystem.SYSTEM = axiom_system
        kb1 = PDKB(1, [1,2], map(Literal, ['p', 'q']))
        kb2 = PDKB(1, [1,2], map(Literal, ['p', 'q']))
        test_expand(kb1, kb2)

        # Test that adding an RML already implied does nothing
        kb1 = IndexedPDKB(1, [1,2], map(Literal, ['p', 'q']))
        kb1.expand(set([Belief(1, Literal('p'))]))
        kb2 = kb1.copy()
        kb1.expand(set([Possible(1, Literal('p'))]))
        assert kb1 == kb2

        # Test that adding an RML that implies an existing RML removes that RML
        kb1 = IndexedPDKB(1, [1,2], map(Literal, ['p', 'q']))
        kb1.expand(set([Possible(1, Literal('p'))]))
        old_size = kb1.size()
        kb1.expand(set([Belief(1, Literal('p'))]))
        assert kb1.size() == old_size, "kb1 = %s, old = %s" % (kb1.size(), old_size)

        l1 = Belief(1, Literal('p'))
        l2 = Belief(2, Literal('p'))
        assert not l1.entails_rml(l2)

    for axiom_system in [KD, KT]:
        AxiomSystem.SYSTEM = axiom_system
        kb1 = IndexedPDKB(1, [1,2], map(Literal, ['p', 'q']))
        kb2 = IndexedPDKB(1, [1,2], map(Literal, ['p', 'q']))
        test_expand(kb1, kb2)       

    print "-- END TEST 6 --\n"

def test7():

    print "-- START TEST 7 --"
    AxiomSystem.SYSTEM = KD
    kb = PDKB(1, [1,2,3], map(Literal, ['p', 'q']))
    test_remove(kb)
        
    kb = IndexedPDKB(1, [1,2,3], map(Literal, ['p', 'q']))
    test_remove(kb)

    AxiomSystem.SYSTEM = KT
    kb = PDKB(1, [1,2,3], map(Literal, ['p', 'q']))
    test_remove_kt(kb)
        
    kb = IndexedPDKB(1, [1,2,3], map(Literal, ['p', 'q']))
    test_remove_kt(kb)
    
    print "-- END TEST 7 --\n"

def test8():

    print "-- START TEST 8 --"

    for axiom_system in [KD, KT]:
        AxiomSystem.SYSTEM = axiom_system
        kb = PDKB(1, [1,2], map(Literal, ['p', 'q']))
        test_update(kb)

        indexed_kb = IndexedPDKB(1, [1,2], map(Literal, ['p', 'q']))
        test_update(indexed_kb)

    print "-- END TEST 8 --\n"

def test9():
    print "-- START TEST 9 --"

    for axiom_system in [KD, KT]:
        AxiomSystem.SYSTEM = axiom_system
        kb1 = PDKB(3, [1,2,3], map(Literal, ['p', 'q', 'r']))
        kb2 = IndexedPDKB(3, [1,2,3], map(Literal, ['p', 'q', 'r']))

        test_consistency(kb1, kb2)

    print "-- END TEST 9 --\n"

def test10():
    print "-- START TEST 10 --"

    for axiom_system in [KD, KT]:
        AxiomSystem.SYSTEM = axiom_system
        kb1 = PDKB(3, [1,2,3,4], map(Literal, ['p', 'q', 'r']))
        kb2 = IndexedPDKB(3, [1,2,3,4], map(Literal, ['p', 'q', 'r']))

        test_consistency_random_kb(kb1, kb2)

    print "-- END TEST 10 --\n"

def test11():
    print "-- START TEST 11 --"
    # Test helper functions
    AxiomSystem.SYSTEM = KD
    p = Belief(2, Belief(1, Literal('p')))
    q = Possible(2, Possible(1, Literal('p')))

    sub = sub_lattice(p, q)
    assert len(sub) == 4, "len(%s) == %d" % (str(sub), len(sub))
    assert p in sub
    assert q in sub
    assert not any(r for r in sub if r.entails_rml(p) and r != p)
    assert all(r for r in sub if r.entails_rml(q))
    assert Belief(2, Possible(1, Literal('p'))) in sub
    assert Possible(2, Belief(1, Literal('p'))) in sub

    p = Belief(5, Possible(4, Belief(3, Belief(2, Belief(1, neg(Literal('p')))))))
    q = Possible(5, Possible(4, Belief(3, Possible(2, Possible(1, neg(Literal('p')))))))
    sub = sub_lattice(p, q)
    assert len(sub) == 8, "len(%s) == %d" % (str(sub), len(sub))
    assert p in sub
    assert q in sub
    assert not any(r for r in sub if r.entails_rml(p) and r != p)
    assert all(r for r in sub if r.entails_rml(q))
    assert Possible(5, Possible(4, Belief(3, Possible(2, Belief(1, neg(Literal('p'))))))) in sub
    assert Belief(5, Belief(4, Belief(3, Belief(2, Belief(1, neg(Literal('p'))))))) not in sub

    # Switch to axiom system KT
    AxiomSystem.SYSTEM = KT
    p = Belief(1, Belief(2, Literal('p')))
    q = Possible(2, Literal('p'))
    sub = sub_lattice(p, q)
    assert len(sub) == 4, "len(%s) == %d" % (str(sub), len(sub))
    assert p in sub
    assert q in sub
    assert not any(r for r in sub if r.entails_rml(p) and r != p)
    assert all(r for r in sub if r.entails_rml(q))
    assert Belief(1, Possible(2, Literal('p'))) in sub
    assert Belief(2, Literal('p')) in sub
    
    p = Belief(1, Possible(2, Belief(3, Belief(4, neg(Literal('p'))))))
    q = Possible(2, neg(Literal('p')))
    sub = sub_lattice(p, q)
    assert len(sub) == 8, "len(%s) == %d" % (str(sub), len(sub))
    assert p in sub
    assert q in sub
    assert not any(r for r in sub if r.entails_rml(p) and r != p)
    assert all(r for r in sub if r.entails_rml(q))
    assert Possible(2, Belief(3, Belief(4, neg(Literal('p'))))) in sub
    assert Possible(2, Belief(4, neg(Literal('p')))) in sub
    assert Possible(2, Possible(3, neg(Literal('p')))) not in sub

    print "-- END TEST 11 --\n"

def test12():
    print "-- START TEST 12 --"

    #kb1 = PDKB(3, [1,2,3], map(Literal, ['p', 'q', 'r']))
    kb2 = IndexedPDKB(3, [1,2,3], map(Literal, ['p', 'q', 'r']))
    kb3 = IndexedPDKB(3, [1,2,3], map(Literal, ['p', 'q', 'r']))

    l1 = Belief(1, Belief(2, Literal('p')))
    l2 = Possible(1, Belief(2, Literal('p')))
    kb2.expand(set([l1]))
    kb3.expand(set([l2]))

    assert kb2.query_t(Literal('p'))
    assert not kb3.query_t(Literal('p'))

    l1_closed = kt_closure(l1)
    assert l1 in l1_closed
    assert Belief(1, Literal('p')) in l1_closed
    assert Belief(2, Literal('p')) in l1_closed
    assert Literal('p') in l1_closed

    l2_closed = kt_closure(l2)
    fully_closed = []
    for rml in l2_closed:
        fully_closed += kd_closure(rml)
    assert l2 in fully_closed
    assert Possible(1, Possible(2, Literal('p'))) in fully_closed
    assert Possible(1, Literal('p')) in fully_closed

    print "-- END TEST 12 --\n"

def test13():
    print "-- START TEST 13 --"

    AxiomSystem.SYSTEM = KD
    l1 = Belief(1, Belief(2, Literal('p')))
    l2 = Belief(1, Possible(2, Literal('p')))
    l3 = Possible(2, Literal('p'))
    l4 = Belief(1, Literal('p'))
    assert l1.kd_entails_rml(l2)
    assert not l1.kd_entails_rml(l3)
    assert not l1.kd_entails_rml(l4)

    assert l1.kt_entails_rml(l2)
    assert l1.kt_entails_rml(l3)
    assert l1.kt_entails_rml(l4)

    l5 = Belief(1, Possible(3, Literal('p')))
    assert not l1.kt_entails_rml(l5)

    l6 = Possible(1, Belief(2, Literal('p')))
    assert not l6.kt_entails_rml(l1)

    l7 = Possible(1, Literal('p'))
    assert l6.kt_entails_rml(l7)

    AxiomSystem.SYSTEM = KT
    l1 = Belief(2, Belief(1, Possible(2, neg(Literal('r')))))
    l2 = Possible(2, neg(Literal('r')))
    assert l1.kt_entails_rml(l2)

    print "-- END TEST 13 --"

def test14():
    print "-- START TEST 14 --"

    for axiom_system in [KD, KT]:
        AxiomSystem.SYSTEM = axiom_system        

        p = Literal('p')
        q = Literal('q')
        assert p.inconsistent(neg(p))
        assert not p.inconsistent(neg(q))
        assert not p.inconsistent(q)
        
        b1p = Belief(1, p)
        b2p = Belief(2, p)
        b2np = Belief(2, neg(p))
        p1np = Possible(1, neg(p))
        p2np = Possible(2, neg(p))
        p2p = Possible(2, p)
        assert b1p.inconsistent(p1np)
        assert p1np.inconsistent(b1p)
        assert not b1p.inconsistent(b2p)
        assert not b2p.inconsistent(b1p)
        assert b2p.inconsistent(b2np)
        assert b2np.inconsistent(b2p)
        assert (b1p.inconsistent(b2np) == (axiom_system in [KT, S5])), ax_system()
        assert (b2np.inconsistent(b1p) == (axiom_system in [KT, S5])), ax_system()
        assert not b1p.inconsistent(p2np)
        assert not p2np.inconsistent(b1p)
        assert not p1np.inconsistent(p2np) 
        assert not p2np.inconsistent(p1np)
        assert not p2np.inconsistent(p2p)
        
        assert (b1p.inconsistent(neg(p)) == (axiom_system in [KT, S5])), ax_system()      
        assert (neg(p).inconsistent(b1p) == (axiom_system in [KT, S5])), ax_system()
        assert not p1np.inconsistent(p)
        assert not p.inconsistent(p1np)

        b2b1p = Belief(2, b1p)
        b2p1np = Belief(2, p1np)
        assert b2b1p.inconsistent(b2p1np), ax_system()
        assert b2p1np.inconsistent(b2b1p), ax_system()

        assert (b1p.inconsistent(b2p1np) == (axiom_system in [KT, S5])), ax_system()
        assert (b2p1np.inconsistent(b1p) == (axiom_system in [KT, S5])), ax_system()

        assert not b2p.inconsistent(Possible(3, neg(p))), ax_system()
        assert b2p.inconsistent(Possible(2, Belief(1, neg(p)))) == (axiom_system in [KT, S5]), ax_system()

    print "-- END TEST 14 --"

def ax_system():
    return "system = %s" % AxiomSystem.SYSTEM

###################################
## Helper functions called by tests
###################################

def test_expand(kb1, kb2):

    l1 = Literal('p')
    l2 = Belief(2, Belief(1, l1))
    l3 = Belief(2, neg(Belief(1, neg(l1))))
    l4 = neg(l3)

    kb1.expand(set([l1, l2, l3, l4]))
    kb2.add_rml(l1)
    kb2.add_rml(l2)
    kb2.add_rml(l3)
    kb2.add_rml(l4)

    assert kb1.size() == kb2.size()

    l5 = Possible(2, Possible(1, l1))
    assert kb1.query(l5)
    assert kb2.query(l5)

    l6 = Possible(1, l1)
    assert kb1.query(l6) == (AxiomSystem.SYSTEM == KT), "KB = %s\nSystem = %s" % (kb1, AxiomSystem.SYSTEM)

    kb2.remove_rml(l1)
    kb2.remove_rml(l2)
    kb2.remove_rml(l3)
    kb2.remove_rml(l4)
    kb1.contract(set([l1, l2, l3, l4]))

    assert not kb1.query(l1)
    assert not kb2.query(l1)

def test_remove(kb):

    l1 = Belief(2, Belief(1, Literal('p')))
    l2 = Possible(2, Possible(1, Literal('p')))
    l3 = Possible(1, Belief(2, Literal('q')))
    l4 = Belief(1, Possible(2, Literal('q')))

    kb.expand(set([l1, l2, l3, l4]))

    q1 = Possible(2, Belief(1, Literal('p')))
    q2 = Belief(1, Belief(2, Literal('q')))
    
    assert kb.query(q1)
    assert not kb.query(q2)

    kb.remove(set([q1]))

    assert not kb.query(q1)
    assert not kb.query(l1)
    assert kb.query(l2)

    l5 = Possible(1, Possible(2, Literal('q')))
    kb.remove(set([l2, l5]))

    assert kb.size() == 0, "kb.size() == %s" % str(kb.size())

def test_remove_kt(kb):

    l1 = Belief(2, Belief(1, Literal('p')))
    l2 = Possible(2, Possible(1, Literal('p')))
    l3 = Possible(1, Belief(2, Literal('q')))
    l4 = Belief(1, Possible(2, Literal('q')))

    kb.expand(set([l1, l2, l3, l4]))

    q1 = Possible(2, Belief(1, Literal('p')))
    q2 = Belief(1, Belief(2, Literal('q')))
    q3 = Possible(2, Literal('p'))

    assert kb.query(q1)
    assert not kb.query(q2)
    assert kb.query(q3)

    kb.remove(set([q3]))

    assert not kb.query(q1)
    assert not kb.query(l1)
    assert not kb.query(q3)
    assert kb.query(l2)

def test_update(kb):

    l1 = Belief(1, Belief(2, Literal('p')))
    l2 = Belief(1, Belief(2, Literal('q')))

    kb.update(set([l1, l2]))
    assert kb.is_consistent(), str(kb)

    assert kb.query(l1)
    assert kb.query(l2)

    l3 = Possible(1, Possible(2, neg(Literal('p'))))
    l4 = Belief(1, Possible(2, Literal('p')))

    kb.update(set([l3]))
    assert kb.is_consistent(), str(kb)

    assert not kb.query(l1)
    assert kb.query(l2)
    assert kb.query(l3)
    assert kb.query(l4)

    assert kb.is_consistent(), str(kb)

    l5 = Belief(3, neg(Literal('r')))
    kb.update(set([l5]))

    l6 = Belief(3, Literal('r'))
    kb.update(set([l6]))

    assert not kb.query(l5)
    assert kb.query(l6)
    assert kb.query(Possible(3, Literal('r')))

    AxiomSystem.SYSTEM = KT
    kb.reset()
    kb.update(set([Belief(1, Belief(2, Literal('p')))]))
    p1 = Possible(2, Belief(1, neg(Literal('p'))))
    p2 = Possible(3, neg(Literal('p')))
    kb.update(set([p1, p2]))
    q = Literal('p')
    assert kb.query(q) == (AxiomSystem.SYSTEM in [KT, S5])
    assert kb.is_consistent(), str(kb)


# compare consistency of a KB implementation with the PDKB implementation
def test_consistency(pdkb, kb):
    assert isinstance(pdkb, PDKB)

    l1 = Literal('p')
    l2 = Belief(1, Belief(2, l1))
    l3 = Possible(3, Belief(2, Belief(1, neg(l1))))
    l4 = Belief(2, Possible(1, Belief(3, Belief(1, Literal('p')))))

    pdkb.expand(set([l1, l2, l3, l4]))
    kb.expand(set([l1, l2, l3, l4]))

    compare(pdkb, kb)

    l5 = neg(l3)
    pdkb.update(set([l5]))
    kb.update(set([l5]))

    compare(pdkb, kb)

def test_consistency_random_kb(pdkb, kb):
    assert isinstance(pdkb, PDKB)

    NUM_RUNS = 10000
    fluents = map(Literal, 'pqrst')
    agents = list(range(1, 4))
    added = []
    for i in range(0, NUM_RUNS):
        print >> sys.stderr, str(i) + " ",
        kb.reset()
        pdkb.reset()
        rmls = [
            random_rml(4, agents, fluents),
            random_rml(3, agents, fluents),
            random_rml(2, agents, fluents),
            ]
        
        # Only add the RMLs if they are consistent
        check_consistency = PDKB(4, agents, fluents)
        check_consistency.update(set(rmls))
        if check_consistency.is_consistent():
            assert pdkb.is_consistent()
            kb_copy = kb.copy()
            pdkb_copy = pdkb.copy()
            pdkb.update(set(rmls))            
            kb.update(set(rmls))

            rml = compare(pdkb, kb)
            if isinstance(rml, RML):
                kb_copy.restrict(rml)
                pdkb_copy.restrict(rml)
                kb.restrict(rml)
                pdkb.restrict(rml)
                print "before = " + str(kb_copy)
                print "before = " + str(pdkb_copy)
                print "\t add " + str(rmls)
                print "\t after = " + str(kb)
                print "\t after = " + str(pdkb)
                sys.exit()

def compare(pdkb, kb):

    assert pdkb.is_consistent(), "%s\n%s" % (ax_system(), str(pdkb))
    assert kb.is_consistent(), "%s\n%s" % (ax_system(), str(kb))
    for rml in pdkb.all_rmls:
        if kb.query(rml) != pdkb.query(rml):
            print "#############################"
            pdkb.restrict(rml)
            kb.restrict(rml)
            print "RML conflict ax system %s on %s :\n\t %s is %s\n\t%s is %s" % (ax_system(), str(rml), str(pdkb), pdkb.query(rml), str(kb), kb.query(rml))
            print "#############################"
            return rml


