"""Read a single SGF file and recreate the game"""
# TODO think about if/how to integrate this into the GUI-workflow as importer
import sgf
import sys
from Game import Game
from archive.src.play.utils.Utils import str2move

sys.path.append('.')

file = '../example_data/some_game.sgf'
with open(file, 'r') as f:
    content = f.read()
    collection = sgf.parse(content)

# Assume the sgf file contains one game
game_tree = collection.children[0]
n_0 = game_tree.nodes[0]
# n_0.properties contains the initial game setup
board_size = int(n_0.properties['SZ'][0])

game = Game(n_0.properties, show_each_turn=True)
for node in game_tree.nodes[1:]:
    player_color = list(node.properties.keys())[0]
    move_str = str(node.properties[player_color][0])
    move = str2move(move_str, board_size)
    game.play(move, player_color.lower())

game.evaluate_points()
