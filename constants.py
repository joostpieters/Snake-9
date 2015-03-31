__author__ = 'Aaron'

# CONSTANTS
FRAMES_PER_SEC = 25
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
NUM_ROWS = 30
NUM_COLS = 45
DISPLAY_MARGIN = 80  # Used to display player scores and player names
CELL_MARGIN = 1 # TODO need to make this able to be changed, fill_gap and render calcs are off

RED = (255, 0, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
GRAY = (40, 40, 40)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
# DEFAULT_COLOR = (111, 198, 217)
MARGIN_COLOR = GRAY
DEFAULT_COLOR = BLACK

FOOD = 10
EMPTY = 0

# CALCULATED CONSTANTS
HORIZONTAL_MARGINS = ((NUM_COLS + 1) * CELL_MARGIN)
VERTICAL_MARGINS = ((NUM_ROWS + 1) * CELL_MARGIN)
CELL_SIDE = min((SCREEN_WIDTH - HORIZONTAL_MARGINS) // NUM_COLS,
                (SCREEN_HEIGHT - DISPLAY_MARGIN - VERTICAL_MARGINS) // NUM_ROWS)
HORIZONTAL_OFFSET = (SCREEN_WIDTH - (CELL_SIDE * NUM_COLS + HORIZONTAL_MARGINS)) / 2 + CELL_MARGIN
VERTICAL_OFFSET = DISPLAY_MARGIN * 1.2

UP_L = (HORIZONTAL_OFFSET - 1, VERTICAL_OFFSET - 1)
UP_R = (HORIZONTAL_OFFSET + NUM_COLS * CELL_SIDE + HORIZONTAL_MARGINS - 1, VERTICAL_OFFSET - 1)
LOW_L = (HORIZONTAL_OFFSET - 1, VERTICAL_OFFSET + NUM_ROWS * CELL_SIDE + VERTICAL_MARGINS - 1)
LOW_R = (HORIZONTAL_OFFSET + NUM_COLS * CELL_SIDE + HORIZONTAL_MARGINS - 1,
         VERTICAL_OFFSET + NUM_ROWS * CELL_SIDE + VERTICAL_MARGINS - 1)