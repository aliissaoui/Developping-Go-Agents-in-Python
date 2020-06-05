import time   

class Eval():  

    def __init__(self, color):
        self._mycolor = color
        self.stonesTime, self.libertiesTime, self.edgesTime, self.captureTime, self.EulerTime = 0, 0, 0, 0, 0

    """ To maximize the number of stones """
    def maxNbStones(self, b):
        t = time.time()
        if (self._mycolor == 1):
            r = b._nbBLACK - b._nbWHITE
        else:
            r = b._nbWHITE - b._nbBLACK

        self.stonesTime += time.time() - t
        return r

    """ To maximize our libertieson the board """

    def liberties(self, b):
        t = time.time()
        my_iberties = 0
        op_liberties = 0
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

    def manhattan_dist_to_center(self, b):
        m = b._historyMoveNames[-1]
        coord =  b.name_to_coord(m)
        x, y = coord
        dist = abs(x-4)+abs(y-4)
        #print("Manhattan distance for : ---- ", m, " ----- is :  ---- ", dist)
        return dist

    def edges(self, b):
        t = time.time()
        goal = 0
        isOnBoard = True
        coord = b.name_to_coord(b._historyMoveNames[-1])
        x, y = coord
        if(x != -1):

            neighbors = ((x+1, y), (x-1, y), (x, y+1), (x, y-1))
            for c in neighbors:
                isOnBoard = isOnBoard and b._isOnBoard(c[0], c[1])
            if not isOnBoard:
                goal = - 0.5
        self.edgesTime += time.time() - t
        return goal

    
    def stoneConnection(self, b):
        f = []
        
        # put all the stones in f 
        for fcoord in range( (b._BOARDSIZE-1) * 10 + 1):
            f.append(fcoord)
            
        goal = 0
        #
        for fc in f:
            color = b[fc]
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
    

    """ Computes the number of Euler of a board,
        By minimazing it, we create connected stones and eyes """   
    def EulerNumber(self, b):
        t = time.time()
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
                    op_set[i] = (b[b.flatten(stones_set[i])] == 3-self._mycolor)
                else:
                    my_set[i] = 0
                    op_set[i] = 0

            s_b = sum(my_set)
            s_w = sum(op_set)

            if s_b == 1:
                Qb1 += 1
            elif s_b == 3:
                Qb3 += 1
            elif s_b == 2:
                if ((my_set[0] and my_set[3]) or (my_set[1] and my_set[2])):
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

        # Maximiser le nombre de mes pions
        goal1 = self.maxNbStones(b)
        score += 10*goal1

        # Maximiser le nombre de mes libertés
        goal2 = self.liberties(b)
        score += goal2

        # Eviter les bordures du plateau
        goal3 = self.edges(b)
        score += goal3

        # Joueur le plus possible au milieu
        goal31 = self.manhattan_dist_to_center(b)
        score -= goal31

        # maximize le nombre des pions qu'on capture
        goal4 = self.captured(b)
        score += 8*goal4

        # maximiser le nombre des pions connectés
        #goal5 = self.stoneConnection(b)
        #score += goal5
        
        # maximiser le nombre des pions connectés et des cercles crées
        goal6 = self.EulerNumber(b)
        score -= goal6

        return score

