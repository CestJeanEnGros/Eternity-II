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

TEMP_INIT = 100
ALPHA = 0.99
RATIO_NEIGH = 0.1
MAX_ITER = 10000

####################
##   Main Algo    ##
####################

def solve_local_search(puzzle: EternityPuzzle):
    """
    Heuristic solution of the problem
    :param eternity_puzzle: object describing the input
    :return: a tuple (solution, cost) where solution is a list of the pieces (rotations applied) and
        cost is the cost of the solution
    """
    r = 21030923
    print(f'Seed: {r}\n')
    # rd.seed(r)  
    
    solver = Solver(puzzle)
    solver.randomBorder()
    solver.randomInside()
    print(puzzle.get_total_n_conflict(solver.format()))
    solver.simulatedAnnealing()



    s = solver.format()
    return s, puzzle.get_total_n_conflict(s)




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
        self.T = 1200
        
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
    ##################                             Simulated Annealing                            ##################
    ################################################################################################################

    def simulatedAnnealing(self):
        print("Simulated Annealing")
        temp = TEMP_INIT
        ALPHA
        value = self.puzzle.get_total_n_conflict(self.format())

        best = [None, np.inf]

        iter = 0
        iter_without_best = 0
        while (t.time() - self.startTime) < self.T and iter_without_best < MAX_ITER:
            iter += 1 
            iter_without_best += 1
            neighbors = self.sa_neighbors_border(value) + self.sa_neighbors_inner(value)
            neighbors.sort(key=lambda x: x[2])
            neighs = rd.choice(neighbors[:2])
            delta = neighs[2] - best[1]
            if delta < 0:
                x1, y1, p1, o1 = neighbors[0][0] 
                x2, y2, p2, o2 = neighbors[0][1]
                self.place_piece(x1, y1, p1, o1)
                self.place_piece(x2, y2, p2, o2)    
                value = neighs[2]
                print(value)
                iter_without_best = 0
                best = [copy.deepcopy(self.board), neighs[2]]

            elif delta >= 0 and rd.random() < np.exp(-delta/temp):
                x1, y1, p1, o1 = neighbors[0][0] 
                x2, y2, p2, o2 = neighbors[0][1]
                self.place_piece(x1, y1, p1, o1)
                self.place_piece(x2, y2, p2, o2)
                value = neighs[2]

            if value == 0:
                break
            
            temp = ALPHA*temp
            

        self.board = best[0]
        return

    def sa_neighbors_inner(self, value):
        # Initialisation
        neighbors = []

        # Parcours du voisinage d'intérieur
        n = len(self.inner_cells)
        for i in range(n):
            # Sortir si on a plus de temps
            if (t.time() - self.startTime) > self.T:
                return neighbors
            
            x1, y1 = self.inner_cells[i]

            # Rotation d'une pièce
            if rd.random() < RATIO_NEIGH:
                p1 = self.board_pieces[(x1, y1)]
                old_o1 = self.board[(x1, y1)]
                
                for new_o1 in self.all_rotations[p1]:
                    if new_o1 != old_o1:
                        old_conflicts = self.total_conflict_of_o(x1, y1, old_o1)
                        new_conflicts = self.total_conflict_of_o(x1, y1, new_o1)
                        delta = new_conflicts - old_conflicts
          
                        neighbors.append([(x1, y1, p1, new_o1), (x1, y1, p1, new_o1), value + delta, "Rot"])

            for j in range(i + 1, n):
                # Sortir si on a plus de temps
                if (t.time() - self.startTime) > self.T:
                    return neighbors
                
                x2, y2 = self.inner_cells[j]

                # Swap 2 sans rotation
                if rd.random() <= RATIO_NEIGH:
                    p1 = self.board_pieces[(x1, y1)]
                    old_o1 = self.board[(x1, y1)]
                    p2 = self.board_pieces[(x2, y2)]
                    old_o2 = self.board[(x2, y2)]

                    
                    if x1 == x2 or y1 == y2:
                        old_conflicts = self.total_conflict_of_o(x1, y1, old_o1) + self.total_conflict_of_o(x2, y2, old_o2) - self.correction_double_conflicts(x1, y1, old_o1, x2, y2, old_o2)
                        self.place_piece(x1, y1, p2, old_o2)
                        self.place_piece(x2, y2, p1, old_o1)
                        new_conflicts = self.total_conflict_of_o(x1, y1, old_o2) + self.total_conflict_of_o(x2, y2, old_o1) - self.correction_double_conflicts(x1, y1, old_o2, x2, y2, old_o1)
                        self.place_piece(x1, y1, p1, old_o1)
                        self.place_piece(x2, y2, p2, old_o2)
                    else:
                        old_conflicts = self.total_conflict_of_o(x1, y1, old_o1) + self.total_conflict_of_o(x2, y2, old_o2)
                        new_conflicts = self.total_conflict_of_o(x1, y1, old_o2) + self.total_conflict_of_o(x2, y2, old_o1)
                    delta = new_conflicts - old_conflicts
                    
                    neighbors.append([(x1, y1, p2, old_o2), (x2, y2, p1, old_o1), value + delta, "2-Swap"])

        return neighbors

    def sa_neighbors_border(self, value):
        # Initialisation
        neighbors = []

        # Parcours du voisinage de cotés
        for (x1, y1), (x2, y2) in combinations(self.edge_cells, 2):
            # Sortir si on a plus de temps
            if (t.time() - self.startTime) > self.T:
                return neighbors

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
                self.place_piece(x1, y1, p2, new_o2)
                self.place_piece(x2, y2, p1, new_o1)
                new_conflicts = self.total_conflict_of_o(x1, y1, new_o2) + self.total_conflict_of_o(x2, y2, new_o1) - self.correction_double_conflicts(x1, y1, new_o2, x2, y2, new_o1)
                self.place_piece(x1, y1, p1, old_o1)
                self.place_piece(x2, y2, p2, old_o2)
            else:
                old_conflicts = self.total_conflict_of_o(x1, y1, old_o1) + self.total_conflict_of_o(x2, y2, old_o2)
                new_conflicts = self.total_conflict_of_o(x1, y1, new_o2) + self.total_conflict_of_o(x2, y2, new_o1)
            delta = new_conflicts - old_conflicts


            neighbors.append([(x1, y1, p2, new_o2), (x2, y2, p1, new_o1), value + delta, "2-Swap", "WSH", [new_conflicts, old_conflicts, delta]])

        # Parcours de voisinage de coins
        for (x1, y1), (x2, y2) in combinations(self.corner_cells, 2):
            # Sortir si on a plus de temps
            if (t.time() - self.startTime) > self.T:
                return neighbors

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
                self.place_piece(x1, y1, p2, new_o2)
                self.place_piece(x2, y2, p1, new_o1)
                new_conflicts = self.total_conflict_of_o(x1, y1, new_o2) + self.total_conflict_of_o(x2, y2, new_o1) - self.correction_double_conflicts(x1, y1, new_o2, x2, y2, new_o1)
                self.place_piece(x1, y1, p1, old_o1)
                self.place_piece(x2, y2, p2, old_o2)
            else:
                old_conflicts = self.total_conflict_of_o(x1, y1, old_o1) + self.total_conflict_of_o(x2, y2, old_o2) 
                new_conflicts = self.total_conflict_of_o(x1, y1, new_o2) + self.total_conflict_of_o(x2, y2, new_o1) 
            delta = new_conflicts - old_conflicts

            neighbors.append([(x1, y1, p2, new_o2), (x2, y2, p1, new_o1), value + delta, "2-Swap", "OLALA"])

        return neighbors
    

    ################################################################################################################
    ##################                                   UTILS                                    ##################
    ################################################################################################################

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
    
    def homogeneous(self, p1, p2):
        return p1.count(0) == p2.count(0)
    
    def fits_border(self, x, y, oriented):
        return (oriented[SOUTH] == GRAY if x == 0 else True) and \
               (oriented[NORTH] == GRAY if x == self.n - 1 else True) and \
               (oriented[WEST] == GRAY if y == 0 else True) and \
               (oriented[EAST] == GRAY if y == self.n - 1 else True)

    def randomBorder(self):       
        print("Random Border")
        rd.shuffle(self.corner_pieces)
        rd.shuffle(self.edge_pieces)
        
        for x, y in self.corner_cells:
            for piece in self.corner_pieces:
                if piece in self.used_pieces:
                    continue

                for rot in self.all_rotations[piece]:
                    if self.fits_border(x, y, rot):
                        self.place_piece(x, y, piece, rot)
                        break
                break

        for x, y in self.edge_cells:
            for piece in self.edge_pieces:
                if piece in self.used_pieces:
                    continue

                for rot in self.all_rotations[piece]:
                    if self.fits_border(x, y, rot):
                        self.place_piece(x, y, piece, rot)
                        break
                break

    def randomInside(self):
        print("Random Inside")
        rd.shuffle(self.inner_pieces)
        interior_iter = iter(self.inner_pieces)
        for x, y in self.inner_cells:
            piece = next(interior_iter)
            self.place_piece(x, y, piece, rd.choice(self.all_rotations[piece]))

    def place_piece(self, x, y, piece, orientation):
        self.board[(x, y)] = orientation
        self.board_pieces[(x, y)] = piece
        if piece not in self.used_pieces:
            self.used_pieces.append(piece)

    def format(self):
        # Construction de la solution en liste plate : ordre "de bas en haut", chaque ligne de gauche à droite.
        flat_solution = [self.board[(x, y)] for (x,y) in self.cells]
        return flat_solution

