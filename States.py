__author__ = 'Aaron'

# IMPORTS
import pygame
from pygame.locals import *

from Player import *
from Food import *
from constants import *


# STATE DEFINITIONS
class State(object):
    def __init__(self):
        self.manager = None

    def render(self, screen):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    def handle_events(self, events):
        raise NotImplementedError


class MenuState(State):
    def __init__(self):
        super(MenuState, self).__init__()
        self.font = pygame.font.SysFont(FONT, 24)

        self.text = self.font.render(
            "Press SPACE to view the instructions", True, WHITE)
        self.text_rect = self.text.get_rect()
        self.text_rect.x = SCREEN_WIDTH // 2 - (self.text_rect.width // 2)
        self.text_rect.y = SCREEN_HEIGHT // 2 - self.text_rect.height

        self.text1 = self.font.render("Press ENTER to begin", True, WHITE)
        self.text1_rect = self.text1.get_rect()
        self.text1_rect.x = SCREEN_WIDTH // 2 - (self.text1_rect.width // 2)
        self.text1_rect.y = SCREEN_HEIGHT // 2 + (self.text1_rect.height // 2)

    def render(self, screen):
        screen.fill(BLACK)
        screen.blit(self.text, self.text_rect)
        screen.blit(self.text1, self.text1_rect)

    def update(self):
        pass

    def handle_events(self, events):
        for e in events:
            if e.type == KEYDOWN and e.key == K_RETURN:
                self.manager.go_to(PlayState())
            elif e.type == KEYDOWN and e.key == K_SPACE:
                self.manager.go_to(OptionsState())


class OptionsState(State):
    def __init__(self):
        super(OptionsState, self).__init__()
        self.font = pygame.font.SysFont(FONT, 24)
        self.text = self.font.render(
            "The player uses the arrow keys to move up, left, down, and right.", True, WHITE)
        self.text_rect = self.text.get_rect()
        self.text_rect.x = SCREEN_WIDTH // 2 - (self.text_rect.width // 2)
        self.text_rect.y = SCREEN_HEIGHT // 2 - self.text_rect.height

        self.text1 = self.font.render("Press ENTER to begin", True, WHITE)
        self.text1_rect = self.text1.get_rect()
        self.text1_rect.x = SCREEN_WIDTH // 2 - (self.text1_rect.width // 2)
        self.text1_rect.y = SCREEN_HEIGHT // 2 + (self.text1_rect.height // 2)

    def render(self, screen):
        screen.fill(BLACK)
        screen.blit(self.text, self.text_rect)
        screen.blit(self.text1, self.text1_rect)

    def update(self):
        pass

    def handle_events(self, events):
        for e in events:
            if e.type == KEYDOWN and e.key == K_RETURN:
                self.manager.go_to(PlayState())


