# Polytechnique Montréal - INF6102: Eternity II

This project focuses on solving simplified versions of the Eternity II puzzle, a famously difficult 16×16 edge-matching puzzle. Each tile has a colored pattern on each side and must be placed such that adjacent tiles share the same edge color. Tiles can be rotated, and border edges must match a special "border" color. The task is to design an innovative algorithm using heuristics, local search, or metaheuristics to find high-quality solutions. The main contraint was the time allowed (around 30-60 min).

You can find four solver :
* solver_random.py : a random solver.
* solver_heuristic.py : a basic solver using the following heuristic : solve each crown of the puzzle starting from the border into the center
* solver_local_search.py : a basic local-search solver.
* solver_advanced.py : an advanced implementation using several meta-heuristics, full documentation in the Report PDF.

You can find a clear description of what was expected and how to run in the Assignement PDF and a succint report of my implementation in the Report PDF (both in french).

## How to run

To run a solver on an instance :
```console
$ python main.py --agent=(agent-name).py --infile=./instances/(instance-name).txt
```

