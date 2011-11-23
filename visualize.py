from gamemodel import Player

def visualize_board(board):
    buf = ['  /' + '-' * board.size]
    for y, row in enumerate(board.space):
        row_no = str(y)
        if len(row_no) < 2:
            row_no = row_no + ' '

        line = ['%s| ' % row_no]
        for piece in row:
            if piece:
                line.append(piece.owner.mark)
            else:
                line.append(' ')
        buf.append(''.join(line))
    for line in buf:
        print line


NUM2WORD = ['', '', 'dual', 'three', 'four', 'five']

def visualize_stat(board, player, x, y, hval):
    buf = []
    buf.append('[move=(%s, %s, %s), future-hval = %s]' %
               (player.mark, x, y, hval,))
    # and format their owning piece groups.
    for pid, player_stat in enumerate(board.piece_groups):
        stat = ['%s x %d' % (NUM2WORD[length], count)
                 for (length, count) in enumerate(player_stat)
                 if count > 0]
        buf.append('[owning-groups for %s -- %s]' % (
                Player.cache[pid].name, ', '.join(stat)))

    for line in buf:
        print line

