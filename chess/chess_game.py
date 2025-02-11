# --- SOCX CHESS -------------- #
# --- By Musterion for Socx --- #
# --- Version 1.0.0 ----------- #
# --- 11 Feb 2025 --------------#

import sys
import pygame
import chess

# --- Initialization ---

pygame.init()

# Set up the window
WIDTH, HEIGHT = 512, 512  # window dimensions (square board)
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Python Chess")
CLOCK = pygame.time.Clock()

# Each square will be WIDTH//8 pixels wide/high.
SQUARE_SIZE = WIDTH // 8

# Initialize a chess board (from python-chess)
board = chess.Board()

# This variable will hold the currently selected square (if any)
selected_square = None

# --- Unicode symbols for the pieces ---
# White pieces: uppercase; Black pieces: lowercase.
# (These Unicode codepoints are usually supported by fonts like "DejaVu Sans".)
piece_unicode = {
    "K": "\u2654",  # White King
    "Q": "\u2655",  # White Queen
    "R": "\u2656",  # White Rook
    "B": "\u2657",  # White Bishop
    "N": "\u2658",  # White Knight
    "P": "\u2659",  # White Pawn
    "k": "\u265A",  # Black King
    "q": "\u265B",  # Black Queen
    "r": "\u265C",  # Black Rook
    "b": "\u265D",  # Black Bishop
    "n": "\u265E",  # Black Knight
    "p": "\u265F",  # Black Pawn
}

# Choose a font that supports chess Unicode symbols.
# The font size is set roughly to the square size.
FONT = pygame.font.SysFont("DejaVu Sans", SQUARE_SIZE)

# Colors for the board squares
LIGHT_COLOR = (238, 238, 210)
DARK_COLOR = (118, 150, 86)
HIGHLIGHT_COLOR = (50, 50, 200)  # used to highlight a selected square
GAME_OVER_COLOR = (200, 0, 0)      # color for game over message

# --- Helper Functions ---

def get_square_rect(square, square_size):
    """
    Convert a python-chess square (0 to 63) to a pygame.Rect.
    Our board is drawn so that a8 is at the top left and h1 is at the bottom right.
    """
    file = chess.square_file(square)  # 0 for file 'a', 1 for 'b', etc.
    rank = chess.square_rank(square)  # 0 for rank 1, 7 for rank 8.
    # To have rank 8 at the top, compute the row as:
    row = 7 - rank
    x = file * square_size
    y = row * square_size
    return pygame.Rect(x, y, square_size, square_size)

def draw_board(screen, square_size, selected_square):
    """
    Draw the chess board squares and highlight the selected square.
    """
    for row in range(8):
        for col in range(8):
            # Determine square color (light or dark)
            color = LIGHT_COLOR if (row + col) % 2 == 0 else DARK_COLOR
            rect = pygame.Rect(col * square_size, row * square_size, square_size, square_size)
            pygame.draw.rect(screen, color, rect)
    
    # If a square is selected, draw a highlight border around it.
    if selected_square is not None:
        rect = get_square_rect(selected_square, square_size)
        pygame.draw.rect(screen, HIGHLIGHT_COLOR, rect, 4)

def draw_pieces(screen, board, square_size):
    """
    Draw chess pieces on the board using Unicode symbols.
    """
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            # Get file and rank so that a8 is top-left.
            file = chess.square_file(square)
            rank = chess.square_rank(square)
            row = 7 - rank  # flip rank so that rank 8 is row 0
            center_x = file * square_size + square_size // 2
            center_y = row * square_size + square_size // 2
            # Get the Unicode symbol for the piece.
            symbol = piece_unicode[piece.symbol()]
            # Render the symbol. (Using black for all pieces; you can customize colors as desired.)
            text_surface = FONT.render(symbol, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=(center_x, center_y))
            screen.blit(text_surface, text_rect)

def draw_game_over(screen, board, square_size):
    """
    If the game is over, display a message in the center of the board.
    """
    if board.is_game_over():
        outcome = board.outcome()
        if outcome is not None:
            result_text = f"Game Over: {outcome.result()}"
        else:
            result_text = "Game Over"
        text_surface = FONT.render(result_text, True, GAME_OVER_COLOR)
        text_rect = text_surface.get_rect(center=(WIDTH//2, HEIGHT//2))
        screen.blit(text_surface, text_rect)

def square_from_mouse_pos(pos, square_size):
    """
    Convert a mouse position (x, y) into a python-chess square index.
    Remember: our board is drawn with a8 at the top left.
    """
    x, y = pos
    col = x // square_size
    row = y // square_size  # row 0 is top of the screen
    rank = 7 - row          # because row 0 is rank 8 and row 7 is rank 1
    return chess.square(col, rank)

# --- Main Game Loop ---

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Handle mouse clicks
        if event.type == pygame.MOUSEBUTTONDOWN and not board.is_game_over():
            pos = pygame.mouse.get_pos()
            clicked_square = square_from_mouse_pos(pos, SQUARE_SIZE)
            # If nothing is selected, select a piece if it belongs to the player whose turn it is.
            if selected_square is None:
                piece = board.piece_at(clicked_square)
                if piece is not None and piece.color == board.turn:
                    selected_square = clicked_square
            else:
                # A piece has been selected; try to make a move.
                move = chess.Move(selected_square, clicked_square)
                # Some moves (like pawn promotion) require extra info.
                # Check if any legal move from the selected square goes to the clicked square.
                if move not in board.legal_moves:
                    for legal_move in board.legal_moves:
                        if legal_move.from_square == selected_square and legal_move.to_square == clicked_square:
                            move = legal_move  # e.g. will default to queen promotion
                            break
                if move in board.legal_moves:
                    board.push(move)
                    selected_square = None
                else:
                    # If the destination square did not yield a legal move,
                    # check if the player clicked another of their own pieces and change selection.
                    piece = board.piece_at(clicked_square)
                    if piece is not None and piece.color == board.turn:
                        selected_square = clicked_square
                    else:
                        # Otherwise, clear the selection.
                        selected_square = None

    # Draw everything
    draw_board(SCREEN, SQUARE_SIZE, selected_square)
    draw_pieces(SCREEN, board, SQUARE_SIZE)
    draw_game_over(SCREEN, board, SQUARE_SIZE)

    pygame.display.flip()
    CLOCK.tick(60)

pygame.quit()
sys.exit()
