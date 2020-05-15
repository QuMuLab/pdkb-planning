#!/usr/bin/env python
import sys
import os

planner_path = os.path.dirname(os.path.abspath(__file__))
planner = planner_path+"/bfws"
domain = sys.argv[1]
problem = sys.argv[2]
plan = sys.argv[3]

cmd1 = "{} --domain {}  --problem {} --output {} --k-M-BFWS 2 --max_novelty 1".format(planner,domain,problem,plan)
cmd2 = "{} --domain {}  --problem {} --output {} --k-M-BFWS 2 --max_novelty 2".format(planner,domain,problem,plan)
cmd3 = "{} --domain {}  --problem {} --output {} --Poly-Seq-BFWS 1".format(planner,domain,problem,plan)

if os.path.exists(plan):
    os.remove(plan)

print("\nSolving w/ staged BFWS configurations...")
for cmd in [cmd1, cmd2, cmd3]:
    if not os.path.exists(plan):
        print(cmd)
        os.system(cmd)
print("Done!\n")