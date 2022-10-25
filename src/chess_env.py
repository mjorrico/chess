"""
This class is responsible to store current game state and listing all valid moves.
"""
from typing import Iterable
from numpy import array, concatenate
from chess_error import ChessError
from move import Move

import itertools

black_pieces = "pnbrqk"
white_pieces = "PNBRQK"

diag_movements = list(itertools.product([1, -1], [1, -1]))
rook_movements = [[0, -1], [-1, 0], [0, 1], [1, 0]]  # straight movements
L_movements = [
    [-2, -1],  # going up twice and going left once
    [-2, 1],
    [-1, 2],
    [1, 2],
    [2, 1],
    [2, -1],
    [1, -2],
    [-1, -2],
]
king_movements = [
    [i, j] for i in [-1, 0, 1] for j in [-1, 0, 1] if (i != 0 or j != 0)
]


def is_valid_loc(row, col):
    return 0 <= row <= 7 and 0 <= col <= 7


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
        self.white_castles = [True, True]  # queenside, kingside
        self.black_castles = [True, True]  # kingside, queenside

    @property
    def foe_pieces(self):
        return black_pieces if self.white_to_move else white_pieces

    @property
    def friend_pieces(self):
        return white_pieces if self.white_to_move else black_pieces

    def make_move(self, m: Move):
        if m not in self.get_valid_moves():
            raise ChessError(f"invalid move {m}")

        self.board[m.end_row, m.end_col] = (
            m.promote_to
            if m.promote_to
            else self.board[m.start_row, m.start_col]
        )
        self.board[m.start_row, m.start_col] = "."

        if m.enpassant_capt_sq:
            ep_row = m.enpassant_capt_sq[0]
            ep_col = m.enpassant_capt_sq[1]
            self.board[ep_row, ep_col] = "."

        if m.piece_moved == "K":
            self.white_castles = [False, False]
        elif m.piece_moved == "k":
            self.black_castles = [False, False]

        # check if rook has moved
        if self.white_castles[0]:  # False if white can't castle queeenside
            self.white_castles[0] = self.board[-1, 0] == "R"
        if self.white_castles[1]:
            self.white_castles[1] = self.board[-1, -1] == "R"
        if self.black_castles[0]:
            self.black_castles[0] = self.board[0, 0] == "r"
        if self.black_castles[1]:
            self.black_castles[1] = self.board[0, -1] == "r"

        if m.is_castling:
            rook_row, which_rook = [7, "R"] if self.white_to_move else [0, "r"]
            rook_col, rook_col_new = (
                [0, 3] if m.is_castling == "queenside" else [7, 5]
            )

            self.board[rook_row, rook_col_new] = which_rook
            self.board[rook_row, rook_col] = "."

        self.white_to_move = not self.white_to_move
        self.move_log.append(m)

        v = self.get_valid_moves()
        print(v, len(v), end="\n\n")

    def undo_move(self):
        if len(self.move_log) > 0:
            m: Move = self.move_log.pop()
            self.board[m.start_row, m.start_col] = m.piece_moved
            self.white_to_move = not self.white_to_move
            if m.enpassant_capt_sq is None:
                self.board[m.end_row, m.end_col] = m.piece_captured
            else:
                enpassant_row = m.enpassant_capt_sq[0]
                enpassant_col = m.enpassant_capt_sq[1]
                self.board[m.end_row, m.end_col] = "."
                self.board[enpassant_row, enpassant_col] = "p"

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
                        all_possible_moves += self.get_bshp_moves(i, j)
                    elif current_piece.lower() == "n":
                        all_possible_moves += self.get_kght_moves(i, j)
                    elif current_piece.lower() == "r":
                        all_possible_moves += self.get_rook_moves(i, j)
                    elif current_piece.lower() == "q":
                        all_possible_moves += self.get_bshp_moves(i, j)
                        all_possible_moves += self.get_rook_moves(i, j)
                    elif current_piece.lower() == "k":
                        all_possible_moves += self.get_king_moves(i, j)
                        all_possible_moves += self.get_ctle_moves()
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
                    pawn_moves.append(Move([r, c], [2, end_col], self.board))

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
                    pawn_moves.append(Move([r, c], [5, end_col], self.board))

        return pawn_moves

    def get_bshp_moves(self, r, c):
        return self.get_straight_moves(r, c, diag_movements)

    def get_rook_moves(self, r, c):
        return self.get_straight_moves(r, c, rook_movements)

    def get_straight_moves(self, r, c, movetype_list: Iterable):
        moves = []

        for movetype in movetype_list:
            new_row, new_col = r, c
            while True:
                new_row += movetype[0]
                new_col += movetype[1]
                if is_valid_loc(new_row, new_col):
                    target_piece = self.board[new_row, new_col]
                    if target_piece in self.friend_pieces:
                        break
                    else:
                        moves.append(
                            Move([r, c], [new_row, new_col], self.board)
                        )
                        if target_piece != ".":  # if it is enemy's piece
                            break
                else:  # going out of bound
                    break

        return moves

    def get_kght_moves(self, r, c):
        return self.get_fixed_moves(r, c, L_movements)

    def get_king_moves(self, r, c):
        return self.get_fixed_moves(r, c, king_movements)

    def get_fixed_moves(self, r, c, movetype_list: Iterable):
        moves = []

        for movetype in movetype_list:
            new_row = r + movetype[0]
            new_col = c + movetype[1]
            if is_valid_loc(new_row, new_col):
                target_piece = self.board[new_row, new_col]
                if target_piece in "." + self.foe_pieces:
                    moves.append(Move([r, c], [new_row, new_col], self.board))

        return moves

    def get_ctle_moves(self):  # get possible castling moves
        castle_moves = []

        if self.white_to_move:
            if self.white_castles[0] and all(self.board[-1, 1:4] == "."):
                castle_moves.append(Move([7, 4], [7, 2], self.board))
            if self.white_castles[1] and all(self.board[-1, 5:7] == "."):
                castle_moves.append(Move([7, 4], [7, 6], self.board))
        else:
            if self.black_castles[0] and all(self.board[0, 1:4] == "."):
                castle_moves.append(Move([0, 4], [0, 2], self.board))
            if self.black_castles[1] and all(self.board[0, 5:7] == "."):
                castle_moves.append(Move([0, 4], [0, 6], self.board))

        return castle_moves

    def __str__(self):
        indexing_ui = array([["x", "0", "1", "2", "3", "4", "5", "6", "7"]])
        board_ui = concatenate((indexing_ui[:, 1:], self.board), axis=0)
        board_ui = concatenate((indexing_ui.T, board_ui), axis=1)
        info_1 = "\nWhite to move" if self.white_to_move else "\nBlack to move"
        return str(board_ui) + info_1
