import copy 
import numpy as np
import random as rd
import time as t
from math import *
from itertools import combinations, product
from math import exp, comb 
from typing import List, Tuple
from eternity_puzzle import EternityPuzzle
from collections import deque

####################
##   CONSTANTES   ##
####################

GRAY = 0
NORTH = 0
SOUTH = 1
WEST = 2
EAST = 3

####################
##   PARAMETRES   ##
####################

# Affichage
LOG = True

# Tabu Search
TABU_MAX_ITER_WITHOUT_UPGRADE = 1000
TABU_LENGTH = 10
TABU_RATIO = 0.1

# Main Algo
K = 500 # Nombre de greedy dans la phase 1
M = 3 # Nombre d'iterration sans nouveau meilleur solver avant de changer les ratios

CONFLICT_RATIO = 0.8 # Ratio des pièces avec conflits retirés entre chaque essai
UNCONFLICT_RATIO = 0.1 # Ratio des pièces sans conflits retirés entre chaque essai
RATIO_TRESHOLD = 0.4 # Limite de UNCONFLICT_RATIO avant de rebasculer en phase 1

START_TIME = None

####################
##   Main Algo    ##
####################
# def solve_advanced(puzzle : EternityPuzzle):

    

#     start = t.time()
#     for _ in range(1000):
#         solver = Solver(puzzle)
#         solver.greedy()

#     print(t.time()- start)
#     s = solver.format()
#     return s, puzzle.get_total_n_conflict(s)


# def solve_advanced(puzzle : EternityPuzzle):
#     global START_TIME
#     START_TIME = t.time()

#     solver = Solver(puzzle)
#     solver = best_of_K_greedy(puzzle, 1000, solver)
#     best = [copy.deepcopy(solver), puzzle.get_total_n_conflict(solver.format())]
#     print(best[1])

#     while (t.time() - START_TIME) < solver.T:
        
#         solver.destruction(0.8, 0.4)
#         solver = best_of_K_greedy(puzzle, 100, solver)

#         value = puzzle.get_total_n_conflict(solver.format())
#         print(value)
#         if value < best[1]:
#             print("record !")
#             print(value)
#             best = [copy.deepcopy(solver), value]

#     solver = best[0]
#     s = solver.format()
#     return s, puzzle.get_total_n_conflict(s)


def solve_advanced(puzzle : EternityPuzzle):
    # Seeding 
    # r = 241212
    # print(f'Seed: {r}\n')
    # rd.seed(r)      

    # Initialisation
    solver = Solver(puzzle)
    global UNCONFLICT_RATIO
    global START_TIME
    START_TIME = t.time()

    print("SOLVER\n")

    best_solvers = []

    it = 0
    while (t.time() - START_TIME) < solver.T:
        it += 1
        print(f"\nTemps écoulé {t.time() - START_TIME}\n")
        # Phase 1
        solver = phase_1(puzzle, solver)
        unconflict_ratio = UNCONFLICT_RATIO
        conflict_ratio = CONFLICT_RATIO
        while unconflict_ratio <= RATIO_TRESHOLD:
            print(f"\nValeur de UNCONFLICT_RATIO : {unconflict_ratio}\n")
            # Boucle sur la Phase 2
            best = [copy.deepcopy(solver), np.inf]
            iter_without_upgrade = 0
            while iter_without_upgrade < M:
                # Phase 2
                solver = phase_2(puzzle, solver, conflict_ratio, unconflict_ratio)
        
                # Mise à jour du meilleur solver
                value = puzzle.get_total_n_conflict(solver.format())
                if value < best[1]:
                    iter_without_upgrade = 0
                    best = [copy.deepcopy(solver), value]
                else: iter_without_upgrade += 1
            
            # On retourne sur le meilleur solver
            solver = copy.deepcopy(best[0])
            best_solvers.append(best)
            
            # Update des ratios
            unconflict_ratio += 0.05
        

    # print(best_solvers)
    # Retour de la solution
    solver = sorted(best_solvers, key=lambda x: x[1])[0][0]
    s = solver.format()
    return s, puzzle.get_total_n_conflict(s)


