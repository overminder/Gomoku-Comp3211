""" ai.py

    Contains implementation for naive minimax and alpha-beta-pruning.

    TODO: better end-state predication. <- Done
          heuristic function that is more precise (take open/close into
          consideration) <- Done but could there be any efficiency improvement?
          Three-player minimax/alpha-beta-pruning <- Hmmm...
"""

class Future(object):
    def __init__(self, board, player):
        self.board = board
        self.player = player
        self.move = None

    def heuristic_eval(self):
        # XXX: using different marking scheme on self/enemy players?

        # evaluating the max player's heuristic value.
        self_hval = 0
        self_group_man = self.board.get_piece_groups()[self.player.pid]
        for piece_groups in self_group_man.get_groups():
            for piece_group in piece_groups:
                self_hval += piece_group.heuristic_eval(self.board)

        # evaluating the sum of the enemy players' heuristic values.
        enemy_hvals = 0
        for pid, group_man in enumerate(self.board.get_piece_groups()):
            if pid == self.player.pid:
                continue
            for piece_groups in group_man.get_groups():
                for piece_group in piece_groups:
                    enemy_hvals += piece_group.heuristic_eval(self.board)

        return self_hval - 2 * enemy_hvals

    def alphabeta(self, depth, alpha, beta, mover):
        if depth == 0:
            # leaf reached -- just get the heuristic value
            return self.heuristic_eval()
        elif self.board.get_piece_groups()[mover.get_prev().pid].count_of(5):
            # ending case -- someone is winning here.
            return self.heuristic_eval()
        elif mover is self.player: # max move
            saved_pmoves = self.board.get_possible_moves()
            pm_iter = saved_pmoves.get_iterator()
            while pm_iter.has_next():
                (x, y) = pm_iter.get_next()
                self.board.set_possible_moves(saved_pmoves.make_copy())
                self.board.put_at(x, y, mover)
                next_future = Future(self.board, self.player)
                future_value = next_future.alphabeta(depth - 1,
                        alpha, beta, mover.get_next())
                self.board.del_at(x, y) # Restore the board.
                if future_value > alpha:
                    alpha = future_value
                    self.move = [x, y]
                if beta <= alpha:
                    break
            self.board.set_possible_moves(saved_pmoves)
            return alpha
        else: # min move
            saved_pmoves = self.board.get_possible_moves()
            pm_iter = saved_pmoves.get_iterator()
            while pm_iter.has_next():
                (x, y) = pm_iter.get_next()
                self.board.set_possible_moves(saved_pmoves.make_copy())
                self.board.put_at(x, y, mover)
                next_future = Future(self.board, self.player)
                future_value = next_future.alphabeta(depth - 1,
                        alpha, beta, mover.get_next())
                self.board.del_at(x, y) # Restore the board.
                if future_value < beta:
                    beta = future_value
                    self.move = [x, y]
                if beta <= alpha:
                    break
            self.board.set_possible_moves(saved_pmoves)
            return beta

    def naive_minimax(self, depth, mover):
        best_value = 0
        best_move = None
        if depth == 0:
            return self.heuristic_eval()
        elif mover is self.player: # max
            saved_pmoves = self.board.get_possible_moves()
            pm_iter = saved_pmoves.get_iterator()
            while pm_iter.has_next():
                (x, y) = pm_iter.get_next()
                self.board.set_possible_moves(saved_pmoves.make_copy())
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
            pm_iter = saved_pmoves.get_iterator()
            while pm_iter.has_next():
                (x, y) = pm_iter.get_next()
                self.board.set_possible_moves(saved_pmoves.make_copy())
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

