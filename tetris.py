"""Simple Tetris clone built with pygame.

This script provides a minimal but playable version of the classic
Tetris game.  To play, install ``pygame`` (``pip install pygame``) and run
``python tetris.py``.  Use the arrow keys to move/rotate pieces and the
space bar to instantly drop a piece.
"""

from __future__ import annotations

import pygame
import random
from typing import Dict, List, Tuple


# Screen configuration
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 700
PLAY_WIDTH = 300  # 10 columns * 30 pixels
PLAY_HEIGHT = 600  # 20 rows * 30 pixels
BLOCK_SIZE = 30


TOP_LEFT_X = (WINDOW_WIDTH - PLAY_WIDTH) // 2
TOP_LEFT_Y = WINDOW_HEIGHT - PLAY_HEIGHT - 50


# fmt: off
S_SHAPE = [['.....',
            '.....',
            '..00.',
            '.00..',
            '.....'],
           ['.....',
            '..0..',
            '..00.',
            '...0.',
            '.....']]

Z_SHAPE = [['.....',
            '.....',
            '.00..',
            '..00.',
            '.....'],
           ['.....',
            '..0..',
            '.00..',
            '.0...',
            '.....']]

I_SHAPE = [['..0..',
            '..0..',
            '..0..',
            '..0..',
            '.....'],
           ['.....',
            '0000.',
            '.....',
            '.....',
            '.....']]

O_SHAPE = [['.....',
            '.....',
            '.00..',
            '.00..',
            '.....']]

J_SHAPE = [['.....',
            '.0...',
            '.000.',
            '.....',
            '.....'],
           ['.....',
            '..00.',
            '..0..',
            '..0..',
            '.....'],
           ['.....',
            '.....',
            '.000.',
            '...0.',
            '.....'],
           ['.....',
            '..0..',
            '..0..',
            '.00..',
            '.....']]

L_SHAPE = [['.....',
            '...0.',
            '.000.',
            '.....',
            '.....'],
           ['.....',
            '..0..',
            '..0..',
            '..00.',
            '.....'],
           ['.....',
            '.....',
            '.000.',
            '.0...',
            '.....'],
           ['.....',
            '.00..',
            '..0..',
            '..0..',
            '.....']]

T_SHAPE = [['.....',
            '..0..',
            '.000.',
            '.....',
            '.....'],
           ['.....',
            '..0..',
            '..00.',
            '..0..',
            '.....'],
           ['.....',
            '.....',
            '.000.',
            '..0..',
            '.....'],
           ['.....',
            '..0..',
            '.00..',
            '..0..',
            '.....']]
# fmt: on

SHAPES: List[List[List[str]]] = [S_SHAPE, Z_SHAPE, I_SHAPE, O_SHAPE, J_SHAPE, L_SHAPE, T_SHAPE]
SHAPE_COLORS: List[Tuple[int, int, int]] = [
    (0, 255, 0),
    (255, 0, 0),
    (0, 255, 255),
    (255, 255, 0),
    (255, 165, 0),
    (0, 0, 255),
    (128, 0, 128),
]


class Piece:
    """Representation of a tetromino piece."""

    def __init__(self, column: int, row: int, shape: List[List[str]]):
        self.x = column
        self.y = row
        self.shape = shape
        self.color = SHAPE_COLORS[SHAPES.index(shape)]
        self.rotation = 0


def create_grid(locked_positions: Dict[Tuple[int, int], Tuple[int, int, int]]) -> List[List[Tuple[int, int, int]]]:
    """Create a grid with locked positions filled."""

    grid = [[(0, 0, 0) for _ in range(10)] for _ in range(20)]

    for (col, row), color in locked_positions.items():
        if row >= 0:
            grid[row][col] = color

    return grid


def convert_shape_format(piece: Piece) -> List[Tuple[int, int]]:
    """Return a list of positions occupied by the piece."""

    positions: List[Tuple[int, int]] = []
    shape = piece.shape[piece.rotation % len(piece.shape)]

    for i, line in enumerate(shape):
        for j, column in enumerate(line):
            if column == "0":
                positions.append((piece.x + j, piece.y + i))

    # Offset for the 5x5 grid representation
    return [(x - 2, y - 4) for x, y in positions]


def valid_space(piece: Piece, grid: List[List[Tuple[int, int, int]]]) -> bool:
    """Check whether the piece can be placed on the grid."""

    accepted_positions = [
        (j, i)
        for i in range(len(grid))
        for j in range(len(grid[i]))
        if grid[i][j] == (0, 0, 0)
    ]

    formatted = convert_shape_format(piece)

    for pos in formatted:
        if pos not in accepted_positions and pos[1] > -1:
            return False

    return True


def check_lost(positions: Dict[Tuple[int, int], Tuple[int, int, int]]) -> bool:
    """Game over if any locked piece is above the top of the play area."""

    return any(y < 1 for (_, y) in positions)


def get_shape() -> Piece:
    """Return a new random tetromino."""

    shape = random.choice(SHAPES)
    return Piece(5, 0, shape)


def draw_text_middle(surface: pygame.Surface, text: str, size: int, color: Tuple[int, int, int]) -> None:
    """Draw text centered on the play field."""

    font = pygame.font.SysFont("comicsans", size, bold=True)
    label = font.render(text, True, color)

    surface.blit(
        label,
        (
            TOP_LEFT_X + PLAY_WIDTH / 2 - label.get_width() / 2,
            TOP_LEFT_Y + PLAY_HEIGHT / 2 - label.get_height() / 2,
        ),
    )


