# --- SOCX CHECKERS ----------- #
# --- By Musterion for Socx --- #
# --- Version 2.2.0 ----------- #
# --- 08 Feb 2025 --------------#

import pygame
import sys

# ---------------- Pygame Initialization and Global Constants ----------------
pygame.init()

# Board dimensions
WIDTH, HEIGHT = 800, 800
# Extra space at the bottom for info display
INFO_PANEL_HEIGHT = 100
WINDOW_HEIGHT = HEIGHT + INFO_PANEL_HEIGHT

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
        # King promotion if piece reaches the last row
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

    def update(self, elapsed_time):
        # Draw the board (top portion)
        self.board.draw(self.win)
        self.draw_valid_moves(self.valid_moves)
        # Draw the information panel (bottom portion)
        self.draw_info(elapsed_time)
        # If a winner exists, overlay a winner message across the board
        if self.board.winner() is not None:
            winner_color = self.board.winner()
            winner_text = f"Winner: {'RED' if winner_color == RED else 'WHITE'}"
            winner_font = pygame.font.SysFont("comicsans", 72)
            winner_surface = winner_font.render(winner_text, True, WHITE)
            win_x = WIDTH // 2 - winner_surface.get_width() // 2
            win_y = HEIGHT // 2 - winner_surface.get_height() // 2
            self.win.blit(winner_surface, (win_x, win_y))
        pygame.display.update()

    def reset(self):
        self._init()

    def select(self, row, col):
        # Do not allow moves if a winner has been determined.
        if self.board.winner() is not None:
            return False

        clicked_piece = self.board.get_piece(row, col)

        # If a piece is already selected...
        if self.selected:
            # Allow changing selection if clicking another piece of the same color (and not forced to multi-jump).
            if clicked_piece != 0 and clicked_piece.color == self.turn and clicked_piece != self.selected:
                forced_moves = {move: skipped for move, skipped in self.board.get_valid_moves(self.selected).items() if skipped}
                if not forced_moves:
                    self.selected = clicked_piece
                    moves = self.board.get_valid_moves(clicked_piece)
                    capture_moves = {move: skipped for move, skipped in moves.items() if skipped}
                    self.valid_moves = capture_moves if capture_moves else moves
                    return True
            # If the clicked square is a valid move for the selected piece, execute the move.
            if (row, col) in self.valid_moves:
                self._move(row, col)
                return True
            return False

        # If nothing is selected, select the clicked piece (if it belongs to the player)
        if clicked_piece != 0 and clicked_piece.color == self.turn:
            self.selected = clicked_piece
            moves = self.board.get_valid_moves(clicked_piece)
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
                # After capturing, check if additional capture moves exist (multi-jump)
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

    def draw_info(self, elapsed_time):
        # Draw the information panel in the bottom INFO_PANEL_HEIGHT area.
        font = pygame.font.SysFont("comicsans", 24)
        # Next to play
        next_text = f"Next to Play: {'RED' if self.turn == RED else 'WHITE'}"
        next_surface = font.render(next_text, True, WHITE)
        # Pieces left
        pieces_text = f"RED: {self.board.red_left}    WHITE: {self.board.white_left}"
        pieces_surface = font.render(pieces_text, True, WHITE)
        # Timer in MM:ss format
        minutes = elapsed_time // 60000
        seconds = (elapsed_time // 1000) % 60
        timer_text = f"Time: {minutes:02d}:{seconds:02d}"
        timer_surface = font.render(timer_text, True, WHITE)
        
        # Y coordinate for the info panel (start drawing 10 pixels below the board)
        panel_y = HEIGHT + 10
        self.win.blit(next_surface, (10, panel_y))
        pieces_x = WIDTH // 2 - pieces_surface.get_width() // 2
        self.win.blit(pieces_surface, (pieces_x, panel_y))
        timer_x = WIDTH - timer_surface.get_width() - 10
        self.win.blit(timer_surface, (timer_x, panel_y))

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
            moves.append((piece.row, piece.col, move, skip, new_board))
    return moves

def minimax(board, depth, max_player, game, alpha, beta):
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
    # Use minimax to decide the best move for WHITE (computer)
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
    running = True
    mode = None
    while running:
        win.fill(BLACK)
        title_font = pygame.font.SysFont("comicsans", 60)
        option_font = pygame.font.SysFont("comicsans", 40)
        title_text = title_font.render("Checkers", True, WHITE)
        win.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 100))
        option1 = option_font.render("Press 1 for Single Player Mode", True, WHITE)
        option2 = option_font.render("Press 2 for Two Player Mode", True, WHITE)
        win.blit(option1, (WIDTH // 2 - option1.get_width() // 2, 300))
        win.blit(option2, (WIDTH // 2 - option2.get_width() // 2, 400))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    mode = "AI"
                    running = False
                elif event.key == pygame.K_2:
                    mode = "2P"
                    running = False
    return mode

# ---------------- Main Game Loop ----------------
def main():
    mode = menu()  # Show menu and let the user select a mode
    win = pygame.display.set_mode((WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Checkers")
    game = Game(win, mode)
    clock = pygame.time.Clock()
    start_time = pygame.time.get_ticks()  # Record start time for timer

    running = True
    while running:
        clock.tick(60)  # 60 FPS
        elapsed_time = pygame.time.get_ticks() - start_time

        # Do not exit when a winner is determined; simply display the winner on-screen.
        # In single-player mode, let the AI move when it's WHITE's turn.
        if game.mode == "AI" and game.turn == WHITE and game.board.winner() is None:
            pygame.time.delay(500)  # Small delay to make the AI move visible
            ai_move(game)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if game.mode == "2P" or (game.mode == "AI" and game.turn == RED):
                    pos = pygame.mouse.get_pos()
                    # Only consider clicks on the board area (ignore clicks in info panel)
                    if pos[1] < HEIGHT:
                        row = pos[1] // SQUARE_SIZE
                        col = pos[0] // SQUARE_SIZE
                        game.select(row, col)

        if game.board.winner() is None:
            game.update(elapsed_time)

    pygame.quit()

if __name__ == "__main__":
    main()
