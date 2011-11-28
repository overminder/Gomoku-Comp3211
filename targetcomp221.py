""" targetcomp221.py

    The entrypoint for compile comp221 project.
"""

import __pypy_path__
from ai import Future
from comp221io import load_game

DEFAULT_SEARCH_DEPTH = 3

def main(argv):
    try:
        filename = argv[1]
    except IndexError:
        print 'usage: %s [FileName [SearchDepth=3]]' % argv[0]
        return 1
    try:
        (player, board) = load_game(filename)
    except OSError:
        print '%s: %s: cannot open this file' % (argv[0], filename)
        return 1

    try:
        search_depth = int(argv[2])
    except (IndexError, ValueError):
        search_depth = DEFAULT_SEARCH_DEPTH

    try:
        while True:
            future = Future(board, player)
            future.alphabeta_3p(search_depth, -(1 << 60), (1 << 60), player)
            future.dump()
            x, y = future.move
            board.put_at(x, y, player)
            player = player.get_next()
    except KeyboardInterrupt:
        print '[interrupt] received SIGINT, halting...'
    return 0

def target(driver, argl):
    driver.exe_name = 'comp221-c'
    return main, None

if __name__ == '__main__':
    import sys
    main(sys.argv)


