# --- SOCX CHECKERS ----------- #
# --- By Musterion for Socx --- #
# --- Version 2.0.0 ----------- #
# --- 07 Feb 2025 --------------#

import pygame
import sys
import copy
import math
import random

# ---------------- Pygame Initialization and Global Constants ----------------
pygame.init()

WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

# Colors
RED    = (255, 0, 0)
WHITE  = (255, 255, 255)
BLACK  = (0, 0, 0)
GREY   = (128, 128, 128)
BLUE   = (0, 0, 255)

# ---------------- Piece Class ----------------
class Piece:
    PADDING = 15
    OUTLINE = 2

    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.king = False
        self.x = 0
        self.y = 0
        self.calc_pos()
    
    def calc_pos(self):
        self.x = SQUARE_SIZE * self.col + SQUARE_SIZE // 2
        self.y = SQUARE_SIZE * self.row + SQUARE_SIZE // 2
    
    def make_king(self):
        self.king = True

    def draw(self, win):
        radius = SQUARE_SIZE // 2 - self.PADDING
        # Draw an outline circle
        pygame.draw.circle(win, GREY, (self.x, self.y), radius + self.OUTLINE)
        # Draw the piece itself
        pygame.draw.circle(win, self.color, (self.x, self.y), radius)
        if self.king:
            font = pygame.font.SysFont("comicsans", 30)
            crown = font.render("K", True, BLUE)
            win.blit(crown, (self.x - crown.get_width() // 2, self.y - crown.get_height() // 2))
    
    def move(self, row, col):
        self.row = row
        self.col = col
        self.calc_pos()

# ---------------- Board Class ----------------
class Board:
    def __init__(self):
        self.board = []
        self.red_left = self.white_left = 12
        self.red_kings = self.white_kings = 0
        self.create_board()

    def draw_squares(self, win):
        win.fill(BLACK)
        for row in range(ROWS):
            for col in range(row % 2, COLS, 2):
                pygame.draw.rect(win, GREY, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def create_board(self):
        for row in range(ROWS):
            self.board.append([])
            for col in range(COLS):
                if col % 2 == ((row + 1) % 2):
                    if row < 3:
                        self.board[row].append(Piece(row, col, WHITE))
                    elif row > 4:
                        self.board[row].append(Piece(row, col, RED))
                    else:
                        self.board[row].append(0)
                else:
                    self.board[row].append(0)
    
    def draw(self, win):
        self.draw_squares(win)
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0:
                    piece.draw(win)

    def move(self, piece, row, col):
        # Move piece on board and update its position
        self.board[piece.row][piece.col], self.board[row][col] = 0, piece
        piece.move(row, col)
        # King promotion
        if row == ROWS - 1 or row == 0:
            if not piece.king:
                piece.make_king()
                if piece.color == RED:
                    self.red_kings += 1
                else:
                    self.white_kings += 1

    def get_piece(self, row, col):
        return self.board[row][col]

    def remove(self, pieces):
        for piece in pieces:
            self.board[piece.row][piece.col] = 0
            if piece != 0:
                if piece.color == RED:
                    self.red_left -= 1
                else:
                    self.white_left -= 1

    def winner(self):
        if self.red_left <= 0:
            return WHITE
        elif self.white_left <= 0:
            return RED
        return None

    def get_valid_moves(self, piece):
        moves = {}
        left = piece.col - 1
        right = piece.col + 1
        row = piece.row

        # For RED (and kings) move upward (decreasing row)
        if piece.color == RED or piece.king:
            moves.update(self._traverse_left(row - 1, max(row - 3, -1), -1, piece.color, left))
            moves.update(self._traverse_right(row - 1, max(row - 3, -1), -1, piece.color, right))
        # For WHITE (and kings) move downward (increasing row)
        if piece.color == WHITE or piece.king:
            moves.update(self._traverse_left(row + 1, min(row + 3, ROWS), 1, piece.color, left))
            moves.update(self._traverse_right(row + 1, min(row + 3, ROWS), 1, piece.color, right))
        return moves

    def _traverse_left(self, start, stop, step, color, left, skipped=[]):
        moves = {}
        last = []
        for r in range(start, stop, step):
            if left < 0:
                break

            current = self.board[r][left]
            if current == 0:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r, left)] = last + skipped
                else:
                    moves[(r, left)] = last

                if last:
                    next_r = r + step
                    if 0 <= next_r < ROWS:
                        moves.update(self._traverse_left(r + step, stop, step, color, left - 1, skipped=last))
                        moves.update(self._traverse_right(r + step, stop, step, color, left + 1, skipped=last))
                break
            elif current.color == color:
                break
            else:
                last = [current]

            left -= 1

        return moves

    def _traverse_right(self, start, stop, step, color, right, skipped=[]):
        moves = {}
        last = []
        for r in range(start, stop, step):
            if right >= COLS:
                break

            current = self.board[r][right]
            if current == 0:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r, right)] = last + skipped
                else:
                    moves[(r, right)] = last

                if last:
                    next_r = r + step
                    if 0 <= next_r < ROWS:
                        moves.update(self._traverse_left(r + step, stop, step, color, right - 1, skipped=last))
                        moves.update(self._traverse_right(r + step, stop, step, color, right + 1, skipped=last))
                break
            elif current.color == color:
                break
            else:
                last = [current]

            right += 1

        return moves

    # ------------- Helper Methods for the AI (Simulation and Cloning) -------------
    def get_all_pieces(self, color):
        pieces = []
        for row in self.board:
            for piece in row:
                if piece != 0 and piece.color == color:
                    pieces.append(piece)
        return pieces

    def clone(self):
        # Create a deep copy of the board (for simulation purposes)
        new_board = Board.__new__(Board)
        new_board.board = []
        for row in self.board:
            new_row = []
            for piece in row:
                if piece == 0:
                    new_row.append(0)
                else:
                    new_piece = Piece(piece.row, piece.col, piece.color)
                    new_piece.king = piece.king
                    new_row.append(new_piece)
            new_board.board.append(new_row)
        new_board.red_left = self.red_left
        new_board.white_left = self.white_left
        new_board.red_kings = self.red_kings
        new_board.white_kings = self.white_kings
        return new_board

