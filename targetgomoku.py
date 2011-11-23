from gamemodel import Board, circle
from ai import Future

def main(argv):
    board = Board()
    board.put_at(10, 10, circle)
    player = circle.get_next()
    try:
        while True:
            future = Future(board, player)
            #hval = future.alphabeta(5, -(1 << 61), (1 << 61), player)
            hval = future.naive_minimax(4, player)
            (x, y) = future.move
            board.put_at(x, y, player)

            print board.get_state()
            print ('[move=(%s, %s, %s), future-hval = %s, hvals=%s] ' %
                      (player.mark, x, y, hval, board.hvals))
            player = player.get_next()
    except KeyboardInterrupt:
        pass
    return 0

def target(*argl):
    return main, None

if __name__ == '__main__':
    main([])

