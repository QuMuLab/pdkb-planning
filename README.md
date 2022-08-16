# Multi-agent Epistemic Planning With Proper Doxastic Knowledge Bases #

This repository houses the code for solving Multi-agent Epistemic Planning (MEP) problems using Proper Doxastic Knowledge Bases (PDKB). There are a number of components that may be useful on their own, including [working directing with PDKB's](https://github.com/QuMuLab/PDKB-Planning/blob/master/pdkb/kd45.py?at=default), [augmenting the MEP formalism](https://github.com/QuMuLab/PDKB-Planning/blob/master/pdkb/problems.py?at=default), or even just creating / dealing with [KD45 kripke structures](https://github.com/QuMuLab/PDKB-Planning/blob/master/pdkb/kripke.py?at=default).

Eventually, more documentation will be added to the project, but feel free to [contact me](http://haz.ca/contact.html) if you have any questions. For a demo and more information on the project, [[click here](http://pdkb.haz.ca/)].

## Getting started ##

### Using Docker ###

```sh
docker build -t pdkbplanning:latest .
docker run -it pdkbplanning
```

You end up in a shell running in the Docker container,
which has all the required tools installed.
Then you can run the planner on an example PKDBDDL problem:

```sh
python3 -m pdkb.planner /MEP/pdkb-planning/examples/planning/grapevine/prob-paper1.pdkbddl
```

## Requirements ##
* [Graphviz](http://graphviz.org/)
* [NetworkX](http://networkx.github.io/)
* [Pygraphviz](http://networkx.lanl.gov/pygraphviz/index.html)
