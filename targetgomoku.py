import __pypy_path__
from pypy.rlib.objectmodel import we_are_translated

from board import Board
from model import circle
from ai import Future
from visualize import visualize_board, visualize_stat

def main(argv):
    try:
        search_depth = int(argv[1])
    except (IndexError, ValueError):
        search_depth = 4

    try:
        round_limit = int(argv[2])
    except (IndexError, ValueError):
        round_limit = 99999

    board = Board()
    board.put_at(10, 10, circle)
    player = circle.get_next()

    try:
        for _ in xrange(round_limit):
            future = Future(board, player)
            # w/pruning.
            hval = future.alphabeta(search_depth,
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
        if we_are_translated():
            pass
        else:
            raise
    return 0

def target(driver, argl):
    driver.exe_name = 'gomoku-c'
    return main, None

if __name__ == '__main__':
    main([])

