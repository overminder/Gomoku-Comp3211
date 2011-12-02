""" targetvisualize.py

    The entrypoint for visualizing ai players fighting.
"""
import __pypy_path__
from pypy.rlib.objectmodel import we_are_translated

from board import Board
from model import circle
from ai import Future
from visualize import visualize_board, visualize_stat

DEFAULT_ROUND_LIMIT = 99999

def main(argv):
    try:
        search_depth = int(argv[1])
    except (IndexError, ValueError):
        print 'usage: %s [SearchDepth [RoundLimit=%s]]' % (
                argv[0], DEFAULT_ROUND_LIMIT)
        return 1

    try:
        round_limit = int(argv[2])
    except (IndexError, ValueError):
        round_limit = DEFAULT_ROUND_LIMIT

    board = Board()
    board.put_at(10, 10, circle)
    player = circle.get_next()

    try:
        for _ in xrange(round_limit):
            future = Future(board, player)
            #hval = future.naive_minimax(search_depth, player)
            # w/pruning.
            #val = future.alphabeta(search_depth,
            #                        -(1 << 60), (1 << 60), player)
            hval = future.alphabeta_3p(search_depth,
                                       -(1 << 60), (1 << 60), player)
            (x, y) = future.move
            board.put_at(x, y, player)
            visualize_board(board)
            visualize_stat(board, player, x, y, hval)
            # test for winner
            if board.piece_groups[player.pid].count_of(5) != 0:
                print 'player %s wins' % player.name
                break
            player = player.get_next()
    except KeyboardInterrupt:
        pass
    return 0

def target(driver, argl):
    driver.exe_name = 'visualize-c'
    return main, None

if __name__ == '__main__':
    import sys
    main(sys.argv)
