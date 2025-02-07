import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
width, height = 600, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Checkers")

# Colors
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 255, 0)

# Board size
board_size = 8

# Square size
square_size = width // board_size

# Create an empty board
board = [[None for _ in range(board_size)] for _ in range(board_size)]

# Initialize player pieces (red and black)
def initialize_board():
    for row in range(board_size):
        for col in range(board_size):
            if (row + col) % 2 == 0:
                if row < 3:
                    board[row][col] = 'r'  # Red piece
                elif row > 4:
                    board[row][col] = 'b'  # Black piece

# Function to draw the board
def draw_board():
    for row in range(board_size):
        for col in range(board_size):
            color = white if (row + col) % 2 == 0 else black
            pygame.draw.rect(screen, color, (col * square_size, row * square_size, square_size, square_size))

# Function to draw the pieces
def draw_pieces():
    for row in range(board_size):
        for col in range(board_size):
            if board[row][col] == 'r':
                pygame.draw.circle(screen, red, (col * square_size + square_size // 2, row * square_size + square_size // 2), square_size // 2 - 5)
            elif board[row][col] == 'b':
                pygame.draw.circle(screen, black, (col * square_size + square_size // 2, row * square_size + square_size // 2), square_size // 2 - 5)

# Function to get valid moves for a piece
def get_valid_moves(row, col, color):
    valid_moves = []
    if color == 'r':
        if row > 0:
            # Forward left diagonal
            if col > 0 and board[row - 1][col - 1] is None:
                valid_moves.append((row - 1, col - 1))
                if row > 1 and col > 1 and board[row - 1][col - 1] == 'b' and board[row - 2][col - 2] is None:
                    valid_moves.append((row - 2, col - 2))
            # Forward right diagonal
            if col < board_size - 1 and board[row - 1][col + 1] is None:
                valid_moves.append((row - 1, col + 1))
                if row > 1 and col < board_size - 2 and board[row - 1][col + 1] == 'b' and board[row - 2][col + 2] is None:
                    valid_moves.append((row - 2, col + 2))
    elif color == 'b':
        if row < board_size - 1:
            # Forward left diagonal
            if col > 0 and board[row + 1][col - 1] is None:
                valid_moves.append((row + 1, col - 1))
                if row < board_size - 2 and col > 1 and board[row + 1][col - 1] == 'r' and board[row + 2][col - 2] is None:
                    valid_moves.append((row + 2, col - 2))
            # Forward right diagonal
            if col < board_size - 1 and board[row + 1][col + 1] is None:
                valid_moves.append((row + 1, col + 1))
                if row < board_size - 2 and col < board_size - 2 and board[row + 1][col + 1] == 'r' and board[row + 2][col + 2] is None:
                    valid_moves.append((row + 2, col + 2))
    return valid_moves

# Game loop
running = True
current_player = 'r'  # Red player starts
selected_piece = None

initialize_board()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            row = mouse_y // square_size
            col = mouse_x // square_size

            if selected_piece is None:
                if board[row][col] == current_player:
                    selected_piece = (row, col)
            else:
                new_row, new_col = row, col
                if (new_row, new_col) in get_valid_moves(selected_piece[0], selected_piece[1], current_player):
                    # Move the piece
                    board[new_row][new_col] = board[selected_piece[0]][selected_piece[1]]
                    board[selected_piece[0]][selected_piece[1]] = None

                    # Check for captures (implement later)

                    current_player = 'b' if current_player == 'r' else 'r'
                selected_piece = None

    draw_board()
    draw_pieces()
    pygame.display.update()

pygame.quit()
