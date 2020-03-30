
import sys, random, time

from pdkb.kd45 import *
from pdkb.indexed_kd45 import *
from pdkb.pinf import *
from pdkb.rml import *
from pdkb.test.utils import random_pdkb, random_rml, write_file, append_file, load_CSV

TYPE = 'small'
NUM_PDKBS = 30
QUERIES_PER_PDKB = 30

if 'small' == TYPE:
    SIZE = (20, 30)
    DEPTH = (2,3)
    FLUENTS = list(map(Literal, 'pqr'))
    FLUENT_RANGE = (2,3)
    RMLS = (3,8)

elif 'normal' == TYPE:
    SIZE = (30,60)
    DEPTH = (4,7)
    FLUENTS = list(map(Literal, 'pqrst'))
    FLUENT_RANGE = (3,5)
    RMLS = (13,39)

elif 'big' == TYPE:
    SIZE = (10,100)
    DEPTH = (3,10)
    FLUENTS = list(map(Literal, 'pqrstvwxyz'))
    FLUENT_RANGE = (5,10)
    RMLS = (50,150)

else:
    assert False, "Bad experiment type: %s" % TYPE

INF_KD = '$INF_{KD}$'
INF_KT = '$INF_{KT}$'
CLOSURE_KD = 'Closure$_{KD}$'
CLOSURE_KT = 'Closure$_{KT}$'
V_KD = '$V_{KD}$'
V_KT = '$V_{KT}$'

INF_KD_SIZE = 3
CLOSURE_KD_SIZE = 4
V_KD_SIZE = 5
INF_KD_QUERY = 6
CLOSURE_KD_QUERY = 7
V_KD_QUERY = 8
INF_KD_UPDATE = 9
CLOSURE_KD_UPDATE = 10
V_KD_UPDATE = 11

INF_KT_SIZE = 15
CLOSURE_KT_SIZE = 16
V_KT_SIZE = 17
INF_KT_QUERY = 18
CLOSURE_KT_QUERY = 19
V_KT_QUERY = 20
INF_KT_UPDATE = 21
CLOSURE_KT_UPDATE = 22
V_KT_UPDATE = 23

COLOUR_1 = '#1112c4'
COLOUR_2 = '#1b9e77'
COLOUR_3 = '#d95f02'
COLOUR_4 = '#3331b2'
COLOUR_5 = '#7570b3'
COLOUR_6 = '#4550b3'

COLOUR_1 = '#1112c4'
COLOUR_2 = '#1b9e77'
COLOUR_3 = 'yellow'
COLOUR_4 = 'blue'
COLOUR_5 = 'black'
COLOUR_6 = 'red'

COLOURS = {}
COLOURS[INF_KD] =  COLOUR_1
COLOURS[INF_KT] = COLOUR_2
COLOURS[CLOSURE_KD] = COLOUR_3
COLOURS[CLOSURE_KT] = COLOUR_4
COLOURS[V_KD] = COLOUR_5
COLOURS[V_KT] = COLOUR_6

def now():
    return time.time()


def doit(filename):

    skip_size = 0
    skip_dep = 0

    if skip_size == 0 and skip_dep == 0:
        write_file(filename, 'agents,depth,fluents,inf-size,closed-size,reduced-size,inf-query,closed-query,reduced-query,inf-update,closed-update,reduced-update')

    for size in range(SIZE[0], SIZE[1] + 10, 10):
        for dep in range(DEPTH[0], DEPTH[1]+1):

            if size < skip_size:
                continue
            elif size == skip_size and dep < skip_dep:
                continue

            print()
            print("--------------")
            print("   %d x %d" % (size, dep))
            print("--------------")
            (times, sizes) = get_size_and_time(size, dep, FLUENTS)
            print()
            print("-------------------------")

            append_file(filename, "\n%d,%d,%d,%f,%f,%f,%f,%f,%f,%f,%f,%f" % (size, dep, len(FLUENTS), sizes[0], sizes[1], sizes[2], times[0], times[1], times[2], times[3], times[4], times[5]))

    #csv = ['agents,depth,fluents,reduced-rmls,closed-rmls,inf-size,closed-size,reduced-size,inf-pre,closed-pre,inf-query,closed-query,reduced-query,result']
    #csv_yes = [csv[0]]
    #csv_no = [csv[0]]

    #kbs.append(random_pdkb(random.randint(DEPTH[0], DEPTH[1]),
    #                               random.randint(AGENTS[0], AGENTS[1]),
    #                               FLUENTS[:random.randint(FLUENT_RANGE[0], FLUENT_RANGE[1])],
    #                               random.randint(RMLS[0], RMLS[1]),
    #                               False))


