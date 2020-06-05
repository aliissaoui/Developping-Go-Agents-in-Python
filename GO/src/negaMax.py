import eval
import time

class NegaMax():

    def __init__(self, color):
        self._mycolor = color
        self._maxscore = 100000
        self._eval = eval.Eval(color)
    
    def Negamax(self, b, depth, alpha, beta, color):
        """ Negamax function with Alpha Beta Pruning ( without Transposition table) """
        if b.is_game_over():
            res = b.result()
            if res == "1-0":
                r = ((-1)**self._mycolor) * (self._maxscore + 1)
            elif res == "0-1":
                r = - ((-1)**self._mycolor) * (self._maxscore + 1)
            else:
                r = 0
            return color * r

        if depth == 0:
            e= color * self._eval.evaluate(b)
            return e

        moves = b.generate_legal_moves()
        max_score = -self._maxscore

        for move in moves:
            b.push(move)
            max_score = max( max_score, -self.Negamax(b, depth-1, -beta, -alpha, -color))
            b . pop()

            alpha = max(alpha, max_score)

            if alpha >= beta:
                break

        return max_score

    """ first level of negamax search"""

    def Negamax_coup(self, b, depth, turn):
        if b.is_game_over() or depth == 0:
            return None
        
        moves = b.generate_legal_moves()
        added = []


        moves = b.generate_legal_moves()
        v, coup = None, None
        for m in moves:
            if ( turn < 7):
                x,y = b.unflatten(m)
                if ( x < 2 or y < 2 or x >= b._BOARDSIZE-2 or y >= b._BOARDSIZE-2):
                    continue
            elif ( turn < 15):
                x,y = b.unflatten(m)
                if ( x < 1 or y < 1 or x >= b._BOARDSIZE-1 or y >= b._BOARDSIZE-1):
                    continue

            b.push(m)
            t = time.time()
            ret = self.Negamax(b, depth - 1, -self._maxscore, self._maxscore, self._mycolor)

            if v is None or ret > v:
                coup = m
                v = ret
            b.pop()
    
        return (coup, v)
