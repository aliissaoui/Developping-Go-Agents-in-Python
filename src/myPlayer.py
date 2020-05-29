# -*- coding: utf-8 -*-
''' This is the file you have to modify for the tournament. Your default AI player must be called by this module, in the
myPlayer class.

Right now, this class contains the copy of the randomPlayer. But you have to change this!
'''

import time
import Goban 
from random import choice
from playerInterface import *

class myPlayer(PlayerInterface):
    ''' Example of a random player for the go. The only tricky part is to be able to handle
    the internal representation of moves given by legal_moves() and used by push() and 
    to translate them to the GO-move strings "A1", ..., "J8", "PASS". Easy!

    '''

    def __init__(self):
        self._board = Goban.Board()
        self._mycolor = None

    def getPlayerName(self):
        return "Random Player"

    def getPlayerMove(self):
        if self._board.is_game_over():
            print("Referee told me to play but the game is over!")
            return "PASS" 
        moves = self._board.legal_moves() # Dont use weak_legal_moves() here!
        move = choice(moves) 
        self._board.push(move)

        # New here: allows to consider internal representations of moves
        print("I am playing ", self._board.move_to_str(move))
        print("My current board :")
        self._board.prettyPrint()
        # move is an internal representation. To communicate with the interface I need to change if to a string
        return Goban.Board.flat_to_name(move) 

    def playOpponentMove(self, move):
        print("Opponent played ", move) # New here
        # the board needs an internal represetation to push the move.  Not a string
        self._board.push(Goban.Board.name_to_flat(move)) 

    def newGame(self, color):
        self._mycolor = color
        self._opponent = Goban.Board.flip(color)

    def endGame(self, winner):
        if self._mycolor == winner:
            print("I won!!!")
        else:
            print("I lost :(!!")


    def evaluate(self,b):

        score = 0
        # !add coef to every goal
        # maximizing the number of stones *
        goal1 = b._nbBLACK - b._nbWHITE
        score += goal1 
        #print(goal1)
        
        
        # maximizing the number of liberties
        libertyBlack = 0
        libertyWhite = 0
        for fcoord in range( (b._BOARDSIZE -1) * 10) :
            if b._stringLiberties[fcoord ] != -1:
                if b._board[ fcoord ] == 1:
                    libertyBlack += b._stringLiberties[ fcoord ]
                else:
                    libertyWhite += b._stringLiberties[ fcoord ]
        goal2 = libertyBlack - libertyWhite
        score += goal2
        #print(goal2)
        # avoinding moves on the edge
        # !goal3 value
        goal3 = 0
        isOnBoard = True
        coord = b.name_to_coord( b._historyMoveNames[-1] )
        x, y = coord
        if( x == -1 ):
            goal3 = 0
        else:  
            neighbors = ((x+1, y), (x-1, y), (x, y+1), (x, y-1))
            for c in neighbors:
                isOnBoard = isOnBoard and b._isOnBoard(c[0], c[1])
            if not isOnBoard:
                goal3 = - 10
        
        score += goal3
        #print(goal3)
        #connectiong stones
        # dictionnaire de pairs racineString:longeur !can remove it
        d = {}
        f = []
           
        for fcoord in range( (b._BOARDSIZE-1) * 10 + 1):
            f.append(fcoord)
        
        for fc in f:
            color = self._board[fc]
            if color == 0:
                continue
            string = set([fc])
            frontier = [fc]
            while frontier:
                current_fc = frontier.pop() 
                string.add(current_fc)
                i = b._neighborsEntries[current_fc]
                while b._neighbors[i] != -1:
                    fn = b._neighbors[i]
                    i += 1
                    if b._board[fn] == color and not fn in string:
                        frontier.append(fn)
            #d[fc] = len(string)
            score += len(string) * (1 + len(string)/100)

            for s in string:
                if( s != fc):
                    f.remove(s)
            
        '''
        for key,value in d.items():
            print( key , value )
        '''
        return score
       
       