################################################################################################################
##################                               GLOBAL FONCTION                              ##################
################################################################################################################

def phase_1(puzzle, solver):
    print("Phase 1")
    solver = Solver(puzzle)
    solver = best_of_K_greedy(puzzle, K, solver)
    print(f"Valeur après greedy : {puzzle.get_total_n_conflict(solver.format())}")

    solver.tabu_search()
    print(f"Valeur après tabu : {puzzle.get_total_n_conflict(solver.format())}")

    return solver

def phase_2(puzzle: EternityPuzzle, solver, conflict_ratio, unconflict_ratio):
    print("\nPhase 2")

    solver.destruction(conflict_ratio, unconflict_ratio)

    solver = best_of_K_greedy(puzzle, int(K/2), solver)
    print(f"Valeur après greedy : {puzzle.get_total_n_conflict(solver.format())}")

    solver.tabu_search()    
    print(f"Valeur après tabu : {puzzle.get_total_n_conflict(solver.format())}")


    return solver


def best_of_K_greedy(puzzle: EternityPuzzle, K, curr_solver):
    best_value = np.inf
    best_solver = curr_solver
    
    for i in range(K):
        # On part du solver courant
        solver = Solver(puzzle)
        solver.board = copy.deepcopy(curr_solver.board)
        solver.board_pieces = copy.deepcopy(curr_solver.board_pieces)
        solver.used_pieces = copy.deepcopy(curr_solver.used_pieces)
        
        # Greedy sur le solveur courant
        solver.greedy()

        # Mise à jour du meilleur solver
        value = puzzle.get_total_n_conflict(solver.format())
        if value < best_value:
            best_value = value
            best_solver = copy.deepcopy(solver)

    return best_solver


################################################################################################################
##################                               Solver Class                                 ##################
################################################################################################################

