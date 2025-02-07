import pygame
import sys

# Initialize Pygame
pygame.init()

# ----- Global Constants -----
WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

# RGB Colors
RED    = (255, 0, 0)
WHITE  = (255, 255, 255)
BLACK  = (0, 0, 0)
GREY   = (128, 128, 128)
BLUE   = (0, 0, 255)

# ----- Piece Class -----
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
        """Draw the piece (with an outline and a king mark if needed)."""
        radius = SQUARE_SIZE // 2 - self.PADDING
        # Draw the outline circle (in grey)
        pygame.draw.circle(win, GREY, (self.x, self.y), radius + self.OUTLINE)
        # Draw the actual piece
        pygame.draw.circle(win, self.color, (self.x, self.y), radius)
        if self.king:
            # Mark the piece as king by drawing a "K" in the center
            font = pygame.font.SysFont("comicsans", 30)
            crown = font.render("K", True, BLUE)
            win.blit(crown, (self.x - crown.get_width()//2, self.y - crown.get_height()//2))
    
    def move(self, row, col):
        """Update piece’s row and column, and recalc its center."""
        self.row = row
        self.col = col
        self.calc_pos()


# ----- Board Class -----
class Board:
    def __init__(self):
        self.board = []
        self.red_left = self.white_left = 12  # each side starts with 12 pieces
        self.red_kings = self.white_kings = 0
        self.create_board()

    def draw_squares(self, win):
        """Draw the checkerboard (only the dark squares are drawn)."""
        win.fill(BLACK)
        for row in range(ROWS):
            # Offset every other row
            for col in range(row % 2, COLS, 2):
                pygame.draw.rect(win, GREY, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def create_board(self):
        """Create and place all pieces on the board."""
        for row in range(ROWS):
            self.board.append([])
            for col in range(COLS):
                # Only place pieces on the dark squares
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
        """Draw the board and all pieces."""
        self.draw_squares(win)
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0:
                    piece.draw(win)

    def move(self, piece, row, col):
        """Move a piece to a new location and king it if it reaches the end."""
        self.board[piece.row][piece.col], self.board[row][col] = 0, piece
        piece.move(row, col)

        # Promote to king if piece reaches the end row
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
        """Return the winning color if a side has no remaining pieces."""
        if self.red_left <= 0:
            return WHITE
        elif self.white_left <= 0:
            return RED
        return None

    def get_valid_moves(self, piece):
        """Return a dictionary of valid moves for the given piece.
        
        The keys are destination (row, col) tuples; the values are lists of pieces
        that would be captured in that move.
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
        """Traverse to the left looking for valid moves and captures."""
        moves = {}
        last = []
        for r in range(start, stop, step):
            if left < 0:
                break

            current = self.board[r][left]
            if current == 0:
                # Empty square: if there was a capture, you must capture
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r, left)] = last + skipped
                else:
                    moves[(r, left)] = last

                # If a capture was made, look for additional jumps from here.
                if last:
                    next_r = r + step
                    if 0 <= next_r < ROWS:
                        moves.update(self._traverse_left(r + step, stop, step, color, left - 1, skipped=last))
                        moves.update(self._traverse_right(r + step, stop, step, color, left + 1, skipped=last))
                break
            elif current.color == color:
                break
            else:
                # Opponent piece encountered: mark it as a candidate to capture
                last = [current]

            left -= 1

        return moves

    def _traverse_right(self, start, stop, step, color, right, skipped=[]):
        """Traverse to the right looking for valid moves and captures."""
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


# ----- Game Class -----
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
        """Select a piece or move a selected piece."""
        if self.selected:
            result = self._move(row, col)
            if not result:
                # If move is not valid, clear the selection and try to select again.
                self.selected = None
                self.select(row, col)

        piece = self.board.get_piece(row, col)
        if piece != 0 and piece.color == self.turn:
            self.selected = piece
            self.valid_moves = self.board.get_valid_moves(piece)
            return True

        return False

    def _move(self, row, col):
        """Move the selected piece if the destination is valid."""
        if self.selected and (row, col) in self.valid_moves:
            self.board.move(self.selected, row, col)
            skipped = self.valid_moves[(row, col)]
            if skipped:
                self.board.remove(skipped)
            self.change_turn()
        else:
            return False
        return True

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
        """Switch the turn to the other player."""
        self.valid_moves = {}
        self.selected = None
        self.turn = WHITE if self.turn == RED else RED


# ----- Main Game Loop -----
def main():
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Checkers")
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
