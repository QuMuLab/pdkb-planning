
import csv, os, pprint, re, sys

if 3 != len(sys.argv):
    print("\n\tUsage: python3 analyze.py <csv file> <domain>\n")
    exit(0)

with open(sys.argv[1]) as f:
    csvdata = list(csv.DictReader(f, delimiter=','))

data = {
    'corridor-doxastic': {},
    'grapevine-doxastic': {},
    'grid-doxastic': {}
}

def extract_nfluents(dom, prob):
    print("\n")
    print(prob)
    fname = "EVAL-OUTPUT/%s/%s/pdkb-plan.out" % (dom, prob.split('.')[0])
    if not os.path.isfile(fname):
        return -1
    with open(fname, 'r') as f:
        res = re.search(r'#Fluents: ([0-9]+)\n', f.read(), re.MULTILINE)
        if res:
            fluents = int(res.group(1))
        else:
            fluents = -1
    print (fluents)
    return fluents

for r in csvdata:
    dom = r['Problem'].split('/')[2]
    prob = '/'.join(r['Problem'].split('/')[3:])
    data[dom][prob] = r
    # data[dom][prob]['Fluents'] = extract_nfluents(dom, prob)

print()

if sys.argv[2] == 'corridor':
    print("\t{ Corridor Data }\n")

    prob_name_list = ["prob_%d_%d.pdkbddl" % (depth, agents) for depth in [1,3,5] for agents in [3,5,7]]
    for prob_name in prob_name_list:
        prob = data['corridor-doxastic'][prob_name]
        print("%d & %d & %d & %d & %.2f & %.2f & %.2f & %.2f \\\\" % \
               (int(prob['Agents']),
                int(prob['Depth']),
                int(prob['Fluents']),
                # int(prob['Old Plan Length']),
                int(prob['Plan Length']),
                float(prob['Old Planning Time']),
                float(prob['Planning Time']),
                float(prob['Preprocess Time']),
                float(prob['Total Time'])))


elif sys.argv[2] == 'grapevine':
    print("\t{ Grapevine Data }\n")

    prob_name_list = ["prob-%dag-%dg-%dd.pdkbddl" % (agents, goals, depth) \
        for agents in [4,8] for depth in [1,2] for goals in [2,4,8]]
    for prob_name in prob_name_list:
        prob = data['grapevine-doxastic'][prob_name]
        goals = prob_name.split('-')[2][:-1]
        print("%d & %s & %d & %d & %d & %d & %.2f & %.2f & %.2f & %.2f \\\\" % \
               (int(prob['Agents']),
                goals,
                int(prob['Depth']),
                int(prob['Fluents']),
                int(prob['Old Plan Length']),
                int(prob['Plan Length']),
                float(prob['Old Planning Time']),
                float(prob['Planning Time']),
                float(prob['Preprocess Time']),
                float(prob['Total Time'])))

elif sys.argv[2] == 'grid':
    print("\t{ Grid Data }\n")

    print(data['grid-doxastic'].keys())
    scenario_index = 0
    for scenario in ['nonEpGoal', 'EpGoal', 'broadcastCommunication', 'NonbroadcastCommunication', 'blockedCells']:
        scenario_index += 1
        scenario_name = {
            'blockedCells': 'blocked',
            'broadcastCommunication': 'broad',
            'EpGoal': 'epgoal',
            'NonbroadcastCommunication': '!broad',
            'nonEpGoal': '!epgoal'
        }[scenario]

        # First should contain the scenario number
        # print(scenario_index, end='')

        for prob_num in range(1,5):
            prob = data['grid-doxastic']["%s/prob%d.pdkbddl" % (scenario, prob_num)]
            if prob_num == 4:
                spacing = '[2mm]'
            else:
                spacing = ''
            print("%s: %d & %d & %d & %d & %d & %.2f & %.2f & %.2f & %.2f \\\\%s" % \
               (scenario_name, prob_num,
                int(prob['Agents']),
                int(prob['Fluents']),
                int(prob['Old Plan Length']),
                int(prob['Plan Length']),
                float(prob['Old Planning Time']),
                float(prob['Planning Time']),
                float(prob['Preprocess Time']),
                float(prob['Total Time']),
                spacing))



else:
    print("Unrecognized domain: %s" % sys.argv[2])

print()
