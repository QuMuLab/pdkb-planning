import glob, os, re, subprocess, sys, time

AIJ = (len(sys.argv) > 1 and sys.argv[1] == 'AIJ')

domains = [
    'examples/planning/bw4t/EpGoal',
    'examples/planning/bw4t/NonbroadcasrCommunication',
    'examples/planning/bw4t/nonEpGoal',
    'examples/planning/bw4t/broadcastCommunication',
    'examples/planning/bw4t/blockedCells',

    'examples/planning/corridor',
    'examples/planning/corridor-doxastic',
    'examples/planning/grapevine',
    'examples/planning/grapevine-doxastic',
    'examples/planning/thief/prob-paper1.pdkbddl',
    'examples/planning/hattari/problem.pdkbddl',

    'examples/planning/grid/EpGoal',
    'examples/planning/grid/NonbroadcastCommunication',
    'examples/planning/grid/nonEpGoal',
    'examples/planning/grid/broadcastCommunication',
    'examples/planning/grid/blockedCells',

    'examples/planning/grid-doxastic/EpGoal',
    'examples/planning/grid-doxastic/NonbroadcastCommunication',
    'examples/planning/grid-doxastic/nonEpGoal',
    'examples/planning/grid-doxastic/broadcastCommunication',
    'examples/planning/grid-doxastic/blockedCells',
]

if AIJ:
    domains = [
        'examples/planning/corridor-doxastic',
        'examples/planning/grapevine-doxastic',
        'examples/planning/thief/prob-paper1.pdkbddl',
        'examples/planning/hattari/problem.pdkbddl',
        'examples/planning/grid-doxastic/EpGoal',
        'examples/planning/grid-doxastic/NonbroadcastCommunication',
        'examples/planning/grid-doxastic/nonEpGoal',
        'examples/planning/grid-doxastic/broadcastCommunication',
        'examples/planning/grid-doxastic/blockedCells',
    ]

valid_file_names = ['prob1', 'prob2', 'prob3', 'prob4',
                    'prob-paper1',  'prob-paper2',  'prob-paper3',
                    'problem', 'problem-single']

valid_file_names += ["prob_%d_%d" % (num_depth, num_ag) \
                        for num_depth in [1,3,5] \
                        for num_ag in [3,5,7]]

valid_file_names += ["prob-%dag-%dg-%dd" % (num_ag, num_g, num_depth) \
                        for num_ag in [4,8] \
                        for num_g in [2,4,8] \
                        for num_depth in [1,2]]

commands = [
    ('module', "python3 -m pdkb.planner {} --keep-files"),
]

keepfiles = ("pdkb-plan.out", "pdkb-plan.out.err", "pdkb-plan.txt", "pdkb-problem.pddl", "pdkb-domain.pddl")

if AIJ:
    with open("data.csv", 'w') as f:
        f.write("Problem,Preprocess Time,Old Planning Time,Planning Time,Total Time,Old Plan Length,Plan Length,Agents,Fluents,Actions,Effects,Depth")

for command_set, command in commands:
    for domain in domains:
        pdkbddls = glob.glob(os.path.join(domain, '*.pdkbddl'))
        for pdkbddl in pdkbddls:
            filename = os.path.basename(pdkbddl)
            problem_base = filename.split('.pdkbddl')[0]
            dirname = domain
            if problem_base in valid_file_names:
                # print(pdkbddl)
                print(command.format(pdkbddl))

                t0 = time.time()
                try:
                    output = subprocess.check_output(command.format(pdkbddl), shell=True).decode("utf-8")
                    # print(output)
                    planner_t = float(re.search(r'^Plan Time: ([0-9]*\.?[0-9]+)\n', output, re.MULTILINE).group(1))
                    planner_s = int(re.search(r'^Plan Length: ([0-9]+)\n', output, re.MULTILINE).group(1))
                    num_agents = int(re.search(r'^# Agents: ([0-9]+)\n', output, re.MULTILINE).group(1))
                    num_fluents = int(re.search(r'^# Props: ([0-9]+)\n', output, re.MULTILINE).group(1))
                    num_actions = int(re.search(r'^# Acts: ([0-9]+)\n', output, re.MULTILINE).group(1))
                    num_effects = int(re.search(r'^# Effs: ([0-9]+)\n', output, re.MULTILINE).group(1))
                    num_depth = int(re.search(r'^Depth: ([0-9]+)\n', output, re.MULTILINE).group(1))
                except:
                    planner_t = -1.0
                    planner_s = 0
                    num_agents = 0
                    num_fluents = 0
                    num_actions = 0
                    num_effects = 0
                    num_depth = 0

                total_t = time.time() - t0

                if AIJ:
                    try:
                        output2 = subprocess.check_output(command.format(pdkbddl)+' --old-planner', shell=True).decode("utf-8")
                        # print(output)
                        old_planner_t = float(re.search(r'^Plan Time: ([0-9]*\.?[0-9]+)\n', output2, re.MULTILINE).group(1))
                        old_planner_s = int(re.search(r'^Plan Length: ([0-9]+)\n', output2, re.MULTILINE).group(1))
                    except:
                        old_planner_t = -1.0
                        old_planner_s = 0

                    with open("data.csv", 'a') as f:
                        f.write("\n%s,%f,%f,%f,%f,%d,%d,%d,%d,%d,%d,%d" % \
                                (pdkbddl, (total_t-planner_t), old_planner_t, planner_t, total_t, old_planner_s, planner_s, num_agents, num_fluents, num_actions, num_effects, num_depth))

                output_dir_name = "output/{}/{}/{}".format(command_set, domain, problem_base)
                os.makedirs(output_dir_name, exist_ok=True)
                with open(os.path.join(output_dir_name, 'new_solver.out'), 'w') as f:
                    f.write(output)
                with open(os.path.join(output_dir_name, 'old_solver.out'), 'w') as f:
                    f.write(output2)
                for keepfile in keepfiles:
                    if os.path.exists(keepfile):
                        os.rename(keepfile, os.path.join(output_dir_name, keepfile))
