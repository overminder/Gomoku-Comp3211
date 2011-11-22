""" entrypoint.py
    The game emulator and visualizer.
"""

def main():
    from board import Board
    from game import CIRCLE
    from ai import Future

    # Initial state
    board = Board()
    board.place_move(10, 10, CIRCLE)

    player = CIRCLE.next_player
    for _ in xrange(10):
        future = Future(board, player)
        future.resolve_as_maximum(2)

        x, y = future.move
        print board.heuristic_values
        board.place_move(x, y, player)
        player = player.next_player
        print board
        print board.heuristic_values
        #print list(board.iter_possible_moves())
        #try:
        #    raw_input('Continue... ')
        #except:
        #    break

if __name__ == '__main__':
    main()

