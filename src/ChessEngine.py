"""
This class is responsible to store current game state and listing all valid moves.
"""
from numpy import array, concatenate, reshape
from move import Move

from chesserror import ChessError

black_pieces = ["p", "n", "b", "r", "q", "k"]
white_pieces = ["P", "N", "B", "R", "Q", "K"]


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

    @property
    def foe_pieces(self):
        return black_pieces if self.white_to_move else white_pieces

    @property
    def friend_pieces(self):
        return white_pieces if self.white_to_move else black_pieces

    def make_move(self, m: Move):
        if m not in self.get_valid_moves():
            raise ChessError(f"Invalid move {m}")

        self.board[m.end_row, m.end_col] = (
            m.promote_to
            if m.promote_to
            else self.board[m.start_row, m.start_col]
        )
        self.board[m.start_row, m.start_col] = "."
        self.white_to_move = not self.white_to_move
        self.move_log.append(m)

    def undo_move(self):
        if len(self.move_log) != 0:
            m: Move = self.move_log.pop()
            self.board[m.start_row, m.start_col] = m.piece_moved
            self.white_to_move = not self.white_to_move
            if m.enpassant_capt_sq is None:
                self.board[m.end_row, m.end_col] = m.piece_captured
            else:
                enpassant_row = m.enpassant_capt_sq[0]
                enpassant_col = m.enpassant_capt_sq[1]
                self.board[m.end_row, m.end_col] = "."
                self.board[enpassant_row, enpassant_col] = 3

    def get_valid_moves(self):  # removes invalid moves from possible moves
        return self.get_possible_moves()

    def get_possible_moves(self):  # moves returned may be invalid
        all_possible_moves = []

        for i in range(8):
            for j in range(8):
                current_piece = self.board[i, j]
                if current_piece == "." or current_piece in self.foe_pieces:
                    continue
                else:
                    if current_piece.lower() == "p":
                        all_possible_moves += self.get_pawn_moves(i, j)
                    elif current_piece.lower() == "b":
                        all_possible_moves += self.get_bishop_moves(i, j)
                    elif current_piece.lower() == "n":
                        all_possible_moves += self.get_knight_moves(i, j)
                    elif current_piece.lower() == "r":
                        all_possible_moves += self.get_rook_moves(i, j)
                    elif current_piece.lower() == "q":
                        all_possible_moves += self.get_queen_moves(i, j)
                    elif current_piece.lower() == "k":
                        all_possible_moves += self.get_king_moves(i, j)
                    else:
                        raise ChessError("The piece is unknown")

        return all_possible_moves

    def get_pawn_moves(self, r, c):
        pawn_moves = []

        if self.white_to_move:  # moving white pawn

            # just pawn move
            if self.board[r - 1, c] == ".":
                if r == 1:  # promotion
                    for p in self.friend_pieces[1:-1]:
                        pawn_moves.append(Move([1, c], [0, c], self.board, p))
                else:
                    pawn_moves.append(Move([r, c], [r - 1, c], self.board))
                    if r == 6 and self.board[4, c] == ".":  # double move
                        pawn_moves.append(Move([6, c], [4, c], self.board))

            # pawn move with regular capture
            capt_moves = [
                None if c == col else [r - 1, c + i]
                for col, i in zip([0, 7], [-1, 1])
            ]
            for m in capt_moves:
                if m is not None and self.board[m[0], m[1]] in self.foe_pieces:
                    if r == 1:  # capture and promote
                        for p in self.friend_pieces[1:-1]:
                            pawn_moves.append(Move([r, c], m, self.board, p))
                    else:  # just capture
                        pawn_moves.append(Move([r, c], m, self.board))

            # pawn move with enpassant capture
            if r == 3:
                last_move: Move = self.move_log[-1]
                if (
                    last_move.piece_moved == self.foe_pieces[0]  # enemy's pawn
                    and last_move.start_row == 1
                    and last_move.end_row == 3  # double move
                    and abs(last_move.start_col - c) == 1  # column diff is 1
                ):
                    end_col = last_move.start_col  # or last_move.end_col
                    pawn_moves.append(
                        Move(
                            [r, c],
                            [2, end_col],
                            self.board,
                            None,
                            [3, end_col],
                        )
                    )

        else:  # moving black pawn

            # just pawn move
            if self.board[r + 1, c] == ".":
                if r == 6:  # promotion
                    for p in self.friend_pieces[1:-1]:
                        pawn_moves.append(Move([6, c], [7, c], self.board, p))
                else:
                    pawn_moves.append(Move([r, c], [r + 1, c], self.board))
                    if r == 1 and self.board[3, c] == ".":  # double move
                        pawn_moves.append(Move([1, c], [3, c], self.board))

            # pawn move with regular capture
            capt_moves = [
                None if c == col else [r + 1, c + i]
                for col, i in zip([0, 7], [-1, 1])
            ]
            for m in capt_moves:
                if m is not None and self.board[m[0], m[1]] in self.foe_pieces:
                    if r == 6:  # capture and promote
                        for p in self.friend_pieces[1:-1]:
                            pawn_moves.append(Move([r, c], m, self.board, p))
                    else:  # just capture
                        pawn_moves.append(Move([r, c], m, self.board))

            # pawn move with enpassant capture
            if r == 4:
                last_move: Move = self.move_log[-1]
                if (
                    last_move.piece_moved == self.foe_pieces[0]  # enemy's pawn
                    and last_move.start_row == 6
                    and last_move.end_row == 4  # double move
                    and abs(last_move.start_col - c) == 1  # column diff is 1
                ):
                    end_col = last_move.start_col  # or last_move.end_col
                    pawn_moves.append(
                        Move(
                            [r, c],
                            [5, end_col],
                            self.board,
                            None,
                            [4, end_col],
                        )
                    )

        return pawn_moves

    def get_bishop_moves(self, r, c):
        bishop_moves = []

        return bishop_moves

    def get_knight_moves(self, r, c):
        knight_moves = []

        return knight_moves

    def get_rook_moves(self, r, c):
        rook_moves = []

        return rook_moves

    def get_queen_moves(self, r, c):
        queen_moves = []

        return queen_moves

    def get_king_moves(self, r, c):
        king_moves = []

        return king_moves

    def __str__(self):
        indexing_ui = array([["x", "0", "1", "2", "3", "4", "5", "6", "7"]])
        board_ui = concatenate((indexing_ui[:, 1:], self.board), axis=0)
        board_ui = concatenate((indexing_ui.T, board_ui), axis=1)
        info_1 = "\nWhite to move" if self.white_to_move else "\nBlack to move"
        return str(board_ui) + info_1
