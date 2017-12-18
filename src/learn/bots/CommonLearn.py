"""Intermediary class to define the common setup and add some funcitons

The multiple bots here are just all combinations of input and output type
presented in the markdown. It therefore makes sense to define the
generation of those data formats here, as they will be shared accross
multiple bots.
"""
import numpy as np

from keras.models import Sequential
from keras.layers import Dense, Dropout

from src.learn.BaseLearn import BaseLearn


class CommonLearn(BaseLearn):

    def __init__(self):
        super().__init__()
        np.random.seed(1234)
        # Training size is here not the number of rows, but of games!
        self.training_size = 10
        # Results in 77016 rows, counting symmetries
        self.data_retrieval_command = '''
            WITH relevant_games as (
                SELECT id,
                    CASE WHEN elo_black <= elo_white THEN elo_black
                    WHEN elo_white <= elo_black THEN elo_white
                    END AS min_elo
                FROM meta
                WHERE elo_white != ""
                AND elo_black != ""
                AND turns > 30
                ORDER BY min_elo DESC
                LIMIT ?)
            SELECT games.*, meta.result
            FROM relevant_games, games, meta
            WHERE relevant_games.id == games.id
            AND games.id == meta.id
            AND meta.result != 'Draw'
            AND meta.result != 'Time'
            AND meta.all_moves_imported!=0'''

    def setup_and_compile_model(self):
        model = Sequential()
        model.add(Dense(100, input_dim=self.input_dim, activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(self.output_dim, activation='softmax'))
        model.compile(
            loss='categorical_crossentropy',
            optimizer='adam',
            metrics=['accuracy'])
        return model

    def train(self, model, X, Y):
        model.fit(X, Y, epochs=8, batch_size=10000)


if __name__ == '__main__':
    CommonLearn().run()