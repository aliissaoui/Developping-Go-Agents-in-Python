import time, os
import eval
import alphaBeta
import operator
import concurrent.futures
from copy import deepcopy as cp
import multiprocessing, threading

class AlphaBetaThreaded():

    
    def __init__(self, color):
        self._mycolor = color
        self._maxscore = 100000
        self._processes = []
        self._eval = eval.Eval(color)

    def keywithmaxval(self, d):
     v=list(d.values())
     k=list(d.keys())
     return k[v.index(max(v))]


    ########################### THREADED ############################@@
    def AlphaBetaCoupThreaded(self, b, depth):
        """ First level of MinMax search with Alpha Beta Pruning"""
        if b.is_game_over() or depth == 0:
            return None
        
        moves = b.generate_legal_moves()
        n = len(moves)

        manager = multiprocessing.Manager()
        results = manager.dict()

        start_time = time.time()
        processes = [None] * n
        boards = [None] * n
        

        self._nodes = 0
        v, coup = None, None
        for i in range(n):
            b.push(moves[i])
            d = cp(b)
            processes[i] = multiprocessing.Process(target=self.AlphaBetaThreaded, args=(d, depth - 1, -self._maxscore, self._maxscore, results, i, depth-1)) 
            b.pop()

        self._processes = processes

        [process.start() for process in processes]
        [process.join()  for process in processes]



        results = dict(results)
        i = self.keywithmaxval(results)
        coup, v = moves[int(i)], results[i]

        end_time = time.time()
        print("processes time=", end_time - start_time)

        print("processes hit: ", coup, ", of value: ", v)
        return (coup, v)

    def BetaAlphaThreaded(self, b, depth, alpha, beta, results, i, depth_init):
        self._nodes += 1

        """ MaxMin with Alpha beta pruning"""
        if b.is_game_over():
            res = b.result()
            if res == "1-0":
                r = - ((-1)**self._mycolor) * self._maxscore
            elif res == "0-1":
                r = ((-1)**self._mycolor) * self._maxscore
            else:
                r = 0
            return r

        if depth == 0:
            e = self._eval.evaluate(b)
            return e

        v = None
        for m in b.generate_legal_moves():
            b.push(m)
            ret = self.AlphaBetaThreaded(b, depth - 1, alpha, beta, results, i, depth_init)
            b.pop()
            if v is None or ret > v:
                v = ret
            if alpha < v:
                alpha = v
            if alpha >= beta:
                return beta
        return alpha

    def AlphaBetaThreaded(self, b, depth, alpha, beta, results, i, depth_init):
        self._nodes += 1

        """ MinMax with Alpha beta pruning"""
        if b.is_game_over():
            res = b.result()
            if res == "1-0":
                r = - ((-1)**self._mycolor) * self._maxscore
            elif res == "0-1":
                r = ((-1)**self._mycolor) * self._maxscore
            else:
                r = 0
            if (depth == depth_init):  
                results[i] = r
            return r

        if depth == 0:
            e = self._eval.evaluate(b)
            if (depth == depth_init):
                results[i] = e
            return e

        v = None
        for move in b.generate_legal_moves():
            b.push(move)
            ret = self.BetaAlphaThreaded(b, depth-1, alpha, beta, results, i, depth_init)
            b.pop()
            if v is None or ret < v:
                v = ret
            if beta > v:
                beta = v

            if alpha >= beta:
                if (depth == depth_init):
                    results[str(i)] = alpha
                return alpha

        if (depth == depth_init):   
            results[str(i)] = beta
        return beta
