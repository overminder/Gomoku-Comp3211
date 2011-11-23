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
            (x, y) = future.move
            board.put_at(x, y, player)
            visualize_board(board)
            visualize_stat(board, player, x, y, hval)
            player = player.get_next()
    except KeyboardInterrupt:
        pass
    return 0

def target(driver, argl):
    driver.exe_name = 'gomoku-c'
    return main, None

if __name__ == '__main__':
    main([])

