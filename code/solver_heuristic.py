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
##   Main Algo    ##
####################

def solve_heuristic(puzzle: EternityPuzzle):
    """
    Heuristic solution of the problem
    :param eternity_puzzle: object describing the input
    :return: a tuple (solution, cost) where solution is a list of the pieces (rotations applied) and
        cost is the cost of the solution
    """
    r = 241212
    print(f'Seed: {r}\n')
    rd.seed(r)  
    
    solver = Solver(puzzle)
    # solver.randomBorder()
    # solver.randomInside()

    # for crown_id in range(ceil(solver.n/2)):
    for crown_id in range(ceil(solver.n/2)):
        cells_crown = solver.get_cells_crown(crown_id)
        solver.greedy_crown(cells_crown, crown_id)
        # solver.randomInside()



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
    ##################                                   GREEDY                                   ##################
    ################################################################################################################

    def greedy_crown(self, cells_crown, i):
        """ Construit une solution greedy diagonales par diagonales """
        rd.shuffle(self.corner_pieces)
        rd.shuffle(self.edge_pieces)
        rd.shuffle(self.inner_pieces)

        for (x, y) in cells_crown:
            p, o, n = self.greedy_best_piece_crown(x, y, i)
            self.place_piece(x, y, p, o)  
                         
    
    def greedy_best_piece_crown(self, x, y, i):
        """ Renvoie la pièce non encore utilié qui engendre le moins de conflits en (x, y) """
        pieces = self.set_of_valid_pieces(i)
        best = [None, None, np.inf]

        for p in pieces:
            if p in self.used_pieces:
                continue  
            for o in self.all_rotations[p]:
                value = self.greedy_predict_conflict_o(x, y, o, i)
                if value < best[2]:
                    best = [p, o, value]
                if value == 0:
                    return best
                
        return best

    ################################################################################################################
    ##################                                   UTILS                                    ##################
    ################################################################################################################

    def greedy_predict_conflict_o(self, x, y, o, i):
        nb_conflicts = 0
        curr_crown = self.get_cells_crown(i)
        prec_crown = self.get_cells_crown(i-1)

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            if (x + dx, y + dy) in prec_crown:
                if i == 0:
                    nb_conflicts += self.get_border_conflict_c1_c2(min(x, x + dx), min(y, y + dy), max(x, x + dx), max(y, y + dy), o)
                else:
                    nb_conflicts += self.get_crown_conflicts_c1_c2(x, y , x + dx, y + dy, o)
            elif (x + dx, y + dy) in curr_crown:
                nb_conflicts += self.get_crown_conflicts_c1_c2(x, y , x + dx, y + dy, o)

        return nb_conflicts

    def get_crown_conflicts_c1_c2(self, x1, y1, x2, y2, o):
        if x1 == x2:
            if self.board[(x2, y2)] == None: return 0
            elif y1 < y2 and self.board[(x2, y2)][WEST] != o[EAST]: return 1
            elif y1 > y2 and self.board[(x2, y2)][EAST] != o[WEST]: return 1

        else:
            if self.board[(x2, y2)] == None: return 0
            elif x1 < x2 and self.board[(x2, y2)][SOUTH] != o[NORTH]: return 1
            elif x1 > x2 and self.board[(x2, y2)][NORTH] != o[SOUTH]: return 1
            
        return 0
    
    def get_border_conflict_c1_c2(self, x1, y1, x2, y2, o):
        if x1 == x2:
            if y1 < 0 and o[WEST] != GRAY:
                return 1
            elif y1 >= 0 and o[EAST] != GRAY:
                return 1
        else:
            if x1 < 0 and o[SOUTH] != GRAY:
                return 1
            elif x1 >= 0 and o[NORTH] != GRAY:
                return 1
        
        return 0

    def set_of_valid_pieces(self, i):
        """ Renvoie le set de pièces valide pour la case (x, y) """
        if i == 0:
            return self.border_pieces
        else:
            return self.inner_pieces

    def get_cells_crown(self, i):

        cells = []
        
        for c in range(i, self.n - i):
            cells.append((i, c))

        if self.n - i - 1 != i:
            for c in range(i, self.n - i):
                cells.append((self.n - i - 1, c))
        
        for r in range(i + 1, self.n - i - 1):
            cells.append((r, i))

        if self.n - i - 1 != i:
            for r in range(i + 1, self.n - i - 1):
                cells.append((r, self.n - i - 1))
        
        return cells

    def place_piece(self, x, y, piece, orientation):
        self.board[(x, y)] = orientation
        self.board_pieces[(x, y)] = piece
        if piece not in self.used_pieces:
            self.used_pieces.append(piece)

    def format(self):
        # Construction de la solution en liste plate : ordre "de bas en haut", chaque ligne de gauche à droite.
        flat_solution = [self.board[(x, y)] for (x,y) in self.cells]
        return flat_solution

