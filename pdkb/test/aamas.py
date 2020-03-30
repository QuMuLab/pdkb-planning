
import sys, random, time

from pdkb.kd45 import *
from pdkb.indexed_kd45 import *
from pdkb.pinf import *
from pdkb.rml import *
from pdkb.test.utils import random_pdkb, random_rml, write_file, append_file

TYPE = 'normal'
NUM_PDKBS = 10
QUERIES_PER_PDKB = 10

if 'small' == TYPE:
    AGENTS = (2,3)
    DEPTH = (2,3)
    FLUENTS = list(map(Literal, 'pqr'))
    FLUENT_RANGE = (2,3)
    RMLS = (3,8)

elif 'normal' == TYPE:
    AGENTS = (3,6)
    DEPTH = (4,7)
    FLUENTS = list(map(Literal, 'pqrst'))
    FLUENT_RANGE = (3,5)
    RMLS = (13,39)

elif 'big' == TYPE:
    AGENTS = (3,10)
    DEPTH = (3,10)
    FLUENTS = list(map(Literal, 'pqrstvwxyz'))
    FLUENT_RANGE = (5,10)
    RMLS = (50,150)

else:
    assert False, "Bad experiment type: %s" % TYPE

def now():
    return time.time()


def doit():

    skip_ag = 0
    skip_dep = 0

    if skip_ag == 0 and skip_dep == 0:
        write_file('aamas.csv', 'agents,depth,fluents,inf-size,closed-size,reduced-size,inf-query,closed-query,reduced-query,inf-update,closed-update,reduced-update')

    for ag in range(AGENTS[0], AGENTS[1]+1):
        for dep in range(DEPTH[0], DEPTH[1]+1):

            if ag < skip_ag:
                continue
            elif ag == skip_ag and dep < skip_dep:
                continue

            print()
            print("--------------")
            print("   %d x %d" % (ag, dep))
            print("--------------")
            (times, sizes) = get_size_and_time(ag, dep, FLUENTS)
            print()
            print("-------------------------")

            append_file('aamas.csv', "\n%d,%d,%d,%f,%f,%f,%f,%f,%f,%f,%f,%f" % (ag, dep, len(FLUENTS), sizes[0], sizes[1], sizes[2], times[0], times[1], times[2], times[3], times[4], times[5]))

    #csv = ['agents,depth,fluents,reduced-rmls,closed-rmls,inf-size,closed-size,reduced-size,inf-pre,closed-pre,inf-query,closed-query,reduced-query,result']
    #csv_yes = [csv[0]]
    #csv_no = [csv[0]]

    #kbs.append(random_pdkb(random.randint(DEPTH[0], DEPTH[1]),
    #                               random.randint(AGENTS[0], AGENTS[1]),
    #                               FLUENTS[:random.randint(FLUENT_RANGE[0], FLUENT_RANGE[1])],
    #                               random.randint(RMLS[0], RMLS[1]),
    #                               False))

    #write_file('aamas.csv', csv)
    #write_file('aamas-no.csv', csv_no)
    #write_file('aamas-yes.csv', csv_yes)
    #write_file('aamas-all.csv', csv_yes + csv_no[1:])

