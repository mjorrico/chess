"""
This class is responsible to store current game state and deciding all valid moves.
"""
from numpy import array
from move import Move

black_pieces = ["p", "b", "n", "r", "q", "k"]
white_pieces = ["P", "B", "N", "R", "Q", "K"]


class Chessboard:
    def __init__(self):
        self.board = array(
            [
                ["r", "n", "b", "q", "k", "b", "n", "r"],
                ["p", "p", "p", "p", "p", "p", "p", "p"],
                [".", ".", ".", ".", ".", ".", ".", "."],
                [".", ".", ".", ".", ".", ".", ".", "."],
                [".", ".", ".", ".", ".", ".", ".", "."],
                [".", ".", ".", ".", ".", ".", ".", "."],
                ["P", "P", "P", "P", "P", "P", "P", "P"],
                ["R", "N", "B", "Q", "K", "B", "N", "R"],
            ]
        )

        self.white_to_move = True
        self.move_log = []

    def make_move(self, m: Move):
        self.board[m.start_row, m.start_col] = m.piece_moved
        self.board[m.end_row, m.end_col] = "."
        self.white_to_move = not self.white_to_move
        self.move_log.append(m)

    def undo_move(self):
        if len(self.move_log) != 0:
            m: Move = self.move_log.pop()
            self.board[m.start_row, m.start_col] = m.piece_moved
            self.board[m.end_row, m.end_col] = m.piece_captured
            self.white_to_move = not self.white_to_move

    def get_valid_moves(self):  # removes invalid possible moves
        return self.get_possible_moves()

    def get_possible_moves(self):  # moves returned may be invalid
        foe_pieces = black_pieces if self.white_to_move else white_pieces
        for i in range(8):
            for j in range(8):
                current_piece = self.board[i, j]
                if current_piece == "." or current_piece in foe_pieces:
                    continue
                else:
                    if current_piece.lower() == "p":
                        pass
                    elif current_piece.lower() == "b":
                        pass
                    elif current_piece.lower() == "n":
                        pass
                    elif current_piece.lower() == "r":
                        pass
                    elif current_piece.lower() == "q":
                        pass
                    elif current_piece.lower() == "k":
                        pass
                    else:
                        raise ValueError("[CHESS_ERROR] The piece is unknown")

    def get_pawn_moves(self, r, c):
        pass

    def get_bishop_moves(self, r, c):
        pass

    def get_knight_moves(self, r, c):
        pass

    def get_rook_moves(self, r, c):
        pass

    def get_queen_moves(self, r, c):
        pass

    def get_king_moves(self, r, c):
        pass

    def __str__(self):
        info_1 = "\nWhite to move" if self.white_to_move else "\nBlack to move"
        return str(self.board) + info_1
