
class Future(object):
    def __init__(self, board, player):
        self.board = board
        self.player = player
        self.move = None

    def alphabeta(self, depth, alpha, beta, mover):
        if depth == 0:
            self_hval = self.board.hvals[self.player.pid]
            other_hval = sum(hval for pid, hval in enumerate(self.board.hvals)
                             if pid != self.player.pid)
            return self_hval - other_hval

        elif mover is self.player: # max
            saved_pmoves = self.board.possible_moves
            for (x, y) in saved_pmoves:
                self.board.possible_moves = set(saved_pmoves)
                self.board.put_at(x, y, mover)
                next_future = Future(self.board, self.player)
                future_value = next_future.alphabeta(depth - 1, alpha, beta,
                                                     mover.get_next())
                alpha = max(alpha, future_value)
                self.board.del_at(x, y) # Restore the board.
                if beta <= alpha: # beta cutoff
                    break
            self.board.possible_moves = set(saved_pmoves)
            self.move = (x, y)
            return alpha
        else: # min
            saved_pmoves = self.board.possible_moves
            for (x, y) in saved_pmoves:
                self.board.possible_moves = set(saved_pmoves)
                self.board.put_at(x, y, mover)
                next_future = Future(self.board, self.player)
                future_value = next_future.alphabeta(depth - 1, alpha, beta,
                                                     mover.get_next())
                beta = min(beta, future_value)
                self.board.del_at(x, y) # Restore the board.
                if beta <= alpha: # beta cutoff
                    break
            self.board.possible_moves = set(saved_pmoves)
            self.move = (x, y)
            return beta

    def naive_minimax(self, depth, mover):
        best_value = 0
        best_move = None
        if depth == 0:
            self_hval = self.board.hvals[self.player.pid]
            other_hvals = [hval for pid, hval in enumerate(self.board.hvals)
                           if pid != self.player.pid]
            other_hval = 0
            for hval in other_hvals:
                other_hval += hval
            assert isinstance(self_hval, int)
            assert isinstance(other_hval, int)
            return self_hval - other_hval

        elif mover is self.player: # max
            saved_pmoves = self.board.get_possible_moves()
            for i in xrange(len(saved_pmoves)):
                x, y = saved_pmoves[i]
                self.board.set_possible_moves(saved_pmoves)
                self.board.put_at(x, y, mover)
                next_future = Future(self.board, self.player)
                future_value = next_future.naive_minimax(
                        depth - 1, mover.get_next())
                if best_move is None or future_value > best_value:
                    best_value = future_value
                    best_move = [x, y]
                self.board.del_at(x, y) # Restore the board.
            self.board.set_possible_moves(saved_pmoves)
            self.move = best_move
            return best_value
        else: # min
            saved_pmoves = self.board.get_possible_moves()
            for i in xrange(len(saved_pmoves)):
                x, y = saved_pmoves[i]
                self.board.set_possible_moves(saved_pmoves)
                self.board.put_at(x, y, mover)
                next_future = Future(self.board, self.player)
                future_value = next_future.naive_minimax(
                        depth - 1, mover.get_next())
                if best_move is None or future_value < best_value:
                    best_value = future_value
                    best_move = [x, y]
                self.board.del_at(x, y) # Restore the board.
            self.board.set_possible_moves(saved_pmoves)
            self.move = best_move
            return best_value

