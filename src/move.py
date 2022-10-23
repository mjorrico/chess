from functools import cached_property
from typing import List
import numpy as np

black_pieces = ["p", "b", "n", "r", "q", "k"]
white_pieces = ["P", "B", "N", "R", "Q", "K"]


class Move:
    col_to_file = {i: chr(i + 97) for i in range(8)}
    file_to_col = {chr(i + 97): i for i in range(8)}
    row_to_rank = {i: str(8 - i) for i in range(8)}
    rank_to_row = {str(8 - i): i for i in range(8)}

    def __init__(
        self,
        start,
        end,
        board: np.ndarray,
        promote_to=None,
        enpassant_capt_sq: List = None,
    ):
        self.start_row = start[0]
        self.start_col = start[1]
        self.end_row = end[0]
        self.end_col = end[1]
        self.piece_moved = board[self.start_row, self.start_col]
        self.promote_to = promote_to
        self.enpassant_capt_sq = enpassant_capt_sq
        self.piece_captured = (
            board[enpassant_capt_sq[0], enpassant_capt_sq[1]]
            if enpassant_capt_sq
            else board[self.end_row, self.end_col]
        )

    @cached_property
    def chess_notation(self):
        notation = "" if self.piece_moved in ["p", "P"] else self.piece_moved
        notation += self.get_file_rank(self.start_row, self.start_col)
        notation += "x" if self.piece_captured != "." else ""
        notation += self.get_file_rank(self.end_row, self.end_col)
        notation += f"={self.promote_to}" if self.promote_to else ""
        return notation

    def get_file_rank(self, r, c):
        return self.col_to_file[c] + self.row_to_rank[r]

    def __repr__(self):
        return self.chess_notation

    def __eq__(self, other: object) -> bool:
        return (
            self.start_row == other.start_row
            and self.start_col == other.start_col
            and self.end_row == other.end_row
            and self.end_col == other.end_col
            and self.piece_moved == other.piece_moved
            and self.promote_to == other.promote_to
            and self.enpassant_capt_sq == other.enpassant_capt_sq
            and self.piece_captured == other.piece_captured
        )