# ---------------- Game Class ----------------
class Game:
    def __init__(self, win, mode):
        self.win = win
        self.mode = mode  # "2P" or "AI"
        self._init()

    def _init(self):
        self.selected = None
        self.board = Board()
        # RED always starts; in AI mode human is RED, computer is WHITE.
        self.turn = RED
        self.valid_moves = {}

    def update(self):
        self.board.draw(self.win)
        self.draw_valid_moves(self.valid_moves)
        pygame.display.update()

    def reset(self):
        self._init()

    def select(self, row, col):
        # In multi-jump sequences, the selected piece is fixed.
        if self.selected:
            if (row, col) in self.valid_moves:
                self._move(row, col)
            return True

        piece = self.board.get_piece(row, col)
        if piece != 0 and piece.color == self.turn:
            self.selected = piece
            moves = self.board.get_valid_moves(piece)
            # If capturing moves exist, force them.
            capture_moves = {move: skipped for move, skipped in moves.items() if skipped}
            self.valid_moves = capture_moves if capture_moves else moves
            return True

        return False

    def _move(self, row, col):
        if self.selected and (row, col) in self.valid_moves:
            captured = self.valid_moves[(row, col)]
            self.board.move(self.selected, row, col)
            if captured:
                self.board.remove(captured)
                # After capturing, check if additional capture moves exist.
                new_moves = self.board.get_valid_moves(self.selected)
                capture_moves = {move: skipped for move, skipped in new_moves.items() if skipped}
                if capture_moves:
                    self.valid_moves = capture_moves
                    return True
            self.change_turn()
            return True
        return False

    def draw_valid_moves(self, moves):
        for move in moves:
            row, col = move
            pygame.draw.circle(
                self.win, BLUE,
                (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2),
                15
            )

    def change_turn(self):
        self.valid_moves = {}
        self.selected = None
        self.turn = WHITE if self.turn == RED else RED

