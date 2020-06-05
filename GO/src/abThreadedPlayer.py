# -*- coding: utf-8 -*-
''' This is the file you have to modify for the tournament. Your default AI player must be called by this module, in the
myPlayer class.

Right now, this class contains the copy of the randomPlayer. But you have to change this!
'''

import time
import Goban
from random import choice
import json
import ids
from playerInterface import *
from copy import deepcopy as cp

class myPlayer(PlayerInterface):
    '''
    Example of a random player for the go. The only tricky part is to be able to handle
    the internal representation of moves given by legal_moves() and used by push() and
    to translate them to the GO-move strings "A1", ..., "J8", "PASS". Easy!
    '''
    def __init__(self):
        self._board = Goban.Board()
        self._mycolor = None
        self._gametime = 0
        self._turn = 0

        with open('games.json') as json_file:
            self._games = json.load(json_file)

    def getPlayerName(self):
        return "Budah"

    def getPlayerMove(self):
        if self._turn == 0:
            self.IDS = ids.IDS(self._mycolor)

        t1 = time.time()
        self._turn += 1
        print("-------------------------------- TURN ",
            self._turn, " --------------------")
        if (self._board._lastPlayerHasPassed):
            print("result before I play: ", self._board.result())
            return 'PASS'
        if (self._mycolor == 1):
            c = "B"
        else:
            c = "W"
        e = False
        

        if ( self._turn == 1 and c == "B"):
            move = Goban.Board.name_to_flat('E5')

        elif (self._turn <= 5):
            moves = self._board.generate_legal_moves()
            if ( c == "B"):
                for g in self._games:
                    if (g['moves'][2*self._turn] == self._board._historyMoveNames[-1]) :
                        move = Goban.Board.name_to_flat(g['moves'][2*self._turn+1])
                        if ( move in moves):
                            e = True
                            break
            else:
                for g in self._games:
                    if (g['moves'][2*self._turn] == self._board._historyMoveNames[-1]):
                        move = Goban.Board.name_to_flat(g['moves'][2*self._turn+1])
                        if ( move in moves):
                            e = True
                            break

            # si on n'a pas trouvé de coup dans la bilbiothèque d'ouverture
            if ( e == False ):
                move = choice(moves)

        else:
            if self._board.is_game_over():
                print("Referee told me to play but the game is over!")
                return "PASS"
            t = time.time()

            board_backup = cp(self._board)

            print("time: ", self._gametime)
            n = len(self._board.generate_legal_moves())

            if ( self._gametime > 290 ):
                if ( n < 10 ):
                    move, v = self.IDS.ABT.AlphaBetaCoupThreaded(self._board, 2, self._turn)
                else:
                    move, v = self.IDS.ABT.AlphaBetaCoupThreaded(self._board, 1, self._turn)
            elif(self._turn < 20):
                move, v = self.IDS.IDS_AB_threaded(self._board, 4, self._turn)
            elif(self._turn < 35):
                move, v = self.IDS.IDS_AB_threaded(self._board, 6, self._turn)
            else:
                move, v = self.IDS.IDS_AB_threaded(self._board, 7, self._turn)

            self._board = board_backup

        self._board.push(move)

        # New here: allows to consider internal representations of moves
        print("I am playing ", self._board.move_to_str(move))
        print("My current board :")
        self._board.prettyPrint()
        # move is an internal representation. To communicate with the interface I need to change if to a string
        self._gametime += time.time() - t1
        return Goban.Board.flat_to_name(move)

    def playOpponentMove(self, move):
        print("Opponent played ", move)  # New here
        # the board needs an internal represetation to push the move.  Not a string
        self._board.push(Goban.Board.name_to_flat(move))

    def newGame(self, color):
        self._mycolor = color
        self._opponent = Goban.Board.flip(color)

    def endGame(self, winner):
        if self._mycolor == winner:
            print("I won!!!")
        else:
            print("I lost :(!!")


    def simpleEvaluation(self):
        """ Une fonction de recherche de niveau 1 pour faire des tests. """
        best, v = 0, -100000
        i = 0

        self._board.prettyPrint()
        for m in self._board.generate_legal_moves():
            if (m != -1):
                self._board.push(m)
                tmp = self.evaluate(self._board)
                if tmp > v:
                    best = m
                    v = tmp
                self._board.pop()
                i += 1
        return best, v

