"""
This file is responsible to handle UI and user input.
"""

import pygame as p
import chess_env
from chess_error import ChessError
from move import Move

WIDTH = HEIGHT = 512 // 8 * 8
SQUARE_SIZE = HEIGHT // 8
MAX_FPS = 10
IMAGES = {}
SOUNDS = {}


def load_images():
    IMAGES_DIR = "asset/img/"
    pieces = "pbnrqk"
    pieces += pieces.upper()
    for piece in pieces:
        IMAGES[piece] = p.image.load(IMAGES_DIR + piece + ".png")


def load_sounds():
    SOUNDS_DIR = "asset/sound/"
    for type in ["move", "capture"]:
        SOUNDS[type] = p.mixer.Sound(SOUNDS_DIR + type + ".mp3")


def main():
    p.init()
    p.display.set_caption("Chess")
    screen = p.display.set_mode((WIDTH, HEIGHT))
    screen.fill(p.Color("White"))
    clock = p.time.Clock()
    gs = chess_env.Chessboard()
    load_images()
    load_sounds()
    last_click = ()
    clicks = []

    running = True
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undoMove()
            elif e.type == p.MOUSEBUTTONDOWN:
                pos = p.mouse.get_pos()
                col = pos[0] // SQUARE_SIZE
                row = pos[1] // SQUARE_SIZE
                if len(clicks) == 0:
                    if gs.board[row, col] in gs.friend_pieces:
                        last_click = (row, col)
                        clicks.append(last_click)
                else:
                    if last_click != (row, col):
                        last_click = (row, col)
                        clicks.append(last_click)
                        move = Move(clicks[0], clicks[1], gs.board)
                        # make move
                        try:
                            gs.make_move(move)
                            # play sound
                            if move.piece_captured == ".":
                                p.mixer.Sound.play(SOUNDS["move"])
                            else:
                                p.mixer.Sound.play(SOUNDS["capture"])
                        except ChessError as e:
                            print(e)

                    last_click = ()
                    clicks = []

        selected_piece = None if len(clicks) != 1 else clicks[0]
        drawGameState(screen, gs, selected_piece)
        clock.tick(MAX_FPS)
        p.display.flip()


def drawGameState(screen, gs, active_square):
    drawBoard(screen, active_square)
    drawPieces(screen, gs.board)


def drawBoard(screen, active_square):
    colors = [
        p.Color(240, 215, 184),
        p.Color(179, 133, 104),
        p.Color(130, 151, 105),
    ]  # [light, dark, active_square]
    rectangle = lambda row, col: p.Rect(
        col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE
    )
    for row in range(8):
        for col in range(8):
            if active_square == (row, col):
                color = colors[-1]
            else:
                color = colors[(row + col) % 2]
            p.draw.rect(screen, color, rectangle(row, col))


def drawPieces(screen, board):
    for row in range(8):
        for col in range(8):
            if board[row][col] != ".":
                size_factor = 1.0
                piece_size = size_factor * SQUARE_SIZE
                piece_image = p.transform.smoothscale(
                    IMAGES[board[row, col]], (piece_size, piece_size)
                )
                x_piece_draw = (
                    col * SQUARE_SIZE + SQUARE_SIZE * (1 - size_factor) / 2
                )
                y_piece_draw = (
                    row * SQUARE_SIZE + SQUARE_SIZE * (1 - size_factor) / 2
                )
                screen.blit(piece_image, (x_piece_draw, y_piece_draw))


if __name__ == "__main__":
    main()