def get_size_and_time(num_agents, depth, fluents):

    agents = list(range(1, num_agents + 1))

    def generate_kbs():
        numRMLs = num_agents #num_agents * depth * 2
        closed_kb = PDKB(depth, agents, fluents)
        indexed_kb = IndexedPDKB(depth, agents, fluents)
        count = 0
        while count < numRMLs:
            next_rml = random_rml(depth, agents, fluents)
            if not closed_kb.query(neg(next_rml)):
                closed_kb.add_rml(next_rml)
                closed_kb.logically_close()
                indexed_kb.expand(set([next_rml]))
                count += 1

        inf_kb = [] #INF.PDKB2INF(closed_kb)
        return (inf_kb, closed_kb, indexed_kb)
    
    '''
    print
    print "Generating %d PDKBs..." % NUM_PDKBS
    kbs = []
    infs = []
    indexed_kbs = []
    progress = 10
    trial = 1

    for i in range(NUM_PDKBS):
        if trial > progress:
            print "%d%%" % progress
            progress += 10
        trial += 1

        (inf_kb, closed_kb, indexed_kb) = generate_kbs()
        kbs.append(closed_kb)
        indexed_kbs.append(indexed_kb)
        infs.append(inf_kb)

    print

    print "Closing PDKBs..."
    closed_kbs = [kb.copy() for kb in kbs]
    closure_time = []
    progress = 10
    trial = 1
    for kb in closed_kbs:
        if trial > progress:
            print "%d%%" % progress
            progress += 10
        trial += 1
        start = now()
        kb.logically_close()
        assert kb.is_consistent()
        closure_time.append(now() - start)
    print

    print "Computing INFs..."
    for kb in kbs:
        start = now()
        infs.append(INF.PDKB2INF(kb))
        inf_time.append(now() - start)
    '''

    def run_queries(index, rml, infs_kb, closed_kb, indexed_kb):
        start = now()
        #ans1 = infs_kb.query(rml)
        inf_query = 0.0 #now() - start
        start = now()
        #ans2 = rml in closed_kbs[index].rmls
        ans2 = closed_kb.query(rml)
        closed_query = now() - start
        start = now()
        ans3 = indexed_kb.query(rml)
        indexed_query = now() - start

        ans1 = ans2
        assert ans1 == ans2
        assert ans2 == ans3

        # Copy the KBs to run update commands without changing the original KBs
        copy_kb = closed_kb.copy()
        copy_indexed_kb = indexed_kb.copy()

        #start = now()
        # INF update is not yet implemented...
        inf_update = 0.0 #now() - start
        start = now()
        copy_kb.update(set([rml]))
        closed_update = now() - start
        start = now()
        copy_indexed_kb.update(set([rml]))
        indexed_update = now() - start

        return (ans1, ans2, ans3, inf_query, closed_query, indexed_query, inf_update, closed_update, indexed_update)

    #print "Performing random misc queries..."
    for i in range(NUM_PDKBS):
    #for i in range(0):
        (infs_kb, closed_kb, indexed_kb) = generate_kbs()
        for j in range(QUERIES_PER_PDKB):

            rml = random_rml(closed_kb.depth, closed_kb.agents, closed_kb.props)
            (ans1, ans2, ans3, inf_query, closed_query, indexed_query, inf_update, closed_update, indexed_update) = run_queries(i, rml, infs_kb, closed_kb, indexed_kb)
            #(inf_update, closed_update, indexed_update) =

            #csv.append("%d,%d,%d,%d,%d,%d,%d,%d,%f,%f,%f,%f,%f,%s" %
            #           (len(kbs[i].agents), kbs[i].depth, len(kbs[i].props), len(kbs[i].rmls), len(closed_kbs[i].rmls), infs[i].size(), closed_kbs[i].size(), kbs[i].size(),
            #            inf_time[i], closure_time[i], inf_query, closed_query, indexed_query, str(ans1)))

    print("Performing random successful queries...")
    times = [0.0,0.0,0.0,0.0,0.0,0.0]
    for i in range(NUM_PDKBS):

        (infs_kb, closed_kb, indexed_kb) = generate_kbs()

        for j in range(QUERIES_PER_PDKB):

            # Get a random RML from the PDKB
            rml = random.choice(list(closed_kb.rmls))
            # Get the closed set
            #entailed = list(kd_closure(rml))
            # Pick a random element
            #rml = random.choice(entailed)
            #(infs_kb, closed_kb, indexed_kb) = generate_kbs()
            (ans1, ans2, ans3, inf_query, closed_query, indexed_query, inf_update,  closed_update, indexed_update) = run_queries(i, rml, infs_kb, closed_kb, indexed_kb)

            assert ans1 == ans2
            assert ans2 == ans3

            times[0] += inf_query
            times[1] += closed_query
            times[2] += indexed_query
            times[3] += inf_update
            times[4] += closed_update
            times[5] += indexed_update

            #csv_yes.append("%d,%d,%d,%d,%d,%d,%d,%d,%f,%f,%f,%f,%f,%s" %
            #               (len(kbs[i].agents), kbs[i].depth, len(kbs[i].props), len(kbs[i].rmls), len(closed_kbs[i].rmls), infs[i].size(), closed_kbs[i].size(), kbs[i].size(),
            #                inf_time[i], closure_time[i], inf_query, closed_query, indexed_query, str(ans1)))

    sizes = [0.0, 0.0, 0.0]
    print("Performing random unsuccessful queries...")
    for i in range(NUM_PDKBS):

        (infs_kb, closed_kb, indexed_kb) = generate_kbs()

        sizes[0] += 0.0 #infs_kb.size()
        sizes[1] += closed_kb.size()
        sizes[2] += indexed_kb.size()

        for j in range(QUERIES_PER_PDKB):


            going = True
            while going:
                rml = random_rml(closed_kb.depth, closed_kb.agents, closed_kb.props)
                if rml not in closed_kb.rmls:
                    going = False
            (ans1, ans2, ans3, inf_query, closed_query, indexed_query, inf_update, closed_update, indexed_update) = run_queries(i, rml, infs_kb, closed_kb, indexed_kb)

            assert ans1 == ans2
            assert ans2 == ans3

            times[0] += inf_query
            times[1] += closed_query
            times[2] += indexed_query
            times[3] += inf_update
            times[4] += closed_update
            times[5] += indexed_update

            #csv_no.append("%d,%d,%d,%d,%d,%d,%d,%d,%f,%f,%f,%f,%f,%s" %
            #              (len(kbs[i].agents), kbs[i].depth, len(kbs[i].props), len(kbs[i].rmls), len(closed_kbs[i].rmls), infs[i].size(), closed_kbs[i].size(), kbs[i].size(),
            #               inf_time[i], closure_time[i], inf_query, closed_query, indexed_query, str(ans1)))


    times[0] /= float(NUM_PDKBS * QUERIES_PER_PDKB * 2)
    times[1] /= float(NUM_PDKBS * QUERIES_PER_PDKB * 2)
    times[2] /= float(NUM_PDKBS * QUERIES_PER_PDKB * 2)
    times[3] /= float(NUM_PDKBS * QUERIES_PER_PDKB * 2)
    times[4] /= float(NUM_PDKBS * QUERIES_PER_PDKB * 2)
    times[5] /= float(NUM_PDKBS * QUERIES_PER_PDKB * 2)

    #sizes.append(float(sum([inf.size() for inf in infs])) / float(NUM_PDKBS))
    #sizes.append(float(sum([kb.size() for kb in kbs])) / float(NUM_PDKBS))
    #sizes.append(float(sum([kb.size() for kb in indexed_kbs])) / float(NUM_PDKBS))
    sizes[0] /= float(NUM_PDKBS)
    sizes[1] /= float(NUM_PDKBS)
    sizes[2] /= float(NUM_PDKBS)

    print("\nDone!\n")

    return (times, sizes)