def draw_grid(surface: pygame.Surface, grid: List[List[Tuple[int, int, int]]]) -> None:
    """Draw the grid lines for the play area."""

    for i in range(len(grid)):
        pygame.draw.line(
            surface,
            (128, 128, 128),
            (TOP_LEFT_X, TOP_LEFT_Y + i * BLOCK_SIZE),
            (TOP_LEFT_X + PLAY_WIDTH, TOP_LEFT_Y + i * BLOCK_SIZE),
        )
    for j in range(len(grid[0])):
        pygame.draw.line(
            surface,
            (128, 128, 128),
            (TOP_LEFT_X + j * BLOCK_SIZE, TOP_LEFT_Y),
            (TOP_LEFT_X + j * BLOCK_SIZE, TOP_LEFT_Y + PLAY_HEIGHT),
        )


def clear_rows(grid: List[List[Tuple[int, int, int]]], locked: Dict[Tuple[int, int], Tuple[int, int, int]]) -> int:
    """Clear completed rows and update locked positions."""

    rows_to_clear = [i for i in range(len(grid) - 1, -1, -1) if (0, 0, 0) not in grid[i]]

    if not rows_to_clear:
        return 0

    for row in rows_to_clear:
        for j in range(len(grid[row])):
            locked.pop((j, row), None)

    # Shift everything above the cleared rows down
    rows_cleared = len(rows_to_clear)
    rows_to_clear.sort()
    for key in sorted(list(locked), key=lambda x: x[1]):
        x, y = key
        shift = sum(1 for cleared_row in rows_to_clear if cleared_row < y)
        if shift:
            color = locked.pop(key)
            locked[(x, y - shift)] = color

    return rows_cleared


def draw_next_shape(surface: pygame.Surface, piece: Piece) -> None:
    """Display the next piece preview."""

    font = pygame.font.SysFont("comicsans", 30)
    label = font.render("Próxima peça", True, (255, 255, 255))

    sx = TOP_LEFT_X + PLAY_WIDTH + 50
    sy = TOP_LEFT_Y + PLAY_HEIGHT / 2 - 100

    surface.blit(label, (sx + 10, sy - 30))
    formatted = piece.shape[piece.rotation % len(piece.shape)]

    for i, line in enumerate(formatted):
        for j, column in enumerate(line):
            if column == "0":
                pygame.draw.rect(
                    surface,
                    piece.color,
                    (sx + j * BLOCK_SIZE, sy + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE),
                )


def draw_window(surface: pygame.Surface, grid: List[List[Tuple[int, int, int]]], score: int = 0) -> None:
    """Render the main game window."""

    surface.fill((0, 0, 0))

    font = pygame.font.SysFont("comicsans", 60)
    label = font.render("TETRIS", True, (255, 255, 255))
    surface.blit(label, (TOP_LEFT_X + PLAY_WIDTH / 2 - label.get_width() / 2, 30))

    score_font = pygame.font.SysFont("comicsans", 30)
    score_label = score_font.render(f"Pontuação: {score}", True, (255, 255, 255))
    surface.blit(score_label, (TOP_LEFT_X - 200, TOP_LEFT_Y + 100))

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            color = grid[i][j]
            if color != (0, 0, 0):
                pygame.draw.rect(
                    surface,
                    color,
                    (TOP_LEFT_X + j * BLOCK_SIZE, TOP_LEFT_Y + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE),
                )

    pygame.draw.rect(surface, (255, 0, 0), (TOP_LEFT_X, TOP_LEFT_Y, PLAY_WIDTH, PLAY_HEIGHT), 4)
    draw_grid(surface, grid)


def main() -> None:
    """Main game loop."""

    locked_positions: Dict[Tuple[int, int], Tuple[int, int, int]] = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.5
    score = 0

    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick()

        if fall_time / 1000 >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                elif event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
                elif event.key == pygame.K_UP:
                    current_piece.rotation = (current_piece.rotation + 1) % len(current_piece.shape)
                    if not valid_space(current_piece, grid):
                        current_piece.rotation = (current_piece.rotation - 1) % len(current_piece.shape)
                elif event.key == pygame.K_SPACE:
                    while valid_space(current_piece, grid):
                        current_piece.y += 1
                    current_piece.y -= 1
                    change_piece = True

        shape_pos = convert_shape_format(current_piece)

        for x, y in shape_pos:
            if y > -1:
                grid[y][x] = current_piece.color

        if change_piece:
            for pos in shape_pos:
                locked_positions[(pos[0], pos[1])] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            rows_cleared = clear_rows(grid, locked_positions)
            score += rows_cleared * 100

        draw_window(win, grid, score)
        draw_next_shape(win, next_piece)
        pygame.display.update()

        if check_lost(locked_positions):
            draw_text_middle(win, "Fim de jogo", 80, (255, 255, 255))
            pygame.display.update()
            pygame.time.delay(2000)
            run = False


def main_menu() -> None:
    """Display a simple start screen."""

    run = True
    while run:
        win.fill((0, 0, 0))
        draw_text_middle(win, "Pressione qualquer tecla para iniciar", 60, (255, 255, 255))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                main()
    pygame.quit()


pygame.font.init()
win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Tetris")


if __name__ == "__main__":
    main_menu()

