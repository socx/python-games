# --- SOCX CHECKERS ----------- #
# --- By Musterion for Socx --- #
# --- Version 1.1.0 ----------- #
# --- 07 Feb 2025 --------------#

import pygame
import sys

# Initialize Pygame
pygame.init()

# ---------------- Global Constants ----------------
WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

# RGB Colors
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
        """Calculate the center position of the piece for drawing."""
        self.x = SQUARE_SIZE * self.col + SQUARE_SIZE // 2
        self.y = SQUARE_SIZE * self.row + SQUARE_SIZE // 2
    
    def make_king(self):
        self.king = True

    def draw(self, win):
        """Draw the piece along with an outline. Mark kings with a 'K'."""
        radius = SQUARE_SIZE // 2 - self.PADDING
        pygame.draw.circle(win, GREY, (self.x, self.y), radius + self.OUTLINE)
        pygame.draw.circle(win, self.color, (self.x, self.y), radius)
        if self.king:
            font = pygame.font.SysFont("comicsans", 30)
            crown = font.render("K", True, BLUE)
            win.blit(crown, (self.x - crown.get_width() // 2, self.y - crown.get_height() // 2))
    
    def move(self, row, col):
        """Update piece position and recalc its center coordinates."""
        self.row = row
        self.col = col
        self.calc_pos()


# ---------------- Board Class ----------------
class Board:
    def __init__(self):
        self.board = []
        self.red_left = self.white_left = 12  # each side starts with 12 pieces
        self.red_kings = self.white_kings = 0
        self.create_board()

    def draw_squares(self, win):
        """Draw the checkerboard squares."""
        win.fill(BLACK)
        for row in range(ROWS):
            for col in range(row % 2, COLS, 2):
                pygame.draw.rect(win, GREY, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def create_board(self):
        """Initialize the board with pieces in the proper positions."""
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
        """Draw the board and all the pieces."""
        self.draw_squares(win)
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0:
                    piece.draw(win)

    def move(self, piece, row, col):
        """Move a piece to a new square and promote it to king if it reaches the end."""
        self.board[piece.row][piece.col], self.board[row][col] = 0, piece
        piece.move(row, col)
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
        """Remove captured pieces from the board."""
        for piece in pieces:
            self.board[piece.row][piece.col] = 0
            if piece != 0:
                if piece.color == RED:
                    self.red_left -= 1
                else:
                    self.white_left -= 1

    def winner(self):
        """Return the winner’s color if one side has no pieces left."""
        if self.red_left <= 0:
            return WHITE
        elif self.white_left <= 0:
            return RED
        return None

    def get_valid_moves(self, piece):
        """
        Return a dictionary of valid moves for a given piece.
        Keys are destination (row, col) tuples;
        Values are lists of opponent pieces that would be captured.
        """
        moves = {}
        left = piece.col - 1
        right = piece.col + 1
        row = piece.row

        # For RED pieces (or kings), moves go upward (decreasing row)
        if piece.color == RED or piece.king:
            moves.update(self._traverse_left(row - 1, max(row - 3, -1), -1, piece.color, left))
            moves.update(self._traverse_right(row - 1, max(row - 3, -1), -1, piece.color, right))
        # For WHITE pieces (or kings), moves go downward (increasing row)
        if piece.color == WHITE or piece.king:
            moves.update(self._traverse_left(row + 1, min(row + 3, ROWS), 1, piece.color, left))
            moves.update(self._traverse_right(row + 1, min(row + 3, ROWS), 1, piece.color, right))
        return moves

    def _traverse_left(self, start, stop, step, color, left, skipped=[]):
        """
        Traverse to the left from the given starting point to check for valid moves.
        """
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
        """
        Traverse to the right from the given starting point to check for valid moves.
        """
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


# ---------------- Game Class ----------------
class Game:
    def __init__(self, win):
        self.win = win
        self._init()

    def _init(self):
        self.selected = None
        self.board = Board()
        # RED moves first
        self.turn = RED
        self.valid_moves = {}

    def update(self):
        """Redraw the game window."""
        self.board.draw(self.win)
        self.draw_valid_moves(self.valid_moves)
        pygame.display.update()

    def reset(self):
        self._init()

    def select(self, row, col):
        """
        Select a piece to move or move the selected piece.
        If the piece is already in a multi‐jump sequence, prevent changing the piece.
        """
        # If a piece is already selected (in a multi‐jump sequence),
        # only allow moves for that same piece.
        if self.selected:
            if (row, col) in self.valid_moves:
                self._move(row, col)
            return True

        piece = self.board.get_piece(row, col)
        if piece != 0 and piece.color == self.turn:
            self.selected = piece
            moves = self.board.get_valid_moves(piece)
            # Enforce mandatory capture: if capturing moves exist, only allow them.
            capture_moves = {move: skipped for move, skipped in moves.items() if skipped}
            self.valid_moves = capture_moves if capture_moves else moves
            return True

        return False

    def _move(self, row, col):
        """
        Move the selected piece if the destination is valid.
        If a capture is made, check for additional capturing moves (multi‐jump).
        """
        if self.selected and (row, col) in self.valid_moves:
            captured = self.valid_moves[(row, col)]
            self.board.move(self.selected, row, col)
            if captured:
                self.board.remove(captured)
                # After capturing, check if further capture moves are available from the new position.
                new_moves = self.board.get_valid_moves(self.selected)
                capture_moves = {move: skipped for move, skipped in new_moves.items() if skipped}
                if capture_moves:
                    # Continue multi‐jump: update valid moves and do not change turn.
                    self.valid_moves = capture_moves
                    return True
            # No further captures available: change turn.
            self.change_turn()
            return True
        return False

    def draw_valid_moves(self, moves):
        """Highlight valid moves on the board."""
        for move in moves:
            row, col = move
            pygame.draw.circle(
                self.win, BLUE,
                (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2),
                15
            )

    def change_turn(self):
        """Switch the turn to the other player and clear any selections."""
        self.valid_moves = {}
        self.selected = None
        self.turn = WHITE if self.turn == RED else RED


# ---------------- Main Game Loop ----------------
def main():
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Checkers with Multi-Jump Enforcement")
    game = Game(win)
    clock = pygame.time.Clock()

    run = True
    while run:
        clock.tick(60)  # 60 frames per second

        # Check for a winner
        if game.board.winner() is not None:
            winner_color = game.board.winner()
            print(f"Game Over! {'RED' if winner_color == RED else 'WHITE'} wins!")
            run = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                row = pos[1] // SQUARE_SIZE
                col = pos[0] // SQUARE_SIZE
                game.select(row, col)

        game.update()

    pygame.quit()


if __name__ == "__main__":
    main()