def checkit(filename):

    data_kd = load_CSV(filename + "_kd.csv")[1:]
    data_kt = load_CSV(filename + "_kt.csv")[1:]

    # Merge the two sets row by row
    assert len(data_kd) == len(data_kt)
    data = []
    for i in range(0, len(data_kd)):
        data.append(data_kd[i] + data_kt[i])

    for row in data:
        for i in range(len(row)):
            if row[i] == '0.000000':
                row[i] = '0.000001'


    def plot_data(data, inds, labels, zlabel, fname):

        data_map = {}
        for size in range(SIZE[0], SIZE[1] + 10, 10):
            data_map[size] = {}
            for dep in range(DEPTH[0], DEPTH[1]+1):
                data_map[size][dep] = {}

        for row in data:
            data_map[int(row[0])][int(row[1])][inds[0]] = float(row[inds[0]])
            data_map[int(row[0])][int(row[1])][inds[1]] = float(row[inds[1]])
            data_map[int(row[0])][int(row[1])][inds[2]] = float(row[inds[2]])
            data_map[int(row[0])][int(row[1])][inds[3]] = float(row[inds[3]])

        from mpl_toolkits.mplot3d import axes3d
        import matplotlib.pyplot as plt
        import matplotlib
        import numpy as np

        X, Y = np.meshgrid(np.arange(SIZE[0], SIZE[1] + 10, 10), np.arange(DEPTH[0], DEPTH[1]+1))

        zs0 = np.array([data_map[x][y][inds[0]] for x,y in zip(np.ravel(X), np.ravel(Y))])
        zs1 = np.array([data_map[x][y][inds[1]] for x,y in zip(np.ravel(X), np.ravel(Y))])
        zs2 = np.array([data_map[x][y][inds[2]] for x,y in zip(np.ravel(X), np.ravel(Y))])
        zs3 = np.array([data_map[x][y][inds[3]] for x,y in zip(np.ravel(X), np.ravel(Y))])

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        #if 'Query Time ($log_e(sec)$)' == zlabel or 'Update Time ($log_e(sec)$)' == zlabel:

        Z0 = np.log(zs0).reshape(X.shape)
        Z1 = np.log(zs1).reshape(X.shape)
        Z2 = np.log(zs2).reshape(X.shape)
        Z3 = np.log(zs3).reshape(X.shape)
