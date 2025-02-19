from os.path import abspath
import numpy as np
import copy
import torch
import os

from src.learn.BaseNNBot import BaseNNBot
from src.play.model.Board import EMPTY, BLACK, WHITE
from src.play.model.Move import Move
from src.learn.pytorch.SimpleWinPredNN import SimpleWinPredNN


class PytorchBot(BaseNNBot):

    def __init__(self):
        # super().__init__()
        self.model = SimpleWinPredNN(
            input_dim=3*81, output_dim=2, hidden_dim=100)
        model_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'model.pt')
        self.model.load_state_dict(torch.load(model_path))

    def get_path_to_self(self):
        return abspath(__file__)

    @staticmethod
    def board_to_input(flat_board):
        X = np.concatenate(
            ((flat_board==WHITE)*3 - 1,
             (flat_board==BLACK)*3 - 1,
             (flat_board==EMPTY)*3 - 1),
            axis=1)
        X = X / np.sqrt(2)

        X = torch.autograd.Variable(torch.from_numpy(X).float())

        return X

    def __str__(self):
        return 'WinPredictionBot'

    def _genmove(self, color, game, flat_board):
        flat_board = flat_board.reshape(1, len(flat_board))

        inp = self.board_to_input(flat_board)
        current_pred = self.model.forward(inp)

        my_index = 0 if color == 'b' else 1
        my_pred = current_pred[0, my_index]
        my_value = BLACK if color == 'b' else WHITE

        # We're still interested in the playable locations
        playable_locations = game.get_playable_locations(color)
        results = np.zeros(game.board.shape)
        for move in playable_locations:
            if move.is_pass:
                continue

            test_board = copy.deepcopy(game.board)
            test_board.place_stone_and_capture_if_applicable_default_values(
                move.to_matrix_location(), my_value)
            inp = self.board_to_input(test_board.flatten())
            pred_result = self.model.forward(inp)
            # pred_result = self.softmax(pred_result)

            results[move.to_matrix_location()] = pred_result[0, my_index]

        results -= my_pred.data.numpy()

        row, col = np.unravel_index(
            results.argmax(),
            results.shape)

        move = Move(col=col, row=row)
        if (results[move.to_matrix_location()] <= 0):
            move = Move(is_pass=True)

        return move
