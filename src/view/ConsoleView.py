from src.view import View

from src.model.Game import BLACK
from src.model.Game import WHITE


class ConsoleView(View):

    def __init__(self, game):
        View.__init__(self, game)

    def update_view(self):
        # Just a simple ascii output, quite cool but the code is a bit messy"""
        b = self.game.board.copy()
        # You might wonder why I do the following, but its so that numpy
        # formats the str representation using a single space
        b[b == BLACK] = 2
        b[b == WHITE] = 3

        matrix_repr = str(b)
        matrix_repr = matrix_repr.replace('2', 'X')
        matrix_repr = matrix_repr.replace('3', 'O')
        matrix_repr = matrix_repr.replace('0', '·')
        matrix_repr = matrix_repr.replace('[[', ' [')
        matrix_repr = matrix_repr.replace(']]', ']')
        col_index = '   a b c d e f g h i'
        row_index = 'a,b,c,d,e,f,g,h,i'.split(',')
        board_repr = ''
        for i in zip(row_index, matrix_repr.splitlines()):
            board_repr += i[0] + i[1] + '\n'
        board_repr = col_index + '\n' + board_repr

        print(board_repr)