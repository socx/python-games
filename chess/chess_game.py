# --- SOCX CHESS -------------- #
# --- By Musterion for Socx --- #
# --- Version 1.3.0 ----------- #
# --- 11 Feb 2025 --------------#

import sys
import pygame
import chess

# --- Initialization ---

pygame.init()
WIDTH, HEIGHT = 700, 700  # window dimensions (square board)
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Socx Chess (WIP)")
CLOCK = pygame.time.Clock()

# Each square will be WIDTH//8 pixels wide/high.
SQUARE_SIZE = WIDTH // 8

# Create a chess board (using python-chess)
board = chess.Board()

# Instead of a selected square, we now keep track of a piece being dragged.
# dragging_info is a dictionary containing:
#   - "from_square": the square index where the piece was picked up.
#   - "piece": the chess.Piece object being dragged.
#   - "offset": the (x,y) offset from the top-left of the square where the mouse was clicked.
#   - "current_pos": the current mouse position (updated during dragging).
dragging_info = None

# --- Load piece images ---
# Images are stored in the "images" folder.
piece_images = {}
piece_images["K"] = pygame.image.load("images/w_king.png")
piece_images["Q"] = pygame.image.load("images/w_queen.png")
piece_images["R"] = pygame.image.load("images/w_rook.png")
piece_images["B"] = pygame.image.load("images/w_bishop.png")
piece_images["N"] = pygame.image.load("images/w_knight.png")
piece_images["P"] = pygame.image.load("images/w_pawn.png")
piece_images["k"] = pygame.image.load("images/b_king.png")
piece_images["q"] = pygame.image.load("images/b_queen.png")
piece_images["r"] = pygame.image.load("images/b_rook.png")
piece_images["b"] = pygame.image.load("images/b_bishop.png")
piece_images["n"] = pygame.image.load("images/b_knight.png")
piece_images["p"] = pygame.image.load("images/b_pawn.png")

# Scale images to fit the square size.
for key in piece_images:
    piece_images[key] = pygame.transform.scale(piece_images[key], (SQUARE_SIZE, SQUARE_SIZE))

# Colors for board squares and messages
LIGHT_COLOR = (238, 238, 210)
DARK_COLOR = (118, 150, 86)
HIGHLIGHT_COLOR = (50, 50, 200)  # can be used to highlight a square (if desired)
GAME_OVER_COLOR = (200, 0, 0)      # color for game over message
HINT_COLOR = (255, 255, 0)         # yellow color for legal move hints

# --- Helper Functions ---

def get_square_rect(square, square_size):
    """
    Convert a python-chess square (0 to 63) to a pygame.Rect.
    The board is drawn so that a8 is at the top left and h1 at the bottom right.
    """
    file = chess.square_file(square)  # 0 for file 'a', 1 for 'b', etc.
    rank = chess.square_rank(square)  # 0 for rank 1, 7 for rank 8.
    row = 7 - rank  # so that rank 8 is at the top
    x = file * square_size
    y = row * square_size
    return pygame.Rect(x, y, square_size, square_size)

def draw_board(screen, square_size):
    """
    Draw the 8x8 chess board.
    """
    for row in range(8):
        for col in range(8):
            color = LIGHT_COLOR if (row + col) % 2 == 0 else DARK_COLOR
            rect = pygame.Rect(col * square_size, row * square_size, square_size, square_size)
            pygame.draw.rect(screen, color, rect)

