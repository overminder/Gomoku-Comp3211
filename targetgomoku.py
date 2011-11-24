import __pypy_path__
from pypy.rlib.objectmodel import we_are_translated
from gamemodel import Board, circle
from ai import Future
from visualize import visualize_board, visualize_stat

def main(argv):
    board = Board()
    board.put_at(9, 9, circle)
    board.put_at(10, 10, circle)
    player = circle.get_next()
    try:
        #while True:
        for _ in xrange(20):
            future = Future(board, player)
            hval = future.naive_minimax(4, player) # minimax
            #hval = future.alphabeta(4, -(1 << 31), (1 << 31), player) # w/prune
            (x, y) = future.move
            board.put_at(x, y, player)
            visualize_board(board)
            visualize_stat(board, player, x, y, hval)
            # test for winner
            if board.piece_groups[player.pid][5]:
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

