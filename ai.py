import functools

class Future(object):
    def __init__(self, board, player):
        from game import PLAYER_COUNT
        self.board = board
        self.player = player
        self.PLAYER_COUNT = PLAYER_COUNT
        self.move = None
        self.value = None

    def resolve_as_minimum(self, depth):
        """ For this player's move, he is going to make the other two's
            total value to be minimum.
        """
        value = None
        move = None
        this_player = self.player
        next_players = functools.reduce(
                lambda builder, _: builder + (builder[-1].next_player,),
                xrange(self.PLAYER_COUNT),
                (this_player.next_player,))
        if depth == 0:
            # Straightforward minimum.
            for (x, y) in self.board.iter_possible_moves():
                new_board = self.board.make_deep_copy()
                new_board.place_move(x, y, this_player)
                total_of_other_two = (
                    sum(new_board.heuristic_value_for(p)
                        for p in next_players) -
                    new_board.heuristic_value_for(this_player))
                if value is None or value > total_of_other_two:
                    value = total_of_other_two
                    move = (x, y)
        else:
            for (x, y) in self.board.iter_possible_moves():
                new_board = self.board.make_deep_copy()
                new_board.place_move(x, y, this_player)
                next_future = Future(new_board, next_players[0])
                next_future.resolve_as_maximum(depth - 1)
                future_value = next_future.value
                if value is None or value > future_value:
                    value = future_value
                    move = (x, y)
        self.value = value
        self.move = move

    def resolve_as_maximum(self, depth):
        """ For this player's move, he is going to make his value
            to be maximum.
        """
        value = None
        move = None
        this_player = self.player
        next_players = functools.reduce(
                lambda builder, _: builder + (builder[-1].next_player,),
                xrange(self.PLAYER_COUNT),
                (this_player.next_player,))
        if depth == 0:
            # Straightforward maximum.
            for (x, y) in self.board.iter_possible_moves():
                new_board = self.board.make_deep_copy()
                new_board.place_move(x, y, this_player)
                future_value = (
                    new_board.heuristic_value_for(this_player) -
                    sum(new_board.heuristic_value_for(p)
                        for p in next_players))
                if value is None or value < future_value:
                    value = future_value
                    move = (x, y)
        else:
            for (x, y) in self.board.iter_possible_moves():
                new_board = self.board.make_deep_copy()
                new_board.place_move(x, y, this_player)
                next_future = Future(new_board, next_players[0])
                next_future.resolve_as_minimum(depth - 1)
                future_value = next_future.value
                if value is None or value < future_value:
                    value = future_value
                    move = (x, y)
        self.value = value
        self.move = move