def draw_move_hints(screen, board, square_size, dragging_info):
    """
    If a piece is currently being dragged (i.e. selected),
    display small yellow circles on each square that is a legal destination.
    """
    if dragging_info is not None:
        from_square = dragging_info["from_square"]
        # Filter legal moves for the piece being dragged.
        legal_moves = [move for move in board.legal_moves if move.from_square == from_square]
        for move in legal_moves:
            to_square = move.to_square
            rect = get_square_rect(to_square, square_size)
            center = rect.center
            # Draw a small circle as a move hint.
            pygame.draw.circle(screen, HINT_COLOR, center, square_size // 8)

def draw_pieces(screen, board, square_size, dragging_info):
    """
    Draw all the pieces on the board using images.
    The piece being dragged is not drawn on its original square.
    """
    for square in chess.SQUARES:
        # Skip drawing the piece if it is being dragged.
        if dragging_info is not None and square == dragging_info["from_square"]:
            continue
        piece = board.piece_at(square)
        if piece:
            rect = get_square_rect(square, square_size)
            image = piece_images[piece.symbol()]
            screen.blit(image, rect)
    
    # Draw the dragged piece (if any) at the current mouse position (accounting for the offset).
    if dragging_info is not None:
        image = piece_images[dragging_info["piece"].symbol()]
        pos = dragging_info["current_pos"]
        offset = dragging_info["offset"]
        draw_x = pos[0] - offset[0]
        draw_y = pos[1] - offset[1]
        dragged_rect = pygame.Rect(draw_x, draw_y, SQUARE_SIZE, SQUARE_SIZE)
        screen.blit(image, dragged_rect)

def draw_game_over(screen, board, square_size):
    """
    If the game is over, display a game over message in the center of the board.
    """
    if board.is_game_over():
        outcome = board.outcome()
        result_text = f"Game Over: {outcome.result()}" if outcome is not None else "Game Over"
        # Use a font to render the message.
        font = pygame.font.SysFont("DejaVu Sans", 32)
        text_surface = font.render(result_text, True, GAME_OVER_COLOR)
        text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(text_surface, text_rect)

def square_from_mouse_pos(pos, square_size):
    """
    Convert a mouse position (x, y) into a python-chess square index.
    The board is drawn with a8 at the top left.
    """
    x, y = pos
    col = x // square_size
    row = y // square_size  # row 0 is at the top
    rank = 7 - row          # convert row back to chess rank
    return chess.square(col, rank)

# --- Main Game Loop ---

running = True
while running:
    for event in pygame.event.get():
        # Quit if the window is closed.
        if event.type == pygame.QUIT:
            running = False

        # --- Start Dragging ---
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not board.is_game_over():
            pos = event.pos
            square = square_from_mouse_pos(pos, SQUARE_SIZE)
            piece = board.piece_at(square)
            if piece is not None and piece.color == board.turn:
                # Calculate the offset within the square where the piece was clicked.
                rect = get_square_rect(square, SQUARE_SIZE)
                offset_x = pos[0] - rect.x
                offset_y = pos[1] - rect.y
                dragging_info = {
                    "from_square": square,
                    "piece": piece,
                    "offset": (offset_x, offset_y),
                    "current_pos": pos,
                }

        # --- Update Dragging Position ---
        if event.type == pygame.MOUSEMOTION:
            if dragging_info is not None:
                dragging_info["current_pos"] = event.pos

        # --- Drop the Piece ---
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and dragging_info is not None:
            pos = event.pos
            to_square = square_from_mouse_pos(pos, SQUARE_SIZE)
            from_square = dragging_info["from_square"]
            move = chess.Move(from_square, to_square)
            # Handle ambiguous moves (like pawn promotion) by checking legal moves.
            if move not in board.legal_moves:
                for legal_move in board.legal_moves:
                    if legal_move.from_square == from_square and legal_move.to_square == to_square:
                        move = legal_move  # defaults to queen promotion when needed
                        break
            if move in board.legal_moves:
                board.push(move)
            # Clear the dragging info whether the move was legal or not.
            dragging_info = None

    # --- Drawing ---
    SCREEN.fill((0, 0, 0))
    draw_board(SCREEN, SQUARE_SIZE)
    draw_move_hints(SCREEN, board, SQUARE_SIZE, dragging_info)
    draw_pieces(SCREEN, board, SQUARE_SIZE, dragging_info)
    draw_game_over(SCREEN, board, SQUARE_SIZE)
    pygame.display.flip()
    CLOCK.tick(60)

pygame.quit()
sys.exit()
