import glob
import os

domains = [
    'examples/planning/bw4t/EpGoal',
    'examples/planning/bw4t/NonbroadcasrCommunication',
    'examples/planning/bw4t/nonEpGoal',
    'examples/planning/bw4t/broadcastCommunication',
    'examples/planning/bw4t/blockedCells',

    'examples/planning/corridor',
    'examples/planning/grapevine',
    'examples/planning/thief/prob-paper1.pdkbddl',
    'examples/planning/hattari/problem.pdkbddl',

    'examples/planning/grid/EpGoal',
    'examples/planning/grid/NonbroadcastCommunication',
    'examples/planning/grid/nonEpGoal',
    'examples/planning/grid/broadcastCommunication',
    'examples/planning/grid/blockedCells',
]

valid_file_names = ['prob1', 'prob2', 'prob3', 'prob4',
                    'prob-depth1', 'prob-depth2','prob-depth3',
                    'prob-paper1',  'prob-paper2',  'prob-paper3',
                    'problem', 'problem-single']

commands = [
    ('module', "python3 -m pdkb.planner {} --keep-files"),
]

keepfiles = ("pdkb-plan.out", "pdkb-plan.out.err", "pdkb-plan.txt", "pdkb-problem.pddl", "pdkb-domain.pddl")

for command_set, command in commands:
    for domain in domains:
        pdkbddls = glob.glob(os.path.join(domain, '*.pdkbddl'))
        for pdkbddl in pdkbddls:
            filename = os.path.basename(pdkbddl)
            problem_base = filename.split('.pdkbddl')[0]
            dirname = domain
            if problem_base in valid_file_names:
                print(pdkbddl)
                print(command.format(pdkbddl))
                os.system(command.format(pdkbddl))
                output_dir_name = "output/{}/{}/{}".format(command_set, domain, problem_base)
                os.makedirs(output_dir_name, exist_ok=True)
                for keepfile in keepfiles:
                    if os.path.exists(keepfile):
                        os.rename(keepfile, os.path.join(output_dir_name, keepfile))
