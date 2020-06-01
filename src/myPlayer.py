# -*- coding: utf-8 -*-
''' This is the file you have to modify for the tournament. Your default AI player must be called by this module, in the
myPlayer class.

Right now, this class contains the copy of the randomPlayer. But you have to change this!
'''

import time
import Goban
import signal
import random
import threading
import queue
from random import choice
from playerInterface import *
from copy import deepcopy as cp
from contextlib import contextmanager


@contextmanager
def timeout(time):
    # Register a function to raise a TimeoutError on the signal.
    signal.signal(signal.SIGALRM, raise_timeout)
    # Schedule the signal to be sent after ``time``.
    signal.alarm(time)

    try:
        yield
    except TimeoutError:
        pass
    finally:
        # Unregister the signal so it won't be triggered
        # if the timeout is not reached.
        signal.signal(signal.SIGALRM, signal.SIG_IGN)


def raise_timeout(signum, frame):
    raise TimeoutError


class myPlayer(PlayerInterface):
    ''' 
    Example of a random player for the go. The only tricky part is to be able to handle
    the internal representation of moves given by legal_moves() and used by push() and 
    to translate them to the GO-move strings "A1", ..., "J8", "PASS". Easy!
    '''
    turn = 0
    stonesTime, libertiesTime, edgesTime, captureTime, EulerTime = 0, 0, 0, 0, 0
    zob_hash = []

    def __init__(self):
        self._board = Goban.Board()
        self._mycolor = None

    def getPlayerName(self):
        return "My Player"

    def getPlayerMove(self):
        self.turn += 1
        print("-------------------------------- TURN ",
              self.turn, " --------------------")
        if (self._board._lastPlayerHasPassed):
            print("result before I play: ", self._board.result())
            return 'PASS'
        if (self.turn == 1):
            if (self._mycolor == 1):
                move = Goban.Board.name_to_flat('C6')
            else:
                move = Goban.Board.name_to_flat('G6')

        elif (self.turn == 2):
            if (self._mycolor == 1):
                move = Goban.Board.name_to_flat('D4')
            else:
                move = Goban.Board.name_to_flat('F4')
        elif (self.turn == 3):
            if (self._mycolor == 1):
                move = Goban.Board.name_to_flat('F6')
            else:
                move = Goban.Board.name_to_flat('D6')

        else:
            if self._board.is_game_over():
                print("Referee told me to play but the game is over!")
                return "PASS"
            t = time.time()

            # self._board.prettyPrint()
            board_backup = cp(self._board)

            #move, v = self.simpleEvaluation()
            #move, v = self.MaxMinCoup(self._board, 3)
            #move, v = self.AlphaBetaCoup(self._board, 2)
            # print(self._board.__str__())
            #move, v = self.Negamax_coup(self._board, 1)
            #move, v = self.IDS_AB(10)
            move, v = self.IDS_NG(10)

            self._board = board_backup
            print("############### ::::: ", Goban.Board.flat_to_name(
                move), "value: ", v, "   time: ", time.time() - t)

        self._board.push(move)

        # New here: allows to consider internal representations of moves
        print("I am playing ", self._board.move_to_str(move))
        print("My current board :")
        self._board.prettyPrint()
        # move is an internal representation. To communicate with the interface I need to change if to a string
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

    """ To maximize the number of stones """

    def maxNbStones(self):
        t = time.time()
        b = self._board
        if (self._mycolor == 1):
            r = b._nbBLACK - b._nbWHITE
        else:
            r = b._nbWHITE - b._nbBLACK

        self.stonesTime += time.time() - t
        return r

    """ To maximize our libertieson the board """

    def liberties(self):
        t = time.time()
        my_iberties = 0
        op_liberties = 0
        b = self._board
        for fcoord in range((b._BOARDSIZE - 1) * 10):
            if b._stringLiberties[fcoord] != -1:
                if b._board[fcoord] == self._mycolor:
                    my_iberties += b._stringLiberties[fcoord]
                else:
                    op_liberties += b._stringLiberties[fcoord]
        self.libertiesTime += time.time()-t

        r = my_iberties - op_liberties

        self.stonesTime += time.time() - t
        return r

    """ To avoid the stones on the edges of the board. """

    def edges(self):
        t = time.time()
        goal = 0
        b = self._board
        isOnBoard = True
        coord = b.name_to_coord(b._historyMoveNames[-1])
        #print("coord : ", coord)
        x, y = coord
        if(x != -1):

            neighbors = ((x+1, y), (x-1, y), (x, y+1), (x, y-1))
            for c in neighbors:
                isOnBoard = isOnBoard and b._isOnBoard(c[0], c[1])
            if not isOnBoard:
                #print("\n ",(x,y),"is on edge dude\n")
                goal = - 0.5
        self.edgesTime += time.time() - t
        return goal

    """ Computes the number of Euler of a board,
        By minimazing it, we create connected stones and eyes """

    def EulerNumber(self):
        t = time.time()
        b = self._board
        Qb1, Qb2, Qb3 = 0, 0, 0
        Qw1, Qw2, Qw3 = 0, 0, 0

        end = (b._BOARDSIZE-1) * 10 + 1

        my_set, op_set = [0, 0, 0, 0], [0, 0, 0, 0]
        for a in range(end):

            x, y = b.unflatten(a)

        #   print("treating :", b.flat_to_name(a), "aka: ",x,y)
            stones_set = [(x, y), (x+1, y), (x, y-1), (x+1, y-1)]

            for i in range(4):
                if (b._isOnBoard(stones_set[i][0], stones_set[i][1])):
                    my_set[i] = (b[b.flatten(stones_set[i])] == self._mycolor)
                    op_set[i] = (b[b.flatten(stones_set[i])]
                                 == 3-self._mycolor)
                else:
                    my_set[i] = 0
                    op_set[i] = 0

            s_b = sum(my_set)
            s_w = sum(op_set)

            if s_b == 1:
                #print("Q1 FOUUNNNNDDD")
                Qb1 += 1
            elif s_b == 3:
                #print("Q3 FOUUNNNNDDD")
                Qb3 += 1
            elif s_b == 2:
                if ((my_set[0] and my_set[3]) or (my_set[1] and my_set[2])):
                    #print("Q2 FOUUNNNNDDD")
                    Qb2 += 1
            if s_w == 1:
                Qw1 += 1
            elif s_w == 3:
                Qw3 += 1
            elif s_w == 2:
                if ((op_set[0] and op_set[3]) or (op_set[1] and op_set[2])):
                    Qw2 += 1

        e_b = (Qb1 - Qb2 + 2*Qb3) / 4
        e_w = (Qw1 - Qw2 + 2*Qw3) / 4
        r = e_b - e_w
        self.EulerTime += time.time() - t
        return r

    """ Returns the difference between the number of stones we captured
        and the stones the ennemie captured"""

    def captured(self, b):
        if (self._mycolor == 1):
            r = 3*(b._capturedWHITE - b._capturedBLACK)
        else:
            r = 3*(b._capturedBLACK - b._capturedWHITE)

        return r

    """ The evaluation function """

    def evaluate(self, b):

        score = 0
        # !add coef to every goal

        # maximizing the number of stones *
        goal1 = self.maxNbStones()
        score += goal1

        # maximizing the number of liberties
        goal2 = self.liberties()
        score += goal2

        # avoinding moves on the edge
        # !goal3 value
        goal3 = self.edges()
        score += goal3

        # maximize the number of stones we capture
        goal4 = self.captured(self._board)
        score += goal4

        # connecting stones and eyes making with euler number
        goal5 = self.EulerNumber()
        score -= goal5

        #print("             goal1: ", goal1, " ///// goal2: ", goal2, " //// goal3: ", goal3, " //// goal5: ", goal5 , "score: ", score)
        return score
        '''
        for key,value in d.items():
            print( key , value )
        '''

    def simpleEvaluation(self):
        """ A one level search for test """
        best, v = 0, -1000
        i = 0

        self._board.prettyPrint()
        for m in self._board.generate_legal_moves():
            if (m != -1):
                self._board.push(m)
                tmp = self.evaluate(self._board)
                # self._board.prettyPrint()
                # print("_____ coup: ", Goban.Board.flat_to_name(
                #    m), " of value: ", tmp)

                if tmp > v:
                    best = m
                    v = tmp
                self._board.pop()
                i += 1
        # print("-----------chosen: ",  Goban.Board.flat_to_name(best),
              # " aka: ", best, v, "-----------")
        return best, v

    # ALPHA BETA
    def AlphaBetaCoup(self, b, depth):
        """ First level of MinMax search with Alpha Beta Pruning"""
        if b.is_game_over() or depth == 0:
            return None

        v, coup = None, None
        for m in b.generate_legal_moves():
            b.push(m)
            #t = time.time()
            ret = self.AlphaBeta(b, depth - 1, -1000, 1000)
            #print("Coup: ", b.flat_to_name(m), "valeur: ", ret, " temps: ", time.time()-t)

            if v is None or ret > v:
                coup = m
                v = ret
            b.pop()
        totalEvalTime = self.stonesTime + self.libertiesTime + \
            self.edgesTime + self.captureTime + self.EulerTime
        print("   Stones time : ", self.stonesTime,
              "   Liberties time: ", self.libertiesTime,
              "   Edges time: ", self.edgesTime,
              "   Capture time: ", self.captureTime,
              "   Euler Time: ", self.EulerTime,
              "   Total: ", totalEvalTime)
        self.stonesTime, self.libertiesTime, self.edgesTime, self.captureTime, self.EulerTime = 0, 0, 0, 0, 0
        return (coup, v)

    def BetaAlpha(self, b, depth, alpha, beta):
        """ MaxMin with Alpha beta pruning"""
        if b.is_game_over():
            res = b.result()
            if res == "1-0":
                return 400
            elif res == "0-1":
                return -400
            else:
                return 0

        if depth == 0:
            e = self.evaluate(b)
            #print("depth : ", depth, "evaluation: ", e)
            return e

        v = None
        for m in b.generate_legal_moves():
            b.push(m)
            ret = self.AlphaBeta(b, depth - 1, alpha, beta)
            b.pop()
            if v is None or ret > v:
                v = ret
            if alpha < v:
                alpha = v
            #print("IN BETA ALPHA alpha : ", alpha, " --- Beta : ", beta)
            if alpha >= beta:
                #print("BETA CUT")
                return beta
       # print("depth: ", depth, "beta: ", beta)
        return alpha

    def AlphaBeta(self, b, depth, alpha, beta):
        """ MinMax with Alpha beta pruning"""
        if b.is_game_over():
            res = b.result()
            if res == "1-0":
                return 400
            elif res == "0-1":
                return -400
            else:
                return 0

        if depth == 0:
            e = self.evaluate(b)
            #print("depth : ", depth, "evaluation: ", e)
            return e

        v = None
        for move in b.generate_legal_moves():
            b.push(move)
            ret = self.BetaAlpha(b, depth-1, alpha, beta)
            b.pop()
            #print("reeeet : ", ret)
            if v is None or ret < v:
                v = ret
            if beta > v:
                beta = v

            #print(" IN ALPHA BETA: alpha : ", alpha, " --- Beta : ", beta)
            if alpha >= beta:
                #print("ALPHA CUT")
                return alpha

        #print("depth: ", depth, "beta: ", beta)
        return beta

    def IDS_AB(self, timeRange):
        """ Iterative deepening search for Alpha Beta"""

        # pour retourner une valeur au cas ou le temps est expiré.
        best_move, v = choice(list(self._board.generate_legal_moves())), 0
        depth = 1

        with timeout(timeRange):
            while (True):
                t = time.time()
                #print("applying depth: ", depth, " on :\n", board)
                move, v = self.AlphaBetaCoup(self._board, depth)
                print("depth : ", depth, " time: ", time.time() -
                    t, " move : ", Goban.Board.flat_to_name(move))
                # if move != best_move:
                best_move = move
                # print()

                depth += 1

        return best_move, v

    def Negamax(self, b, depth, alpha, beta):
        """ Negamax function with Alpha Beta Pruning ( without Transposition table) """
        if b.is_game_over():
            res = b.result()
            if res == "1-0":
                return 400
            elif res == "0-1":
                return -400
            else:
                return 0

        if depth == 0:
            e = self.evaluate(b)
            return e

        best_move, max_score = None, -1000
        moves = b.generate_legal_moves()
        for move in moves:
            b.push(move)
            score = -self.Negamax(b, depth-1, -beta, -alpha)
            b.pop()

            if best_move is None or score >= max_score:
                best_move = move
                max_score = score

            alpha = max(alpha, score)

                #print(" IN ALPHA BETA: alpha : ", alpha, " --- Beta : ", beta)
            if alpha >= beta:
                #print("ALPHA CUT")
                return alpha

        return alpha

    def Negamax_tb(self, b, depth, alpha, beta):
        """ Negamax function with Alpha Beta Pruning with a Transposition table """
        if b.is_game_over():
            res = b.result()
            if res == "1-0":
                return 400
            elif res == "0-1":
                return -400
            else:
                return 0

        if depth == 0:
            e = self.evaluate(b)
            return e

        best_move, max_score = None, -1000
        moves = b.generate_legal_moves()
        for move in moves:
            b.push(move)
            score = -self.Negamax(b, depth-1, -beta, -alpha)
            b.pop()

            if best_move is None or score >= max_score:
                best_move = move
                max_score = score

            alpha = max(alpha, score)

            #print(" IN ALPHA BETA: alpha : ", alpha, " --- Beta : ", beta)
            if alpha >= beta:
                #print("ALPHA CUT")
                return alpha

        return alpha

    """ first level of negamax search"""

    def Negamax_coup(self, b, depth):
        if b.is_game_over() or depth == 0:
            return None

        v, coup = None, None
        for m in b.generate_legal_moves():
            b.push(m)
           # t = time.time()
            ret = self.Negamax(b, depth - 1, -1000, 1000)
            #print("Coup: ", b.flat_to_name(m), "valeur: ", ret, " temps: ", time.time()-t)

            if v is None or ret > v:
                coup = m
                v = ret
            b.pop()
        return (coup, v)

    def IDS_NG(self, timeRange):
        """ Iterative deepening search for NegaMax"""

        # pour retourner une valeur au cas ou le temps est expiré.
        best_move, v = choice(list(self._board.generate_legal_moves())), 0
        depth = 1

        with timeout(timeRange):
            while (True):
                t = time.time()
                #print("applying depth: ", depth, " on :\n", board)
                move, v = self.Negamax_coup(self._board, depth)
                print("depth : ", depth, " time: ", time.time() -
                      t, " move : ", Goban.Board.flat_to_name(move))
                # if move != best_move:
                best_move = move
               # print()

                depth += 1

        return best_move, v

    def init_zobrist_Hash(self, b):
        self.zob_hash = [[0 for x in range(self._board._BOARDSIZE)] for y in range(
            self._board._BOARDSIZE)]
        for i in range((b._BOARDSIZE - 1) * 10):
            for j in range(2):
                self.zob_hash[i][j] = random.getrandbits(32)

    def zobrist_hash(self, b):
        h = 0
        for i in range((b._BOARDSIZE - 1) * 10):
            if (b[i] == 1):
                h ^= self.zob_hash[i][b[i]+1]
        return h

    def zob_narrowing(self, tt, alpha, beta):
        if tt.bound == tt.BOUND_LOWER:  # was entry.score >= beta
            alpha = max(alpha, tt.score)
        elif tt.bound == tt.BOUND_UPPER:  # was entry.score <= alpha
            beta = min(beta, tt.score)
        return alpha, beta

    def zob_is_exact(self, tt):
        return tt.bound == tt.BOUND_EXACT