def get_size_and_time(num_agents, depth, fluents):

    agents = list(range(1, num_agents + 1))

    def generate_kbs():
        numRMLs = num_agents * depth * 2
        closed_kb = PDKB(depth, agents, fluents)
        indexed_kb = IndexedPDKB(depth, agents, fluents)
        count = 0
        while count < numRMLs:
            next_rml = random_rml(depth, agents, fluents)
            if not closed_kb.query(neg(next_rml)):
                closed_kb.add_rml(next_rml)
                indexed_kb.expand(set([next_rml]))
                count += 1

        inf_kb = INF.PDKB2INF(closed_kb)
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
        ans1 = infs_kb.query(rml)
        inf_query = now() - start
        start = now()
        #ans2 = rml in closed_kbs[index].rmls
        ans2 = closed_kb.query(rml)
        closed_query = now() - start
        start = now()
        ans3 = indexed_kb.query(rml)
        unclosed_query = now() - start

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
        unclosed_update = now() - start

        return (ans1, ans2, ans3, inf_query, closed_query, unclosed_query, inf_update, closed_update, unclosed_update)

    #print "Performing random misc queries..."
    for i in range(NUM_PDKBS):
    #for i in range(0):
        (infs_kb, closed_kb, unclosed_kb) = generate_kbs()
        for j in range(QUERIES_PER_PDKB):

            rml = random_rml(closed_kb.depth, closed_kb.agents, closed_kb.props)
            (ans1, ans2, ans3, inf_query, closed_query, unclosed_query, inf_update, closed_update, unclosed_update) = run_queries(i, rml, infs_kb, closed_kb, unclosed_kb)
            #(inf_update, closed_update, unclosed_update) =

            #csv.append("%d,%d,%d,%d,%d,%d,%d,%d,%f,%f,%f,%f,%f,%s" %
            #           (len(kbs[i].agents), kbs[i].depth, len(kbs[i].props), len(kbs[i].rmls), len(closed_kbs[i].rmls), infs[i].size(), closed_kbs[i].size(), kbs[i].size(),
            #            inf_time[i], closure_time[i], inf_query, closed_query, unclosed_query, str(ans1)))

    print("Performing random successful queries...")
    times = [0.0,0.0,0.0,0.0,0.0,0.0]
    for i in range(NUM_PDKBS):

        (infs_kb, closed_kb, unclosed_kb) = generate_kbs()

        for j in range(QUERIES_PER_PDKB):

            # Get a random RML from the PDKB
            rml = random.choice(list(closed_kb.rmls))
            # Get the closed set
            #entailed = list(kd_closure(rml))
            # Pick a random element
            #rml = random.choice(entailed)
            #(infs_kb, closed_kb, unclosed_kb) = generate_kbs()
            (ans1, ans2, ans3, inf_query, closed_query, unclosed_query, inf_update,  closed_update, unclosed_update) = run_queries(i, rml, infs_kb, closed_kb, unclosed_kb)

            assert ans1 == ans2
            assert ans2 == ans3

            times[0] += inf_query
            times[1] += closed_query
            times[2] += unclosed_query
            times[3] += inf_update
            times[4] += closed_update
            times[5] += unclosed_update

            #csv_yes.append("%d,%d,%d,%d,%d,%d,%d,%d,%f,%f,%f,%f,%f,%s" %
            #               (len(kbs[i].agents), kbs[i].depth, len(kbs[i].props), len(kbs[i].rmls), len(closed_kbs[i].rmls), infs[i].size(), closed_kbs[i].size(), kbs[i].size(),
            #                inf_time[i], closure_time[i], inf_query, closed_query, unclosed_query, str(ans1)))

    sizes = [0.0, 0.0, 0.0]
    print("Performing random unsuccessful queries...")
    for i in range(NUM_PDKBS):

        (infs_kb, closed_kb, unclosed_kb) = generate_kbs()

        sizes[0] += infs_kb.size()
        sizes[1] += closed_kb.size()
        sizes[2] += unclosed_kb.size()

        for j in range(QUERIES_PER_PDKB):


            going = True
            while going:
                rml = random_rml(closed_kb.depth, closed_kb.agents, closed_kb.props)
                if rml not in closed_kb.rmls:
                    going = False
            (ans1, ans2, ans3, inf_query, closed_query, unclosed_query, inf_update, closed_update, unclosed_update) = run_queries(i, rml, infs_kb, closed_kb, unclosed_kb)

            assert ans1 == ans2
            assert ans2 == ans3

            times[0] += inf_query
            times[1] += closed_query
            times[2] += unclosed_query
            times[3] += inf_update
            times[4] += closed_update
            times[5] += unclosed_update


            #csv_no.append("%d,%d,%d,%d,%d,%d,%d,%d,%f,%f,%f,%f,%f,%s" %
            #              (len(kbs[i].agents), kbs[i].depth, len(kbs[i].props), len(kbs[i].rmls), len(closed_kbs[i].rmls), infs[i].size(), closed_kbs[i].size(), kbs[i].size(),
            #               inf_time[i], closure_time[i], inf_query, closed_query, unclosed_query, str(ans1)))


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

    data = load_CSV(filename)[1:]

    for row in data:
        for i in range(len(row)):
            if row[i] == '0.000000':
                row[i] = '0.000001'

    def plot_data(data, inds, labs, cols, zlabel, fname):

        data_map = {}
        for ag in range(AGENTS[0], AGENTS[1]+1):
            data_map[ag] = {}
            for dep in range(DEPTH[0], DEPTH[1]+1):
                data_map[ag][dep] = {}

        for row in data:
            data_map[int(row[0])][int(row[1])][inds[0]] = float(row[inds[0]])
            data_map[int(row[0])][int(row[1])][inds[1]] = float(row[inds[1]])
            data_map[int(row[0])][int(row[1])][inds[2]] = float(row[inds[2]])

        from mpl_toolkits.mplot3d import axes3d
        import matplotlib.pyplot as plt
        import matplotlib
        import numpy as np

        X, Y = np.meshgrid(np.arange(AGENTS[0], AGENTS[1]+1), np.arange(DEPTH[0], DEPTH[1]+1))

        #zs0 = np.array([1 for x,y in zip(np.ravel(X), np.ravel(Y))])
        #zs1 = np.array([data_map[x][y][ind1] / data_map[x][y][indnorm] for x,y in zip(np.ravel(X), np.ravel(Y))])
        #zs2 = np.array([data_map[x][y][ind2] / data_map[x][y][indnorm] for x,y in zip(np.ravel(X), np.ravel(Y))])

        zs0 = np.array([data_map[x][y][inds[0]] for x,y in zip(np.ravel(X), np.ravel(Y))])
        zs1 = np.array([data_map[x][y][inds[1]] for x,y in zip(np.ravel(X), np.ravel(Y))])
        zs2 = np.array([data_map[x][y][inds[2]] for x,y in zip(np.ravel(X), np.ravel(Y))])

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        if 'Query Time ($log_e(sec)$)' == zlabel or 'Update Time ($log_e(sec)$)' == zlabel:
           print("za = " + str(zs0))
           Z0 = np.log(zs0).reshape(X.shape)
           print("Z0 = " + str(Z0))
           Z1 = np.log(zs1).reshape(X.shape)
           Z2 = np.log(zs2).reshape(X.shape)
        else:
            #ax.set_zticks([])
            Z0 = (zs0 / 1000).reshape(X.shape)
            Z1 = (zs1 / 1000).reshape(X.shape)
            Z2 = (zs2 / 1000).reshape(X.shape)

        #ax.plot_wireframe(X, Y, Z0, color='0.75')
        ax.plot_wireframe(X, Y, Z0, color=cols[0])
        ax.plot_wireframe(X, Y, Z1, color=cols[1])
        ax.plot_wireframe(X, Y, Z2, color=cols[2])

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
        ax.legend([scatter1_proxy, scatter2_proxy, scatter3_proxy], [labs[0], labs[1], labs[2]], numpoints = 1)

        ax.get_xaxis().set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
        ax.get_yaxis().set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))

        plt.show()


    col1 = '#1b9e77'
    col2 = '#d95f02'
    col3 = '#7570b3'

    print("Plotting query time...")
    plot_data(data, [6, 8, 7], ['INF', '$V_{RML}$', 'Closure'], [col1, col3, col2], 'Query Time ($log_e(sec)$)', 'time.eps')

    print("Plotting size...")
    plot_data(data, [4, 3, 5], ['Closure', 'INF', '$V_{RML}$'], [col2, col1, col3], 'Size (x1000)', 'size.eps')

    print("Plotting update time...")
    plot_data(data, [9, 11, 10], ['INF', '$V_{RML}$', 'Closure'], [col1, col3, col2], 'Update Time ($log_e(sec)$)', 'update_time.eps')



