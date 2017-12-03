import os
import sgf
import glob
import time
import string
import sqlite3
from os.path import dirname, abspath
from src.play.model.Board import Board, EMPTY, BLACK, WHITE


project_root_dir = dirname(dirname(dirname(abspath(__file__))))  # GO_DILab
data_dir = os.path.join(project_root_dir, 'data')

db_name = 'db.sqlite'
db_path = os.path.join(data_dir, db_name)

if os.path.exists(db_path):
    print('connecting to existing db: ' + db_name)
else:
    print('creating new db and connecting to it: ' + db_name)

db = sqlite3.connect(db_path)
cursor = db.cursor()

flat_matrix_table_column_names = []
for row in range(0, 9):
    for col in range(0, 9):
        flat_matrix_table_column_names.append('loc_' + str(row) + '_' + str(col) + '_' + str(row * 9 + col))


def setup():
    print('creating tables meta and games')
    cursor.execute('CREATE TABLE meta(id INTEGER PRIMARY KEY, all_moves_imported INTEGER, sgf_content TEXT)')
    db.commit()
    cursor.execute('CREATE TABLE games(id INTEGER, color INTEGER, move INTEGER'
                   + ''.join([', ' + _str + ' INTEGER' for _str in flat_matrix_table_column_names]) + ')')
    db.commit()


def import_data():
    sgf_dir = os.path.join(data_dir, 'dgs')
    if not os.path.exists(sgf_dir):
        print(sgf_dir + ' does not exist')
        exit(1)
    sgf_files = glob.glob(os.path.join(sgf_dir, '*'))
    if len(sgf_files) is 0:
        print('no sgf files in ' + sgf_dir)
        exit(1)

    table_insert_command = 'INSERT INTO games(id, color, move' \
                           + ''.join([', ' + _str for _str in flat_matrix_table_column_names]) + ') ' \
                           + 'VALUES(' + ''.join(['?,' for i in range(0, 84)])[:-1] + ')'

    print('importing ' + str(len(sgf_files)) + ' sgf-files into ' + db_name + '...')

    start_time = time.time()

    for i, path in enumerate(sgf_files):
        # not ignoring errors caused UnicodeDecodeError: 'ascii' codec can't decode byte 0xf6
        sgf_file = open(path, 'r', errors='ignore')  # via stackoverflow.com/a/12468274/2474159
        filename = os.path.basename(path)
        elapsed_time = time.time() - start_time
        time_remaining_str = ''
        if i > 0:
            time_remaining = (elapsed_time / i) * (len(sgf_files) - i)
            time_remaining_str = '~' + '{0:.0f}'.format(time_remaining) + 's remaining'

        print(filename + '\t' + str(i) + '/' + str(len(sgf_files)) + '\t'
              + '{0:.2f}'.format((i / len(sgf_files)) * 100) + '%\t'
              + '{0:.0f}'.format(elapsed_time) + 's elapsed\t' + time_remaining_str)

        game_id = int(filename.split('_')[1][:-4])  # get x in game_x.sgf
        sgf_content = sgf_file.read().replace('\n', '')
        sgf_file.close()
        collection = sgf.parse(sgf_content)
        game_tree = collection.children[0]
        moves = game_tree.nodes[1:]
        board = Board([[EMPTY] * 9] * 9)

        all_moves_imported = True

        for j, move in enumerate(moves):
            keys = move.properties.keys()
            if 'B' not in keys and 'W' not in keys:  # don't know how to deal with special stuff (yet?)
                all_moves_imported = False
                break  # or just continue? would are the moves afterwards still definitely be useful? not sure
            # can't rely on the order in keys(), apparently must extract it like this
            player_color = 'B' if 'B' in move.properties.keys() else 'W'
            player_val = BLACK if player_color == 'B' else WHITE
            sgf_move = move.properties[player_color][0]

            flat_move = -1
            if len(sgf_move) is 2:  # otherwise its a pass
                _row = string.ascii_lowercase.index(sgf_move[1])
                _col = string.ascii_lowercase.index(sgf_move[0])
                flat_move = _row * 9 + _col
                board.place_stone_and_capture_if_applicable_default_values((_row, _col), player_val)

            values = [game_id, player_val, flat_move]
            flat_matrix = [val for _row in board.tolist() for val in _row]
            values.extend(flat_matrix)
            cursor.execute(table_insert_command, values)

        cursor.execute('INSERT INTO meta(id, all_moves_imported, sgf_content) VALUES(?,?,?)',
                       (game_id, all_moves_imported, sgf_content))
        db.commit()


setup()
import_data()

db.close()