#        else:
            #ax.set_zticks([])
        '''
        Z0 = (zs0 / 1).reshape(X.shape)
        Z1 = (zs1 / 1).reshape(X.shape)
        Z2 = (zs2 / 1).reshape(X.shape)
        Z3 = (zs3 / 1).reshape(X.shape)
        '''

        cols = []
        for i in range(0, len(labels)):
            cols.append(COLOURS[labels[i]])

        ax.plot_wireframe(X, Y, Z0, color=cols[0])
        ax.plot_wireframe(X, Y, Z1, color=cols[1])
        ax.plot_wireframe(X, Y, Z2, color=cols[2])
        ax.plot_wireframe(X, Y, Z3, color=cols[3])

        #cset = ax.contourf(X, Y, Z0, zdir='z', offset=-100, cmap=matplotlib.cm.coolwarm)
        #cset = ax.contourf(X, Y, Z0, zdir='x', offset=0, cmap=matplotlib.cm.coolwarm)
        #cset = ax.contourf(X, Y, Z0, zdir='z', offset=0, cmap=matplotlib.cm.coolwarm)
        #cset = ax.contourf(X, Y, Z0, zdir='y', offset=40, cmap=cm.coolwarm)

        ax.set_xlabel('# of Agents')
        ax.set_ylabel('Maximum Depth')
        ax.set_zlabel(zlabel)

        scatter1_proxy = matplotlib.lines.Line2D([0],[0], linestyle="none", c=cols[0], marker = 's')
        scatter2_proxy = matplotlib.lines.Line2D([0],[0], linestyle="none", c=cols[1], marker = 's')
        scatter3_proxy = matplotlib.lines.Line2D([0],[0], linestyle="none", c=cols[2], marker = 's')
        scatter4_proxy = matplotlib.lines.Line2D([0],[0], linestyle="none", c=cols[3], marker = 's')
        ax.legend([scatter1_proxy, scatter2_proxy, scatter3_proxy, scatter4_proxy], labels, numpoints = 1)

        ax.get_xaxis().set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
        ax.get_yaxis().set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))

        plt.show()


    print("Plotting query time...")
    plot_data(data, [V_KT_QUERY, V_KD_QUERY, CLOSURE_KD_QUERY, CLOSURE_KT_QUERY], [V_KT, V_KD, CLOSURE_KD, CLOSURE_KT], 'Query Time ($log_e(sec)$)', 'time.eps')

    print("Plotting size...")
    plot_data(data, [CLOSURE_KT_SIZE, CLOSURE_KD_SIZE, V_KD_SIZE, V_KT_SIZE], [CLOSURE_KT, CLOSURE_KD, V_KD, V_KT], 'Size (x1000)', 'size.eps')

    print("Plotting update time...")
    plot_data(data, [CLOSURE_KT_UPDATE, CLOSURE_KD_UPDATE, V_KT_UPDATE, V_KD_UPDATE], [CLOSURE_KT, CLOSURE_KD, V_KT, V_KD], 'Update Time ($log_e(sec)$)', 'update_time.eps')