class PlayState(State):
    def __init__(self):
        super(PlayState, self).__init__()

        # PLAYER, BOARD, FOOD
        self.player = Player((NUM_ROWS // 2, NUM_COLS // 2), 'START', BLUE, 2)
        self.board = Board()
        self.food = Food()
        self.initialized = True  # flag used for initial board generation

        # FITNESS FUNCTION KILL SWITCH
        self.moves_since_food = 0

        # PLAYER NAMES & SCORES
        self.font = pygame.font.SysFont(FONT, 24)
        self.player_text = self.font.render("Player 1: {0:>4d}".format(self.player.score), True,
                                            WHITE)  # TODO make color generic for choice
        self.player_text_pos = self.player_text.get_rect()

        self.player_text_pos.x = self.player_text_pos.y = CELL_SIDE

        # LOGO
        self.logo_text = pygame.font.SysFont(
            FONT, 48).render("SNAKE", True, (0, 255, 0))
        self.logo_text_pos = self.logo_text.get_rect()
        self.logo_text_pos.x = SCREEN_WIDTH // 2
        self.logo_text_pos.y = CELL_SIDE

    @staticmethod
    def draw_bounds(line_color, screen):
        """
        Draws to the screen the initial bounding box of the game, passed a color.
        Locations are based off of calculated constants.
        :param line_color: color to set the bounds
        :param screen: surface reference
        """
        # Draw top, bottom, left, right bounds
        pygame.draw.line(screen, line_color, UP_L, UP_R)
        pygame.draw.line(screen, line_color, LOW_L, LOW_R)
        pygame.draw.line(screen, line_color, UP_L, LOW_L)
        pygame.draw.line(screen, line_color, UP_R, LOW_R)

    @staticmethod
    def draw_margins(line_color, screen):
        """
        Draws to the screen all the margins between cells.
        :param line_color: color to set the margins
        :param screen: surface reference
        """
        for row in range(1, NUM_ROWS + 1):
            # DRAW HORIZONTAL MARGINS
            x0 = HORIZONTAL_OFFSET
            x1 = SCREEN_WIDTH - HORIZONTAL_OFFSET - CELL_MARGIN
            y0 = y1 = (CELL_MARGIN + CELL_SIDE) * row + \
                VERTICAL_OFFSET - CELL_MARGIN
            pygame.draw.line(screen, line_color, (x0, y0), (x1, y1))

        for column in range(1, NUM_COLS + 1):
            # DRAW VERTICAL MARGINS
            x0 = x1 = (CELL_MARGIN + CELL_SIDE) * column + \
                HORIZONTAL_OFFSET - CELL_MARGIN
            y0 = VERTICAL_OFFSET
            y1 = VERTICAL_OFFSET + VERTICAL_MARGINS + \
                (CELL_SIDE * NUM_ROWS) - 2 * CELL_MARGIN
            pygame.draw.line(screen, line_color, (x0, y0), (x1, y1))

    @staticmethod
    def draw_cell(row, column, cell_color, screen):
        """
        Draws to the screen a rectangle of a given color corresponding to a board matrix cell.
        :param row: row of cell
        :param column: column of cell
        :param cell_color: player color to paint
        :param screen: surface reference
        """
        pygame.draw.rect(screen, cell_color,
                         [(CELL_MARGIN + CELL_SIDE) * column + HORIZONTAL_OFFSET,
                          (CELL_MARGIN + CELL_SIDE) * row + VERTICAL_OFFSET,
                          CELL_SIDE,
                          CELL_SIDE])

    @staticmethod
    def fill_gap(pos, direction, line_color, screen):
        # TODO clean up calculations
        """
        Draws the transitions between player cells
        :param direction: direction from a given position to the next
        :param line_color: player color
        :param screen: surface reference
        """

        if direction == 'START':
            return

        (row, column) = pos

        start = end = None
        if direction == 'LEFT' or direction == 'UP':
            start = ((CELL_MARGIN + CELL_SIDE) * column + HORIZONTAL_OFFSET - CELL_MARGIN,
                     (CELL_MARGIN + CELL_SIDE) * row + VERTICAL_OFFSET - CELL_MARGIN)
            if direction == 'LEFT':
                end = (start[0], start[1] + CELL_SIDE)
                start = (start[0], start[1] + CELL_MARGIN)
            else:
                end = (start[0] + CELL_SIDE, start[1])
                start = (start[0] + 1, start[1])
        elif direction == 'RIGHT' or direction == 'DOWN':
            end = ((CELL_MARGIN + CELL_SIDE) * (column + 1) + HORIZONTAL_OFFSET - CELL_MARGIN,
                   (CELL_MARGIN + CELL_SIDE) * (row + 1) + VERTICAL_OFFSET - CELL_MARGIN)
            if direction == 'RIGHT':
                start = (end[0], end[1] - CELL_SIDE)
                end = (end[0], end[1] - CELL_MARGIN)
            else:
                start = (end[0] - CELL_SIDE, end[1])
                end = (end[0] - CELL_MARGIN, end[1])

        pygame.draw.line(screen, line_color, start, end)

    def face_nonempty(self, row, column, direction):
        """
        Boolean expression describing whether a player is currently adjacent to and facing a nonempty cell.
        :param row: row of current position
        :param column: column of current position
        :param direction: direction player is facing
        :return: True if adjacent to a nonempty cell and facing it, False otherwise
        """
        if (row == 0 and direction == 'UP') or (row == NUM_ROWS - 1 and direction == 'DOWN'):
            return True
        elif (column == 0 and direction == 'LEFT') or (column == NUM_COLS - 1 and direction == 'RIGHT'):
            return True

        if direction == 'UP':
            row -= 1
        elif direction == 'DOWN':
            row += 1
        elif direction == 'LEFT':
            column -= 1
        elif direction == 'RIGHT':
            column += 1

        next_cell = self.board.get_cell(row, column)
        return next_cell != 0

    def render(self, screen):
        if screen is None:
            return

        # DRAW INITIAL BOARD
        if self.initialized:
            screen.fill(BLACK)
            for row in range(NUM_ROWS):
                for column in range(NUM_COLS):
                    cell_color = DEFAULT_COLOR
                    PlayState.draw_cell(row, column, cell_color, screen)
            PlayState.draw_bounds(WHITE, screen)
            PlayState.draw_margins(MARGIN_COLOR, screen)
            self.initialized = False

        player = self.player
        food = self.food

        # PAINT OVER DELETED CELLS
        delete = player.delete
        if delete[0] is not None and delete[1] is not None:
            row, column = delete[0]
            transition = delete[1]
            self.draw_cell(row, column, DEFAULT_COLOR, screen)
            # PlayState.fill_gap((row, column), transition, MARGIN_COLOR, screen)

        old_center = food.old_center
        if (old_center is not None) and (not Board.cell_equals(old_center, food.center)):
            pygame.draw.circle(screen, DEFAULT_COLOR,
                               food.old_center, food.radius)

        # DRAW FOOD
        pygame.draw.circle(screen, food.color, food.center, food.radius)

        # DRAW PREVIOUS CELLS AND TRANSITIONS
        positions = player.positions
        transitions = player.transitions
        for i in range(len(transitions)):
            row, column = positions[i]
            # transition = transitions[i]
            self.draw_cell(row, column, player.color, screen)
            # PlayState.fill_gap((row, column), transition, player.color, screen)

        # DRAW CURRENT POSITION
        row, column = player.get_position()
        self.draw_cell(row, column, player.color, screen)

        # UPDATE TEXT
        # TODO make color generic for choice
        self.player_text = self.font.render(
            "Player 1: {0:4d}".format(self.player.score), True, WHITE)
        rect = self.player_text_pos
        rect.width += 20
        pygame.draw.rect(screen, DEFAULT_COLOR, rect)
        screen.blit(self.player_text, self.player_text_pos)

        screen.blit(self.logo_text, self.logo_text_pos)

    def update(self):
        player = self.player
        player.delete = None, None

        # UPDATE NEXT MOVE
        player.direction = self.get_move()

        # PLAYER POSITION UPDATE
        row, column = player.update()
        valid = player.set_position(row, column)
        self.moves_since_food += 1

        # WALL/BOUNDS COLLISION CHECK
        if valid == -1 and player.direction != 'START':
            self.end_game()
        elif self.manager.ann is not None and self.moves_since_food >= (NUM_ROWS * NUM_COLS) // 2:
            self.end_game()

        # UPDATE SNAKE TAIL (GRID)
        delete = player.delete
        if delete[0] is not None and delete[1] is not None:
            position = delete[0]
            self.board.set_cell(position[0], position[1], EMPTY)
            player.position_set.remove(position)

        # SELF/FOOD COLLISION CHECK AND BOARD UPDATE
        food = self.food
        ate_food = self.board.check_collision((row, column))
        if ate_food == -1 and player.direction != 'START':
            self.end_game()
        else:
            self.board.set_cell(row, column, player.number)
            if ate_food == 1:
                self.board.set_cell(food.position[0], food.position[1], EMPTY)
                food.move()
                while self.board.get_cell(food.position[0], food.position[1]) != EMPTY:
                    food.move()
                player.score += food.score
                player.length += 1
                self.moves_since_food = 0

        # FOOD UPDATE
        self.board.set_cell(food.position[0], food.position[1], FOOD)

    def end_game(self):
        """
        Transitions to game over state and updates the StateManager score for fitness function
        to use.
        """
        # Fitness calculation
        self.manager.fitness = 10 * self.player.score

        dist_x, dist_y = Board.distance_to(
            self.player.get_position(), self.food.position)
        self.manager.fitness += NUM_ROWS - abs(dist_y)
        self.manager.fitness += NUM_COLS - abs(dist_x)

        self.manager.go_to(GameOverState())

    def get_move(self):
        """
        Get the next move to make. Next keypress if human player, output of neural network otherwise.
        :return: next direction to move in
        """
        if self.manager.ann is None:
            keypress = pygame.key.get_pressed()
            if keypress[K_LEFT]:
                return 'LEFT'
            elif keypress[K_UP]:
                return 'UP'
            elif keypress[K_DOWN]:
                return 'DOWN'
            elif keypress[K_RIGHT]:
                return 'RIGHT'
            else:
                return self.player.direction  # continue going in same direction
        else:
            outputs = self.manager.ann.update(self.ann_inputs())
            max_output = max(outputs)
            if outputs[0] is max_output:
                return 'LEFT'
            elif outputs[1] is max_output:
                return 'UP'
            elif outputs[2] is max_output:
                return 'DOWN'
            elif outputs[3] is max_output:
                return 'RIGHT'

    def ann_inputs(self):
        """
        Return a list of the necessary inputs for a neural network.
        :return: [Manhattan distance to food (x, y), state of board to left,
                  in front of, and right of the player]
        """
        row, col = self.player.get_position()
        dist_x, dist_y = Board.distance_to((row, col), self.food.position)
        left = self.board.get_cell(row, col - 1)
        up = self.board.get_cell(row - 1, col)
        down = self.board.get_cell(row + 1, col)
        right = self.board.get_cell(row, col + 1)

        direction = self.player.direction
        if direction == 'UP':
            inputs = [dist_x, dist_y, left, up, right]
        elif direction == 'LEFT':
            inputs = [dist_x, dist_y, down, left, up]
        elif direction == 'DOWN':
            inputs = [dist_x, dist_y, right, down, left]
        elif direction == 'RIGHT':
            inputs = [dist_x, dist_y, up, right, down]
        else:
            inputs = [dist_x, dist_y, left, up, right]

        return inputs

    def handle_events(self, events):
        for e in events:
            if e.type == KEYDOWN and e.key == K_ESCAPE:
                self.manager.go_to(MenuState())


class PauseState(State):
    def __init__(self):
        super(PauseState, self).__init__()
        self.font = pygame.font.SysFont(FONT, 24)
        self.text = self.font.render(
            "Paused, press ENTER to unpause", True, WHITE)
        self.text_rect = self.text.get_rect()
        self.dim = Dimmer(1)
        self.shouldDim = 1

    def render(self, screen):
        if self.shouldDim:
            self.dim.dim(255 * 2 / 3)
            self.shouldDim = 0
        text_rect = self.text_rect
        text_x = screen.get_width() / 2 - text_rect.width / 2
        text_y = screen.get_height() / 2 - text_rect.height / 2
        screen.blit(self.text, [text_x, text_y])

    def update(self):
        pass

    def handle_events(self, events):
        # self.dim.undim()
        for e in events:
            if e.type == KEYDOWN and e.key == K_RETURN:
                self.manager.go_to(PlayState())


class GameOverState(State):
    def __init__(self):
        super(GameOverState, self).__init__()
        self.font = pygame.font.SysFont(FONT, 24)
        self.text = self.font.render("Game Over", True, WHITE)
        self.text_rect = self.text.get_rect()
        self.has_dimmed = 0

    def render(self, screen):
        if screen is None:
            return
        if self.has_dimmed == 0:
            self.dim = Dimmer(1)
            self.dim.dim(255 * 2 / 3)
            self.has_dimmed = 1
        text_rect = self.text_rect
        text_x = screen.get_width() / 2 - text_rect.width / 2
        text_y = screen.get_height() / 2 - text_rect.height / 2
        screen.blit(self.text, [text_x, text_y])

    def update(self):
        pass

    def handle_events(self, events):
        # self.dim.undim()
        for e in events:
            if e.type == KEYDOWN and e.key == K_RETURN:
                self.manager.fitness = 0
                self.manager.go_to(PlayState())
            elif e.type == KEYDOWN and e.key == K_ESCAPE:
                self.manager.fitness = 0
                self.manager.go_to(MenuState())


class Dimmer:
    def __init__(self, keep_alive=0):
        self.keep_alive = keep_alive
        if self.keep_alive:
            self.buffer = pygame.Surface(
                pygame.display.get_surface().get_size())
        else:
            self.buffer = None

    def dim(self, darken_factor=64, color_filter=BLACK):
        if not self.keep_alive:
            self.buffer = pygame.Surface(
                pygame.display.get_surface().get_size())
        self.buffer.blit(pygame.display.get_surface(), (0, 0))
        if darken_factor > 0:
            darken = pygame.Surface(pygame.display.get_surface().get_size())
            darken.fill(color_filter)
            darken.set_alpha(darken_factor)
            # safe old clipping rectangle...
            old_clip = pygame.display.get_surface().get_clip()
            # blit over entire screen...
            pygame.display.get_surface().blit(darken, (0, 0))
            pygame.display.flip()
            # ... and restore clipping
            pygame.display.get_surface().set_clip(old_clip)

    def undim(self):
        if self.buffer:
            pygame.display.get_surface().blit(self.buffer, (0, 0))
            pygame.display.flip()
            if not self.keep_alive:
                self.buffer = None
