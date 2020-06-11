
import sys


# Universal swaps
swaps = [
    ('(:requirements :strips :conditional-effects)', ''),
    (':precondition', ':category (ontic)\n        :parameters ()\n        :precondition'),
    (':effect (and', ':effect ('),
    ('(:init', '(:init (and'),
    ('(:goal', ')\n\n    (:constraint (True))\n    (:goal'),
    ('(:predicates', '(:objects )\n    (:agents a b c d)\n    (:predicates')
]



# Custom swaps

for ag1 in 'abcd':
    for ag2 in 'abcd':
        swaps.append(("B%s_secret_%s" % (ag1, ag2),
                      "K_%s (secret_%s)" % (ag1, ag2)))
        swaps.append(("B%s_not_secret_%s" % (ag1, ag2),
                      "K_%s (not (secret_%s))" % (ag1, ag2)))
        swaps.append(("P%s_secret_%s" % (ag1, ag2),
                      "DK_%s (secret_%s)" % (ag1, ag2)))
        swaps.append(("P%s_not_secret_%s" % (ag1, ag2),
                      "DK_%s (not (secret_%s))" % (ag1, ag2)))

for ag in 'abcd':
    for loc in ['l1', 'l2', 'l3']:
        swaps.append(("not_at_%s_%s" % (ag, loc),
                      "not (at_%s_%s)" % (ag, loc)))
        swaps.append(("(not (not (at_%s_%s)))" % (ag, loc),
                      "(at_%s_%s)" % (ag, loc)))





# Content swapping and file merging

with open(sys.argv[1], 'r') as f:
    domain_contents = f.read()
with open(sys.argv[2], 'r') as f:
    problem_contents = f.read()

for x,y in swaps:
    domain_contents = domain_contents.replace(x,y)
    problem_contents = problem_contents.replace(x,y)

contents = '\n'.join(domain_contents.split('\n')[:-1] + problem_contents.split('\n')[4:-1] + [')'])

with open(sys.argv[3], 'w') as f:
    f.write(contents)