# ---------------- AI Helper Functions ----------------
def evaluate(board):
    # A simple evaluation: (computer score) - (human score)
    # Here, computer is WHITE and human is RED.
    return board.white_left - board.red_left + (board.white_kings * 0.5 - board.red_kings * 0.5)

def simulate_move(piece, move, board, skip):
    board.move(piece, move[0], move[1])
    if skip:
        board.remove(skip)
    return board

def get_all_moves(board, color, game):
    moves = []
    for piece in board.get_all_pieces(color):
        valid_moves = board.get_valid_moves(piece)
        for move, skip in valid_moves.items():
            temp_board = board.clone()
            temp_piece = temp_board.get_piece(piece.row, piece.col)
            new_board = simulate_move(temp_piece, move, temp_board, skip)
            # Record: (original piece row, col, destination, skip list, new board state)
            moves.append((piece.row, piece.col, move, skip, new_board))
    return moves

def minimax(board, depth, max_player, game, alpha, beta):
    # Terminal condition: maximum depth reached or game over.
    if depth == 0 or board.winner() is not None:
        return evaluate(board), board

    if max_player:
        max_eval = float('-inf')
        best_move = None
        for move in get_all_moves(board, WHITE, game):
            evaluation = minimax(move[4], depth - 1, False, game, alpha, beta)[0]
            if evaluation > max_eval:
                max_eval = evaluation
                best_move = move
            alpha = max(alpha, evaluation)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = float('inf')
        best_move = None
        for move in get_all_moves(board, RED, game):
            evaluation = minimax(move[4], depth - 1, True, game, alpha, beta)[0]
            if evaluation < min_eval:
                min_eval = evaluation
                best_move = move
            beta = min(beta, evaluation)
            if beta <= alpha:
                break
        return min_eval, best_move

def ai_move(game):
    # Let the minimax algorithm decide the best move for WHITE (computer)
    _, move = minimax(game.board.clone(), 3, True, game, float('-inf'), float('inf'))
    if move is not None:
        r, c, dest, skip, _ = move
        piece = game.board.get_piece(r, c)
        if piece is not None:
            game.board.move(piece, dest[0], dest[1])
            if skip:
                game.board.remove(skip)
        game.change_turn()

# ---------------- Simple Menu ----------------
def menu():
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Checkers Menu")
    run = True
    mode = None
    while run:
        win.fill(BLACK)
        title_font = pygame.font.SysFont("comicsans", 60)
        option_font = pygame.font.SysFont("comicsans", 40)
        title_text = title_font.render("Checkers", True, WHITE)
        win.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 100))
        option1 = option_font.render("Press 1 for Two Player Mode", True, WHITE)
        option2 = option_font.render("Press 2 for Single Player Mode", True, WHITE)
        win.blit(option1, (WIDTH // 2 - option1.get_width() // 2, 300))
        win.blit(option2, (WIDTH // 2 - option2.get_width() // 2, 400))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    mode = "2P"
                    run = False
                elif event.key == pygame.K_2:
                    mode = "AI"
                    run = False
    return mode

# ---------------- Main Game Loop ----------------
def main():
    mode = menu()  # Show menu and let the user select a mode
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Checkers")
    game = Game(win, mode)
    clock = pygame.time.Clock()

    run = True
    while run:
        clock.tick(60)  # 60 FPS

        # Check for a winner
        if game.board.winner() is not None:
            winner_color = game.board.winner()
            print(f"Game Over! {'RED' if winner_color == RED else 'WHITE'} wins!")
            run = False

        # In single-player mode, if it's the computer's turn, let the AI move.
        if game.mode == "AI" and game.turn == WHITE:
            # Small delay to make the AI move visible
            pygame.time.delay(500)
            ai_move(game)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()

            # In two-player mode or when it's the human's turn, handle mouse input.
            if event.type == pygame.MOUSEBUTTONDOWN:
                if game.mode == "2P" or (game.mode == "AI" and game.turn == RED):
                    pos = pygame.mouse.get_pos()
                    row = pos[1] // SQUARE_SIZE
                    col = pos[0] // SQUARE_SIZE
                    game.select(row, col)

        game.update()

    pygame.quit()

if __name__ == "__main__":
    main()
