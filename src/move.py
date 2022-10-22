import numpy as np

black_pieces = ["p", "b", "n", "r", "q", "k"]
white_pieces = ["P", "B", "N", "R", "Q", "K"]


class Move:
    col_to_file = {i: chr(i + 97) for i in range(8)}
    file_to_col = {chr(i + 97): i for i in range(8)}
    row_to_rank = {i: str(8 - i) for i in range(8)}
    rank_to_row = {str(8 - i): i for i in range(8)}

    def __init__(self, start, end, board: np.ndarray):
        self.start_row = start[0]
        self.start_col = start[1]
        self.end_row = end[0]
        self.end_col = end[1]
        self.piece_moved = board[self.start_row, self.start_col]
        self.piece_captured = board[self.end_row, self.end_col]

    @property
    def chess_notation(self):
        prefix = self.piece_moved + self.get_file_rank(
            self.start_row, self.start_col
        )
        prefix += "x" if self.piece_captured != "." else ""
        return prefix + self.get_file_rank(self.end_row, self.end_col)

    def get_file_rank(self, r, c):
        return self.col_to_file[c] + self.row_to_rank[r]
