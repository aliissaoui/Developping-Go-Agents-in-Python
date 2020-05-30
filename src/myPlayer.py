# -*- coding: utf-8 -*-
''' This is the file you have to modify for the tournament. Your default AI player must be called by this module, in the
myPlayer class.

Right now, this class contains the copy of the randomPlayer. But you have to change this!
'''

import time
import Goban 
import signal
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
    ''' Example of a random player for the go. The only tricky part is to be able to handle
    the internal representation of moves given by legal_moves() and used by push() and 
    to translate them to the GO-move strings "A1", ..., "J8", "PASS". Easy!

    '''
    turn = 0
    
    def __init__(self):
        self._board = Goban.Board()
        self._mycolor = None

    def getPlayerName(self):
        return "My Player"

    def getPlayerMove(self):
        self.turn += 1
        print("-------------------------------- TURN ", self.turn, " --------------------" )
        if (self._board._lastPlayerHasPassed and self._board.result() == "1-0"):
                return 'PASS'
        if (self.turn == 1):
            move = Goban.Board.name_to_flat('C7')
            
        else:
            if self._board.is_game_over():
                print("Referee told me to play but the game is over!")
                return "PASS" 
            t = time.time()

            self._board.prettyPrint()
            board_backup = cp(self._board)
            
            #move, v = self.simpleEvaluation()
            #move, v = self.MaxMinCoup(self._board, 3)
            #move, v = self.AlphaBetaCoup(self._board, 2)
            move, v = self.IDS_AB(30)
           
            self._board = board_backup
            print("############### ::::: ", Goban.Board.flat_to_name(move), "value: ", v, "   time: ", time.time() - t)
    
        self._board.push(move)

        # New here: allows to consider internal representations of moves
        print("I am playing ", self._board.move_to_str(move))
        print("My current board :")
        self._board.prettyPrint()
        # move is an internal representation. To communicate with the interface I need to change if to a string
        return Goban.Board.flat_to_name(move) 

    def playOpponentMove(self, move):
        print("Opponent played ", move) # New here
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
            
            
    # maximizing the number of stones *
    def maxNbStones(self):
        b = self._board
        return b._nbBLACK - b._nbWHITE
    
    # maximizing the number of liberties
    def liberties(self):
        libertyBlack = 0
        libertyWhite = 0
        b = self._board
        for fcoord in range( (b._BOARDSIZE -1) * 10 ) :
            if b._stringLiberties[ fcoord ] != -1:
                if b._board[ fcoord ] == 1:
                    libertyBlack += b._stringLiberties[ fcoord ]
                else:
                    libertyWhite += b._stringLiberties[ fcoord ]
        return libertyBlack - libertyWhite

    # avoinding moves on the edge
    def edges(self):
        goal = 0
        b = self._board
        isOnBoard = True
        coord = b.name_to_coord( b._historyMoveNames[-1] )
        #print("coord : ", coord)
        x, y = coord
        if( x != -1 ):
            
            neighbors = ((x+1, y), (x-1, y), (x, y+1), (x, y-1))
            for c in neighbors:
                isOnBoard = isOnBoard and b._isOnBoard(c[0], c[1])
            if not isOnBoard:
                #print("\n ",(x,y),"is on edge dude\n")
                goal = - 10
        return goal
    
    # connecting stones
    def stoneConnection(self, b):
        f = []
        
        # put all the stones in f 
        for fcoord in range( (b._BOARDSIZE-1) * 10 + 1):
            f.append(fcoord)
            
        goal = 0
        #
        for fc in f:
            color = self._board[fc]
            if color == 0:
                continue
            
            string = set([fc])
            frontier = [fc]
            
            # 
            while frontier:
                current_fc = frontier.pop() 
                string.add(current_fc)
                i = b._neighborsEntries[current_fc]
                while b._neighbors[i] != -1:
                    fn = b._neighbors[i]
                    i += 1
                    if b._board[fn] == color and not fn in string:
                        frontier.append(fn)
                     
            if color == 1:
                goal += len(string) * (1 + len(string)/100)
            elif color == 2:
                goal -= len(string) * (1 + len(string)/100)

        
        for s in string:
            if( s != fc):
                f.remove(s)
            
        return goal
    
    
    def EulerNumber(self, color):
        b = self._board
        Qb1, Qb2, Qb3 = 0, 0, 0
        Qw1, Qw2, Qw3 = 0, 0, 0
        
        d = (b._BOARDSIZE-1) + 1
        f = (b._BOARDSIZE-1) * 10 
        black_set, white_set = [0,0,0,0], [0,0,0,0]
        #print("from :", b.flat_to_name(d), "to: ", b.flat_to_name(f))
        for a in range(d,f):
            x,y = b.unflatten(a)

         #   print("treating :", b.flat_to_name(a), "aka: ",x,y)
            stones_set = [(x,y) , (x+1,y), (x, y-1), (x+1, y-1)]
            """ stones_names = [0,0,0,0]
            for i in range(len(stones_set)):
                if b._isOnBoard(stones_set[i][0], stones_set[i][1]):
                    stones_names[i] =  b.coord_to_name(stones_set[i])
                else:
                    stones_names[i] = "out" """
            #print(stones_set)
            for i in range(4):
                if (b._isOnBoard(stones_set[i][0],stones_set[i][1] )):
                    black_set[i] = (b[b.flatten(stones_set[i])] == color)
                    white_set[i] = (b[b.flatten(stones_set[i])] == 2)
                else:
                    black_set[i] = 0
                    white_set[i] = 0
            #if ( True in stones_set ):
            #    print("treating :", b.flat_to_name(a), "aka: ",x,y)
             #   print(stones_names)
              #  print("corrected: ", stones_set)
            s_b = sum(black_set)
            s_w = sum(white_set)
            """ if ( s_b != 0 ):
                print("                         SUM Black: ", s_b)
            if ( s_w != 0 ):
                print("                         SUM White: ", s_w)"""
            
            if s_b == 1:
                #print("Q1 FOUUNNNNDDD")
                Qb1 += 1
            elif s_b == 3:
                #print("Q3 FOUUNNNNDDD")
                Qb3 += 1
            elif s_b == 2:
                if ((black_set[0] and black_set[3]) or (black_set[1] and black_set[2])):
                    #print("Q2 FOUUNNNNDDD")
                    Qb2 += 1
            if s_w == 1:
                Qw1 += 1
            elif s_w == 3:
                Qw3 += 1
            elif s_w == 2:
                if ((white_set[0] and white_set[3]) or (white_set[1] and white_set[2])):
                    Qw2 += 1
                    
        e_b = (Qb1 - Qb2 + 2*Qb3) / 4
        e_w = (Qw1 - Qw2 + 2*Qw3) / 4

        """ print("Black Euler value: ", e_b)
        
        print("White Euler value: ", e_w)"""
        return (e_b - e_w)
        


    def evaluate(self,b):

        score = 0
        # !add coef to every goal
        
        
        # maximizing the number of stones *
        goal1 = self.maxNbStones()
        score +=  goal1         
        
        # maximizing the number of liberties
        goal2 = self.liberties()
        score +=  goal2
        
        # avoinding moves on the edge
        # !goal3 value
        goal3 = self.edges() 
        score += goal3
        
        # connecting stones
        # dictionnaire de pairs racineString:longeur !can remove it
        #goal4 = self.stoneConnection(self._board)
        #score += 10 * goal4
        
        goal5 = self.EulerNumber(1)
        score -= goal5
        
       # print("             goal1: ", goal1, " ///// goal2: ", goal2, " //// goal3: ", goal3, " //// goal5: ", goal5 , "score: ", score)
        return score
        '''
        for key,value in d.items():
            print( key , value )
        '''

    
    def simpleEvaluation(self):
        best, v = 0, -1000
        i = 0

        self._board.prettyPrint()
        for m in self._board.generate_legal_moves():
            if ( m != -1):
                self._board.push(m)
                tmp = self.evaluate(self._board)
                self._board.prettyPrint()
                print("_____ coup: ", Goban.Board.flat_to_name(m)," of value: ", tmp)
    
                if tmp > v:
                    best = m
                    v = tmp
                self._board.pop()
                i += 1
        print("-----------chosen: ",  Goban.Board.flat_to_name(best), " aka: ", best, v,"-----------")
        return best, v
       
           
    # ALPHA BETA
        
    
    def AlphaBetaCoup(self, b, depth):
        if b.is_game_over() or depth == 0:
            return None
    
        v, coup = None, None
        for m in b.generate_legal_moves():
            b.push(m)
            ret = self.AlphaBeta(b, depth - 1, -1000, 1000)
            #print("coup: ", Goban.Board.flat_to_name(m), "value : ", ret)
            if v is None or ret > v:
                coup = m
                v = ret
            b.pop()
    
        return (coup, v) 
    
    def BetaAlpha(self, b, depth, alpha, beta):
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
            if v is None or ret > v:
                v = ret
            if alpha < v:
                alpha = v
            if alpha >= beta:
                b.pop()
                return beta
            b.pop()
        #print("depth: ", depth, "alpha: ", alpha)
        return alpha
    
    def AlphaBeta(self, b, depth, alpha, beta):
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
           # print("depth : ", depth, "evaluation: ", e)
            return e
    
        v = None
        for move in b.generate_legal_moves():
            b.push(move)    
            ret = self.BetaAlpha(b, depth-1, alpha, beta)
           # print("reeeet : ", ret)
            if v is None or ret < v:
                v = ret
            if beta > v:
                beta = v
            if alpha >= beta:
                b.pop()
                return alpha
            b.pop()
       # print("depth: ", depth, "beta: ", beta)
        return beta
    
    #### END ALPHA BETA
    
    
    #### MIN MAX
    
    
    
    def MaxMinCoup(self, b, depth=3):
        if b.is_game_over() or depth == 0:
            return None
    
        v, coup = None, None
        for m in b.generate_legal_moves():
            b.push(m)
            #b.prettyPrint()
            #print("################################### coup: ", Goban.Board.flat_to_name(m), "###################################")
            ret = self.MaxMin(b, depth - 1)
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! coup: ", Goban.Board.flat_to_name(m), "value : ", ret, "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            if v is None or ret > v:
                coup = m
                v = ret
            b.pop()
            #a = input()
    
        return (coup, v) 

    def MaxMin(self, b, depth=3):
        if b.is_game_over():
            res = b.result()
            if res == "1-0":
                return 400
            elif res == "0-1":
                return -400
            else:
                return 0
    
        if depth == 0:
            return self.evaluate(b)
    
        v = None
        for m in b.generate_legal_moves():
            #print("           test: ", Goban.Board.flat_to_name(m))
            b.push(m)
            #b.prettyPrint()
            #a = input()            
            ret = self.MinMax(b, depth - 1)
            #print("                                 Sous coup: ", Goban.Board.flat_to_name(m), "value : ", ret,"                             ")
            if v is None or ret > v:
                v = ret
            b.pop()
    
        return v
    
    def MinMax(self, b, depth=3):
        if b.is_game_over():
            res = b.result()
            if res == "1-0":
                return 400
            elif res == "0-1":
                return -400
            else:
                return 0
    
        if depth == 0:
            return self.evaluate(b)
    
        v = None
        for m in b.generate_legal_moves():
            #print("           test: ", Goban.Board.flat_to_name(m))
            b.push(m)
            #b.prettyPrint()
            #a = input()
            ret = self.MaxMin(b, depth - 1)
            if v is None or ret < v:
                v = ret
            b.pop()
    
        return v


    #### FIN MIN MAX
    
    
    def IDS_AB(self, timeRange):
    
        #pour retourner une valeur au cas ou le temps est expiré.
        best_move, v = choice(list(self._board.generate_legal_moves())), 0
        depth = 1
        
    
        with timeout(timeRange):
            while (True):
                t = time.time()
                #print("applying depth: ", depth, " on :\n", board)
                move, v = self.AlphaBetaCoup(self._board, depth)
                print("depth : ", depth, " time: ", time.time() -t, " move : ", Goban.Board.flat_to_name(move))
                #if move != best_move:
                best_move = move
               # print()
                
                depth += 1
                    
        return best_move, v