class Solver:
    def __init__(self, puzzle: EternityPuzzle):
        """ Initialise le solver sur l'instance puzzle """

        # Général
        self.puzzle = puzzle
        self.n = puzzle.board_size
        self.size = self.n ** 2
        self.startTime = t.time()
        self.T = 3600
        
        # Ensembles de pièces
        self.pieces = puzzle.piece_list
        self.corner_pieces = [piece for piece in self.pieces if piece.count(0) == 2]
        self.edge_pieces = [piece for piece in self.pieces if piece.count(0) == 1]
        self.border_pieces = [piece for piece in self.pieces if piece.count(0) >= 1]
        self.inner_pieces = [piece for piece in self.pieces if piece.count(0) == 0]

        # Ensembles de cases
        self.corner_cells = [(0, 0), (self.n - 1, 0), (0, self.n - 1), (self.n - 1, self.n - 1)]
        self.edge_cells = [(x, y) for x in range(self.n) for y in range(self.n) if (x in [0, self.n - 1] or y in [0, self.n - 1]) and (x, y) not in self.corner_cells]
        self.border_cells = [(x, y) for x in range(self.n) for y in range(self.n) if x == 0 or x == self.n - 1 or y == 0 or y == self.n - 1]
        self.inner_cells = [(x, y) for x in range(1, self.n - 1) for y in range(1, self.n - 1)]
        self.cells = [(x, y) for x in range(self.n) for y in range(self.n )]

        # Représentation de la solution actuelle
        self.board = {(x, y): None for (x,y) in self.cells}
        self.board_pieces = {(x, y): None for (x,y) in self.cells}

        # Utiles
        self.used_pieces = []
        self.all_rotations = {p: puzzle.generate_rotation(p) for p in self.pieces}
        self.all_config = set([self.all_rotations[p][i] for p in self.pieces for i in range(4)])
        self.best_sol = [None, np.inf]
        self.best_sols = []

    

    ################################################################################################################
    ##################                                   GREEDY                                   ##################
    ################################################################################################################

    def greedy(self):
        """ Construit une solution greedy diagonales par diagonales """
        rd.shuffle(self.corner_pieces)
        rd.shuffle(self.edge_pieces)
        rd.shuffle(self.inner_pieces)

        for s in range(2*self.n - 1):  # s = i + j
            for x in range(s, -1, -1):  # i descend
                y = s - x
                if x < self.n and y < self.n:
                    if self.board[(x,y)] == None:
                        p, o, _ = self.greedy_best_piece(x, y)
                        self.place_piece(x, y, p, o, 1)  
                         
    
    def greedy_best_piece(self, x, y):
        """ Renvoie la pièce non encore utilié qui engendre le moins de conflits en (x, y) """
        pieces = self.set_of_valid_pieces(x, y)
        best = [None, None, np.inf]

        for p in pieces:
            if p in self.used_pieces:
                continue  
            for o in self.all_rotations[p]:
                value = self.total_conflict_of_o(x, y, o)
                if value < best[2]:
                    best = [p, o, value]
                if value == 0:
                    return best
                
        return best
    

    ################################################################################################################
    ##################                                TABU SEARCH                                 ##################
    ################################################################################################################

    def tabu_search(self):
        # Sortir si on a plus de temps
        if (t.time() - START_TIME) > self.T:
                return 
        
        # Initialisation
        tabu_list = deque(maxlen=TABU_LENGTH)
        value = self.puzzle.get_total_n_conflict(self.format())
        best = [copy.deepcopy(self.board), copy.deepcopy(self.board_pieces), copy.deepcopy(self.used_pieces), value]
        iter = 0
        iter_without_upgrade = 0

        while (t.time() - START_TIME) < self.T and iter_without_upgrade < TABU_MAX_ITER_WITHOUT_UPGRADE:
            iter += 1 
            iter_without_upgrade += 1
            
            # Voisinage
            neighbors = self.tabu_neighbors_border(value, tabu_list, best[3]) + self.tabu_neighbors_inner(value, tabu_list, best[3])
            neighbors.sort(key=lambda x: x[2])

            if len(neighbors) == 0:
                print("no neigh")
                continue
            
            # Mise à jour de la solution courrante
            neigh = neighbors[0]
            value = neigh[2]
            type = neighbors[0][3]
            x1, y1, p1, o1 = neigh[0] 
            x2, y2, p2, o2 = neigh[1]

            if type == "2-Swap":
                self.place_piece(x1, y1, p1, o1, 0)
                self.place_piece(x2, y2, p2, o2, 0)
                tabu_list.append((x1, y1, p1, o1, x2, y2, p2, o2))
            
            if type == "Rot":
                self.place_piece(x1, y1, p1, o1, 0)
                tabu_list.append((x1, y1, p1, o1))

            # Debug
            if not self.puzzle.verify_solution(self.format()):
                print("INV")
                print(value, self.puzzle.get_total_n_conflict(self.format()))
                print(neigh)
                return

            if value != self.puzzle.get_total_n_conflict(self.format()):
                print(value, self.puzzle.get_total_n_conflict(self.format()))
                print(neigh)

            # Mise à jour de la meilleure solution
            if value < best[3]:
                iter_without_upgrade = 0
                best = [copy.deepcopy(self.board), copy.deepcopy(self.board_pieces), copy.deepcopy(self.used_pieces), value]
                # print(value)

            # Condition de succès
            if value == 0:
                break
            

        # On retourne sur la meilleure solution
        self.board = best[0]
        self.board_pieces = best[1]
        self.used_pieces = best[2]
        return
    
    def tabu_neighbors_inner(self, value, tabu_list, best_value):
        # Initialisation
        neighbors = []

        # Parcours du voisinage d'intérieur
        n = len(self.inner_cells)
        for i in range(n):
            # Sortir si on a plus de temps
            if (t.time() - START_TIME) > self.T:
                return neighbors
            
            x1, y1 = self.inner_cells[i]

            # Rotation d'une pièce
            if rd.random() < TABU_RATIO:
                p1 = self.board_pieces[(x1, y1)]
                old_o1 = self.board[(x1, y1)]
                
                for new_o1 in self.all_rotations[p1]:
                    if new_o1 != old_o1:
                        old_conflicts = self.total_conflict_of_o(x1, y1, old_o1)
                        new_conflicts = self.total_conflict_of_o(x1, y1, new_o1)
                        delta = new_conflicts - old_conflicts

                        if value + delta < best_value or (x1, y1, p1, new_o1) not in tabu_list:
                            neighbors.append([(x1, y1, p1, new_o1), (x1, y1, p1, new_o1), value + delta, "Rot"])

            for j in range(i + 1, n):
                # Sortir si on a plus de temps
                if (t.time() - START_TIME) > self.T:
                    return neighbors
                
                x2, y2 = self.inner_cells[j]

                # Swap 2 sans rotation
                if rd.random() <= TABU_RATIO:
                    p1 = self.board_pieces[(x1, y1)]
                    old_o1 = self.board[(x1, y1)]
                    p2 = self.board_pieces[(x2, y2)]
                    old_o2 = self.board[(x2, y2)]

                    
                    if x1 == x2 or y1 == y2:
                        old_conflicts = self.total_conflict_of_o(x1, y1, old_o1) + self.total_conflict_of_o(x2, y2, old_o2) - self.correction_double_conflicts(x1, y1, old_o1, x2, y2, old_o2)
                        self.place_piece(x1, y1, p2, old_o2, 0)
                        self.place_piece(x2, y2, p1, old_o1, 0)
                        new_conflicts = self.total_conflict_of_o(x1, y1, old_o2) + self.total_conflict_of_o(x2, y2, old_o1) - self.correction_double_conflicts(x1, y1, old_o2, x2, y2, old_o1)
                        self.place_piece(x1, y1, p1, old_o1, 0)
                        self.place_piece(x2, y2, p2, old_o2, 0)
                    else:
                        old_conflicts = self.total_conflict_of_o(x1, y1, old_o1) + self.total_conflict_of_o(x2, y2, old_o2)
                        new_conflicts = self.total_conflict_of_o(x1, y1, old_o2) + self.total_conflict_of_o(x2, y2, old_o1)
                    delta = new_conflicts - old_conflicts
                    
                    if value + delta < best_value or (x1, y1, p2, old_o2, x2, y2, p1, old_o1) not in tabu_list:
                        neighbors.append([(x1, y1, p2, old_o2), (x2, y2, p1, old_o1), value + delta, "2-Swap"])

        return neighbors

    def tabu_neighbors_border(self, value, tabu_list, best_value):
        # Initialisation
        neighbors = []

        # Parcours du voisinage de cotés
        for (x1, y1), (x2, y2) in combinations(self.edge_cells, 2):
            # Sortir si on a plus de temps
            if (t.time() - START_TIME) > self.T:
                return neighbors

            # TODO Verifier condition tabu et random et aspiration ?
            # if tabu_dict[(x1, y1, x2, y2)] >= iter or rd.random() > BORDER_RATIO_VOISINS:
            #     continue

            p1 = self.board_pieces[x1, y1]
            old_o1 = self.board[x1, y1]
            p2 = self.board_pieces[x2, y2]
            old_o2 = self.board[x2, y2]

            for o in self.all_rotations[p1]:
                if self.fits_border(x2, y2, o):
                    new_o1 = o
                    break
            for o in self.all_rotations[p2]:
                if self.fits_border(x1, y1, o):
                    new_o2 = o
                    break
            
            if x1 == x2 or y1 == y2:
                old_conflicts = self.total_conflict_of_o(x1, y1, old_o1) + self.total_conflict_of_o(x2, y2, old_o2) - self.correction_double_conflicts(x1, y1, old_o1, x2, y2, old_o2)
                self.place_piece(x1, y1, p2, new_o2, 0)
                self.place_piece(x2, y2, p1, new_o1, 0)
                new_conflicts = self.total_conflict_of_o(x1, y1, new_o2) + self.total_conflict_of_o(x2, y2, new_o1) - self.correction_double_conflicts(x1, y1, new_o2, x2, y2, new_o1)
                self.place_piece(x1, y1, p1, old_o1, 0)
                self.place_piece(x2, y2, p2, old_o2, 0)
            else:
                old_conflicts = self.total_conflict_of_o(x1, y1, old_o1) + self.total_conflict_of_o(x2, y2, old_o2)
                new_conflicts = self.total_conflict_of_o(x1, y1, new_o2) + self.total_conflict_of_o(x2, y2, new_o1)
            delta = new_conflicts - old_conflicts

            if value + delta < best_value or (x1, y1, p2, new_o2, x2, y2, p1, new_o1) not in tabu_list:
                neighbors.append([(x1, y1, p2, new_o2), (x2, y2, p1, new_o1), value + delta, "2-Swap", "WSH"])

        # Parcours de voisinage de coins
        for (x1, y1), (x2, y2) in combinations(self.corner_cells, 2):
            # Sortir si on a plus de temps
            if (t.time() - START_TIME) > self.T:
                return neighbors

            # TODO Verifier condition tabu et random et aspriration ?
            # if tabu_dict[(x1, y1, x2, y2)] >= iter or rd.random() > BORDER_RATIO_VOISINS:
            #     continue

            p1 = self.board_pieces[x1, y1]
            old_o1 = self.board[x1, y1]
            p2 = self.board_pieces[x2, y2]
            old_o2 = self.board[x2, y2]

            for o in self.all_rotations[p1]:
                if self.fits_border(x2, y2, o):
                    new_o1 = o
                    break
            for o in self.all_rotations[p2]:
                if self.fits_border(x1, y1, o):
                    new_o2 = o
                    break
            
            if x1 == x2 or y1 == y2:
                old_conflicts = self.total_conflict_of_o(x1, y1, old_o1) + self.total_conflict_of_o(x2, y2, old_o2) - self.correction_double_conflicts(x1, y1, old_o1, x2, y2, old_o2)
                self.place_piece(x1, y1, p2, new_o2, 0)
                self.place_piece(x2, y2, p1, new_o1, 0)
                new_conflicts = self.total_conflict_of_o(x1, y1, new_o2) + self.total_conflict_of_o(x2, y2, new_o1) - self.correction_double_conflicts(x1, y1, new_o2, x2, y2, new_o1)
                self.place_piece(x1, y1, p1, old_o1, 0)
                self.place_piece(x2, y2, p2, old_o2, 0)
            else:
                old_conflicts = self.total_conflict_of_o(x1, y1, old_o1) + self.total_conflict_of_o(x2, y2, old_o2) 
                new_conflicts = self.total_conflict_of_o(x1, y1, new_o2) + self.total_conflict_of_o(x2, y2, new_o1) 
            delta = new_conflicts - old_conflicts

            neighbors.append([(x1, y1, p2, new_o2), (x2, y2, p1, new_o1), value + delta, "2-Swap", "OLALA"])

        return neighbors


    ################################################################################################################
    ##################                                   DESTRUCTION                              ##################
    ################################################################################################################

    def destruction(self, conflict_ratio, unconflict_ratio):
        conflict_pieces, unconflict_pieces = self.find_conflict_pieces()

        n_conflict = int(len(conflict_pieces) * conflict_ratio)
        conflict_weights = [c_d["n"] for c_d in conflict_pieces]
        conflict_pieces_to_remove = rd.sample(conflict_pieces, k=n_conflict)
        # conflict_pieces_to_remove = self.weighted_sample_without_replacement(conflict_pieces, conflict_weights ,n_conflict)

        n_unconflict = int(len(unconflict_pieces) * unconflict_ratio)
        unconflict_pieces_to_remove = rd.sample(unconflict_pieces, k=n_unconflict)
        
        for c_d in conflict_pieces_to_remove:
            self.board[c_d["cell"]] = None
            self.board_pieces[c_d["cell"]] = None
            self.used_pieces.remove(c_d["p"])

        for u_d in unconflict_pieces_to_remove:
            self.board[u_d["cell"]] = None
            self.board_pieces[u_d["cell"]] = None
            self.used_pieces.remove(u_d["p"]) 
    
    def weighted_sample_without_replacement(self, items, weights, k):
        weights = np.array(weights, dtype=np.float64)
        weights /= weights.sum()  # normalise les poids
        indices = np.random.choice(len(items), size=k, replace=False, p=weights)
        return [items[i] for i in indices]

    ################################################################################################################
    ##################                                   UTILS                                    ##################
    ################################################################################################################

    def find_conflict_pieces(self):
        
        conflict_pieces, unconflict_pieces = [], []

        for x, y in self.cells:
            p, o = self.board_pieces[(x, y)], self.board[(x, y)]
            nb_conflict = self.total_conflict_of_o(x, y, o)
            if nb_conflict == 0: unconflict_pieces.append({"cell": (x, y), "p": p, "o": o, "n": nb_conflict})
            else: conflict_pieces.append({"cell": (x, y), "p": p, "o": o, "n": nb_conflict})

        return conflict_pieces, unconflict_pieces


    def set_of_valid_pieces(self, x, y):
        """ Renvoie le set de pièces valide pour la case (x, y) """
        if (x, y) in self.corner_cells:
            return self.corner_pieces
        elif (x, y) in self.edge_cells:
            return self.edge_pieces
        else:
            return self.inner_pieces
    
    def total_conflict_of_o(self, x, y, o):
        """ Renvoie le nombre de conflits que l'orientation o cause en (x, y) """
        nb_conflict = 0

        if x-1 < 0: south_col = GRAY
        elif self.board[(x-1, y)] == None: south_col = None
        else: south_col = self.board[(x-1, y)][NORTH]

        if x+1 >= self.n: north_col = GRAY
        elif self.board[(x+1, y)] == None: north_col = None
        else: north_col = self.board[(x+1, y)][SOUTH]
        
        if y-1 < 0: west_col = GRAY
        elif self.board[(x, y-1)] == None: west_col = None
        else: west_col = self.board[(x, y-1)][EAST]

        if y+1 >= self.n: east_col = GRAY
        elif self.board[(x, y+1)] == None: east_col = None
        else: east_col = self.board[(x, y+1)][WEST]

        if south_col != None and south_col != o[SOUTH]: nb_conflict += 1
        if north_col != None and north_col != o[NORTH]: nb_conflict += 1
        if west_col != None and west_col != o[WEST]: nb_conflict += 1
        if east_col != None and east_col != o[EAST]: nb_conflict += 1
        
        return nb_conflict


    def correction_double_conflicts(self, x1, y1, o1, x2, y2, o2):
        if x1 == x2:
            if y1 + 1 == y2:
                if o1[EAST] != o2[WEST]: return 1
            elif y2 + 1 == y1:
                if o1[WEST] != o2[EAST]: return 1
        elif y1 == y2:
            if x1 + 1 == x2:
                if o1[NORTH] != o2[SOUTH]: return 1
            elif x2 + 1 == x1:
                if o1[SOUTH] != o2[NORTH]: return 1
        
        return 0  

    def place_piece(self, x, y, piece, orientation, mode):
        self.board[(x, y)] = orientation
        self.board_pieces[(x, y)] = piece
        if piece not in self.used_pieces:
            self.used_pieces.append(piece)

    def fits_border(self, x, y, oriented):
        return (oriented[SOUTH] == GRAY if x == 0 else True) and \
               (oriented[NORTH] == GRAY if x == self.n - 1 else True) and \
               (oriented[WEST] == GRAY if y == 0 else True) and \
               (oriented[EAST] == GRAY if y == self.n - 1 else True)
    
    def format(self):
        # Construction de la solution en liste plate : ordre "de bas en haut", chaque ligne de gauche à droite.
        flat_solution = [self.board[(x, y)] for (x,y) in self.cells]
        return flat_solution

