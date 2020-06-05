import signal, os
from random import choice
import time
import alphaBeta
import negaMax
import alphaBetaThreaded
import multiprocessing
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
class IDS():

    def __init__(self, color):
        self._mycolor = color
        self.AB = alphaBeta.AlphaBeta(color)
        self.NG = negaMax.NegaMax(color)
        self.ABT = alphaBetaThreaded.AlphaBetaThreaded(color)


    def IDS_AB(self, b, timeRange, turn):
            """ Iterative deepening search for Alpha Beta"""

            # pour retourner une valeur au cas ou le temps est expiré.
            best_move, v = choice(list(b.generate_legal_moves())), 0
            depth = 1

            with timeout(timeRange):
                while (True):
                    t = time.time()
                    move, v = self.AB.AlphaBetaCoup(b, depth, turn)
                    #print("depth : ", depth, " time: ", time.time() -
                    #    t, " move : ", b.flat_to_name(move))
                    best_move = move

                    depth += 1

            return best_move, v

    def IDS_NG(self, b, timeRange, turn):
        """ Iterative deepening search for NegaMax"""

        # pour retourner une valeur au cas ou le temps est expiré.
        best_move, v = choice(list(b.generate_legal_moves())), 0
        depth = 1

        with timeout(timeRange):
            while (True):
                t = time.time()
                move, v = self.NG.Negamax_coup(b, depth, turn)
                #print("depth : ", depth, " time: ", time.time() -
                #        t, " move : ", b.flat_to_name(move))
                best_move = move

                depth += 1

        return best_move, v


    def IDS_AB_threaded2(self, b, timeRange):
        #Iterative deepening search for Alpha Beta

        # pour retourner une valeur au cas ou le temps est expiré.
        best_move, v = choice(list(b.generate_legal_moves())), 0
        depth = 1

        with timeout(timeRange):
            while (True):
                t = time.time()
                move, v = self.ABT.AlphaBetaCoupThreaded(b, depth)
                #print("depth : ", depth, " time: ", time.time() -
                #    t, " move : ", b.flat_to_name(move))
                best_move = move
                depth += 1
        return best_move, v

    def AB_loop(self, b, results):
        depth = 1
        while (True):
            t = time.time()

            move, v = self.ABT.AlphaBetaCoupThreaded(b, depth)
            #print("depth : ", depth, " time: ", time.time() - t, " move : ", b.flat_to_name(move))
            
            best_move = move
            results['move'], results['value'] = move, v
            depth += 1
    

    def IDS_AB_threaded(self, b, timeRange):

        manager = multiprocessing.Manager()
        results = manager.dict()

        p = multiprocessing.Process(target=self.AB_loop, name="Foo", args=(b, results))
        p.start()
        p.join(timeRange)
        for p in self.ABT._processes:
            p.terminate()

        if p.is_alive():
            p.terminate()
            p.join()
        
        #print("move, value: ", results['move'], results['value'])
        return results['move'], results['value']

