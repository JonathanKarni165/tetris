import pygame
from time import sleep
from pygame import draw
from random import randint
import threading
from enum import Enum

WINDOW_SCALE = (300, 500)
TILE_SCALE = 20
# visual sprite scale
BLOCK_SCALE = 18

ROWS = WINDOW_SCALE[1] // TILE_SCALE
COLLUMNS = WINDOW_SCALE[0] // TILE_SCALE

FPS = 60
# time between each frame
DELTA_TIME = 1 / FPS
# delay frame for horizontal movement
HORIZONTAL_DELAY_FRAMES = 5

HORIZONTAL_SPEED = 1
VERTICAL_SPEED = 1
# starts from zero, increasing each row clear
VERTICAL_SPEED_BONUS = 0.0
# add to bonus each clear
VERTICAL_SPEED_INCREMENT = 0.3
VERTICAL_SPEED_FAST_FORWARD = 5.0

PLACE_TETRON_MAX_WAIT = 3
PLACE_TETRON_MIN_WAIT = 1
# add to delay each rotation made to tetron while placing
ROTATE_PLACE_TETRON_INCREMENT = 0.4

# tetron representing matrix is 4X4
TETRON_MATRIX_DIMENSIONS = 4

TETRON_KINDS = 6

WHITE = (255,255,255)
BLACK = (0,0,0)

SCORING_REWARDS = (40,100,300,1200)

#extra options constants
WIDE_WINDOW_SCALE = (600, 600)
FAST_VERTICAL_SPEED = 3
FAST_VERTICAL_SPEED_FAST_FORWARD = 8
FAST_VERTICAL_SPEED_INCREMENT = 0.2
MORE_SHAPES_TETRON_KINDS = 10
HARD_SHPES_TETRON_KINDS = 14

screen = pygame.display.set_mode(WINDOW_SCALE)

# goes into a tile object
class Block(pygame.sprite.Sprite):
    def __init__(self, color, ghost = False):
        self.x = 0
        self.y = 0

        self.width = BLOCK_SCALE
        self.hight = BLOCK_SCALE

        self.tile : Tile = None

        if ghost:
            self.color = BLACK
        else:
            self.color = color

        self.ghost = ghost

        self.rect = pygame.Rect(self.x, self.y, self.width, self.hight)
        draw.rect(screen, self.color, self.rect)

    def move_down(self):
        self.y += TILE_SCALE

    def move_horizontal(self, direction):
        self.x += direction * TILE_SCALE

    def draw(self):
        self.rect = pygame.Rect(self.x, self.y, self.width, self.hight)
        draw.rect(screen, self.color, self.rect)

# manages the blocks that have been placed
class Block_Stack:
    def __init__(self):
        self.stack : list[list[Block]] = []
        self.rows_to_clear = []

    def __str__(self):
        return str([len(row) for row in self.stack])
    
    def add_block(self, block : Block):
        block_row = block.tile.row - 1

        while len(self.stack) < block_row + 1:
            self.stack.append([])
        self.stack[block_row].append(block)
        
        if len(self.stack) >= (WINDOW_SCALE[1] // TILE_SCALE) - 2:
            print('end')
            exit(0)
    
    def clear_line(self):
        row_index = self.rows_to_clear.pop()
        sleep(0.3)
        global VERTICAL_SPEED_BONUS
        # increase speed
        VERTICAL_SPEED_BONUS += VERTICAL_SPEED_INCREMENT

        # drop down all upper levels
        for upper_row_index in range(row_index + 1, len(self.stack)):
            for block in self.stack[upper_row_index]:
                block.move_down()
        
        self.stack.pop(row_index)
    
    # returns number of clears
    def check_for_clear(self):
        clear_count = 0
        row_len_list = []
        for row_index in range(len(self.stack)):
            row_len_list.append(len(self.stack[row_index]))
            if len(self.stack[row_index]) == WINDOW_SCALE[0] // TILE_SCALE:
                print('line clear ', row_index)
                self.rows_to_clear.append(row_index)

                for block in self.stack[row_index]:
                    block.color = WHITE

                clear_count += 1
        return clear_count

    
    def get_block_list(self):
        block_list = []
        for row in self.stack:
            for block in row:
                block_list.append(block)
        return block_list

# all tetris shapes super object
class Tetron:
    def __init__(self, represent_matrix : list[list], color : tuple):
        self.represent_matrix = represent_matrix
        self.block_list : list[Block] = []

        self.move_delay_frames_y = FPS
        self.move_delay_frames_x = HORIZONTAL_DELAY_FRAMES
        self.move_delay_frames_timer_y = FPS
        self.move_delay_frames_timer_x = HORIZONTAL_DELAY_FRAMES

        self.x = COLLUMNS // 2 * TILE_SCALE
        self.y = TILE_SCALE
        self.color = color

        # create tetron from representing matrix
        for i in range(TETRON_MATRIX_DIMENSIONS):
            for j in range(TETRON_MATRIX_DIMENSIONS):
                if self.represent_matrix[i][j]:
                    my_block = Block(color)

                    my_block.x = self.x + (j * TILE_SCALE)
                    my_block.y = self.y + (i * TILE_SCALE)

                    self.block_list.append(my_block)

        # first rotation initialization
        self.rotate()

    def move_down(self):
        # check for collision before moving
        for block in self.block_list:
            if game.grid.cant_move_down(block):
                return
        
        # timing fall rate
        self.move_delay_frames_timer_y -= VERTICAL_SPEED
        if self.move_delay_frames_timer_y > 0 or self.check_vertical_collsion():
            return

        self.move_delay_frames_timer_y = self.move_delay_frames_y

        # move all tetron blocks accordingly
        for block in self.block_list:
            block.move_down()
            # get in a new tile
            game.grid.set_tile(block)

        self.y += TILE_SCALE
        

    def move_horizontal(self, direction):
        # check for collision before moving
        for block in self.block_list:
            if game.grid.cant_move_horizontally(block, direction):
                return
        
        # timing horizontal hold speed
        global HORIZONTAL_DELAY_FRAMES
        self.move_delay_frames_timer_x -= 1
        if self.move_delay_frames_timer_x > 0:
            return
        
        self.move_delay_frames_timer_x = HORIZONTAL_DELAY_FRAMES

        # move all blocks of tetron
        for block in self.block_list:
            block.move_horizontal(direction)
            # set in a new tile
            game.grid.set_tile(block)

        self.x += direction * TILE_SCALE
    
    def check_vertical_collsion(self):
        for block in self.block_list:
            if game.grid.cant_move_down(block):
                return True
        
    def rotate(self):
        rotation_is_not_valid = True
        # will rotate until back to original if all options are not valid
        while rotation_is_not_valid: 

            # flip reprenting matrix
            represent_matrix_temp = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
            for i in range(TETRON_MATRIX_DIMENSIONS):
                for j in range(TETRON_MATRIX_DIMENSIONS):
                    represent_matrix_temp[TETRON_MATRIX_DIMENSIONS-j-1][i] = self.represent_matrix[i][j]

            self.represent_matrix = represent_matrix_temp.copy()
            
            # create flipped tetron from the new represent matrix
            block_index = 0
            for i in range(TETRON_MATRIX_DIMENSIONS):
                for j in range(TETRON_MATRIX_DIMENSIONS):
                    if self.represent_matrix[i][j]:
                        self.block_list[block_index].x = self.x + (i * TILE_SCALE)
                        self.block_list[block_index].y = self.y + (j * TILE_SCALE)
                        block_index += 1
            
            # first rotation call game not yet initialized
            if game is None:
                break
            
            # check if rotation is valid
            all_is_valid = True
            for block in self.block_list:
                if game.grid.overlap_collision(block):
                    all_is_valid = False
            rotation_is_not_valid = not all_is_valid


# represent one cell from the grid
class Tile():
    def __init__(self, row, col):
        self.row = row
        self.col = col

        self.is_on = False
        self.is_in_stack = False
        self.block : Block = None
    
    def set_values(self, block, is_on, is_in_stack):
        self.is_on = is_on
        self.block = block
        self.is_in_stack = is_in_stack

# slices the screen to tiles while each tile can contain a block
class Grid:
    def __init__(self):
        self.tile_matrix : list[list[Tile]] = [[Tile(i,j) for j in range(COLLUMNS)] for i in range(ROWS)]
        self.block_stack : Block_Stack = Block_Stack()
    
    def __str__(self):
        str = '\n\n'
        for i in range(len(self.tile_matrix)-1 , 0, -1):
            str += '\n'
            for j in range(COLLUMNS):
                if self.tile_matrix[i][j].is_on:
                    str += '0 '
                else:
                    str += 'X '
        return str
    
    # put into a tile a new block
    def set_tile(self, block : Block, is_in_stack = False):
        tile = self.tile_matrix[ROWS - (block.y // TILE_SCALE)][(block.x // TILE_SCALE)]
        tile.set_values(block, True, is_in_stack)

        block.tile = tile
    
    # draw all grid
    def draw(self):
        for row in self.tile_matrix:
            for tile in row:
                if tile.is_on:
                    tile.block.draw()

    def clear(self):
        for row in self.tile_matrix:
            for tile in row:
                tile.is_on = False
                tile.block = None
    
    # called each frame to update all the tiles while the blocks switching places
    def refresh(self, current_tetron : Tetron):
        self.clear()
        for block in current_tetron.block_list:
            self.set_tile(block)
        for block in self.block_stack.get_block_list():
            self.set_tile(block, True)
        
    def cant_move_horizontally(self, block : Block, direction):
        if block.tile is None:
            return 
    
        i,j = block.tile.row, block.tile.col
        
        screen_collision = (j + direction) < 0 or (j + direction) >= COLLUMNS
        if screen_collision:
            return True

        stack_collision = self.tile_matrix[i][j + direction].is_on and self.tile_matrix[i][j + direction].is_in_stack

        return stack_collision

    def cant_move_down(self, block : Block):
        i,j = block.tile.row, block.tile.col
        screen_collision = i-1 <= 0 
        if screen_collision:
            return True
        
        stack_collision = self.tile_matrix[i-1][j].is_on and self.tile_matrix[i-1][j].is_in_stack
        return stack_collision

    def overlap_collision(self, block : Block):
        i,j = ROWS - (block.y // TILE_SCALE), (block.x // TILE_SCALE)
        if j >= COLLUMNS or j < 0 or i <= 0:
            return True
        return self.tile_matrix[i][j].is_on and self.tile_matrix[i][j].is_in_stack

class Game:
    def __init__(self):
        self.grid : Grid = Grid()
        self.current_tetron = Tetron_L0()
        # how much rows should be cleared next frame
        self.clear_row_call_count = 0
        self.delay_to_place_tetron = PLACE_TETRON_MIN_WAIT
        self.max_delay_to_place_tetron = PLACE_TETRON_MAX_WAIT
        self.place_tetron_phase = False

    def move_tetron_horizontally(self, direction):
        self.current_tetron.move_horizontal(direction)

    def rotate_tetron(self):
        if self.place_tetron_phase:
            self.delay_to_place_tetron += ROTATE_PLACE_TETRON_INCREMENT
        self.current_tetron.rotate()

    # called each frame
    def update_grid(self):
        self.grid.refresh(self.current_tetron)
        update_visuals()

        self.current_tetron.move_down()
        
        if len(display_text_queue) > 0:
            sleep(1)
            display_text_queue.pop(0)
        
        global score

        # add to score the proper amount according to clear count
        if self.clear_row_call_count > 0 and self.clear_row_call_count < 4:
            score += SCORING_REWARDS[self.clear_row_call_count-1]
        
        # tetris if 4 rows cleared
        elif self.clear_row_call_count >= 4:
            score += SCORING_REWARDS[3]
            display_text_queue.append('YAEL <3')
            display_text_queue.append('TETRIS')

        # clear each row
        while self.clear_row_call_count:
            self.grid.block_stack.clear_line()
            self.clear_row_call_count -= 1

        # try to place tetron if collided with wall or block
        if self.current_tetron.check_vertical_collsion():
            if self.place_tetron_phase:
                self.try_to_place_tetron()
            else:
                self.place_tetron_phase = True
                self.delay_to_place_tetron = PLACE_TETRON_MIN_WAIT
                self.max_delay_to_place_tetron = PLACE_TETRON_MAX_WAIT
        else:
            self.place_tetron_phase = False

    def instantiate_new_tetron(self):
        type_list = [Tetron_L0, Tetron_L1, Tetron_I, Tetron_O, Tetron_T, Tetron_Z0, Tetron_Z1, Tetron_J, Tetron_U, Tetron_L2, Tetron_L3, Tetron_Z2, Tetron_Z3, Tetron_X, Tetron_Y]        
        self.current_tetron = type_list[randint(0,TETRON_KINDS)]()

    def try_to_place_tetron(self):
        # each frame decrease delay by the time between frames 
        self.delay_to_place_tetron -= DELTA_TIME
        self.max_delay_to_place_tetron -= DELTA_TIME
        # if delay never 0 max will certenly reach zero after its max wait time
        if self.delay_to_place_tetron < 0 or self.max_delay_to_place_tetron < 0:
            self.place_tetron_phase = False
            self.place_tetron()

    def place_tetron(self):      
        # save last tetron as placed block and delete the original
        tetron_blocks = self.current_tetron.block_list.copy()
        for block in tetron_blocks:
            self.grid.block_stack.add_block(block)
        del self.current_tetron

        self.instantiate_new_tetron()
        self.clear_row_call_count = self.grid.block_stack.check_for_clear()


class Tetron_L0(Tetron):
    def __init__(self):
        represent_matrix = [[0,0,0,0], [0,1,0,0], [0,1,1,1], [0,0,0,0]]
        color = (52,195,235)
        super().__init__(represent_matrix, color)

class Tetron_L1(Tetron):
    def __init__(self):
        represent_matrix = [[0,0,0,0], [0,1,1,1], [0,0,0,1], [0,0,0,0]]
        color = (52,195,235)
        super().__init__(represent_matrix, color)

class Tetron_T(Tetron):
    def __init__(self):
        represent_matrix = [[0,0,0,0], [0,1,0,0], [1,1,1,0], [0,0,0,0]]
        color = (235, 52, 229)
        super().__init__(represent_matrix, color)

class Tetron_O(Tetron):
    def __init__(self):
        represent_matrix = [[0,0,0,0], [0,1,1,0], [0,1,1,0], [0,0,0,0]]
        color = (235, 64, 52)
        super().__init__(represent_matrix, color)

class Tetron_I(Tetron):
    def __init__(self):
        represent_matrix = [[0,0,0,0], [1,1,1,1], [0,0,0,0], [0,0,0,0]]
        color = (95, 235, 52)
        super().__init__(represent_matrix, color)

class Tetron_Z0(Tetron):
    def __init__(self):
        represent_matrix = [[0,0,0,0], [0,1,1,0], [0,0,1,1], [0,0,0,0]]
        color = (230, 215, 55)
        super().__init__(represent_matrix, color)

class Tetron_Z1(Tetron):
    def __init__(self):
        represent_matrix = [[0,0,0,0], [0,1,1,0], [1,1,0,0], [0,0,0,0]]
        color = (230, 215, 55)
        super().__init__(represent_matrix, color)

class Tetron_X(Tetron):
    def __init__(self):
        represent_matrix = [[0,1,0,1], [0,0,1,0], [0,1,0,1], [0,0,0,0]]
        color = (163, 49, 212)
        super().__init__(represent_matrix, color)

class Tetron_Y(Tetron):
    def __init__(self):
        represent_matrix = [[0,0,0,0], [0,0,1,0], [0,1,1,1], [0,1,0,1]]
        color = (163, 49, 212)
        super().__init__(represent_matrix, color)

class Tetron_U(Tetron):
    def __init__(self):
        represent_matrix = [[0,0,0,0], [0,1,0,1], [0,1,1,1], [0,0,0,0]]
        color = (212, 49, 147)
        super().__init__(represent_matrix, color)

class Tetron_L2(Tetron):
    def __init__(self):
        represent_matrix = [[0,1,0,0], [0,1,0,0], [0,1,1,1], [0,0,0,0]]
        color = (194, 245, 66)
        super().__init__(represent_matrix, color)

class Tetron_L3(Tetron):
    def __init__(self):
        represent_matrix = [[0,0,0,0], [0,1,1,1], [0,1,0,0], [0,1,0,0]]
        color = (194, 245, 66)
        super().__init__(represent_matrix, color)

class Tetron_Z2(Tetron):
    def __init__(self):
        represent_matrix = [[0,1,0,0], [0,1,1,0], [0,0,1,1], [0,0,0,0]]
        color = (230, 175, 55)
        super().__init__(represent_matrix, color)

class Tetron_Z3(Tetron):
    def __init__(self):
        represent_matrix = [[0,0,1,0], [0,1,1,0], [1,1,0,0], [0,0,0,0]]
        color = (230, 175, 55)
        super().__init__(represent_matrix, color)

class Tetron_J(Tetron):
    def __init__(self):
        represent_matrix = [[0,0,0,0], [0,1,1,0], [0,0,1,0], [0,0,0,0]]
        color = (212, 49, 49)
        super().__init__(represent_matrix, color)
                    
def update_visuals():
    screen.fill((0, 0, 0))
    
    game.grid.draw()
    display_score()
    
    # tetris wait to be printed to screen
    if len(display_text_queue) > 0:
        display_text(display_text_queue[0])

    pygame.display.update()

def display_score():
    font = pygame.font.Font('PressStart2P-Regular.ttf', 20)
    score_text = font.render(f'Score:{score}', True, WHITE)
    screen.blit(score_text, (10,10))

def display_text(text):
    font = pygame.font.Font('PressStart2P-Regular.ttf', 22)
    score_text = font.render(text, True, WHITE)
    screen.blit(score_text, (25,230))

# --global variables--
game : Game = None
score = 0
display_text_queue = []

def choose_options():
    options = '''
    *******************
    --WELCOME TO TETRIS--
    CHOOSE GAME OPTION
    
    INSERT A NUMBER TO CHOOSE AN OPTION
    AND THEN ENTER TO START THE GAME

    1 : CLASSIC
    2 : WIDE SCREEN
    3 : FAST
    4 : MORE SHAPES
    5 : ULTRA HARD SHAPES
    6 : FAST + MORE SHAPES
    7 : WIDE SCREEN + HARD SHAPES
    8 : IMPOSSIBLE (FAST + ULTRA HARD SHAPES)
    ******************\n\n
    '''
    print(options)
    option = int(input())

    global screen, WINDOW_SCALE, VERTICAL_SPEED_BONUS, VERTICAL_SPEED_FAST_FORWARD, VERTICAL_SPEED_INCREMENT, TETRON_KINDS, VERTICAL_SPEED, ROWS, COLLUMNS
    if option is 1:
        return
    # wide screen
    if (option is 2) or (option is 7):
        WINDOW_SCALE = WIDE_WINDOW_SCALE
        ROWS = WINDOW_SCALE[1] // TILE_SCALE
        COLLUMNS = WINDOW_SCALE[0] // TILE_SCALE
        screen = pygame.display.set_mode(WINDOW_SCALE)
    # fast
    if (option is 3) or (option is 6) or (option is 8):
        VERTICAL_SPEED_BONUS = FAST_VERTICAL_SPEED
        VERTICAL_SPEED = VERTICAL_SPEED + FAST_VERTICAL_SPEED
        VERTICAL_SPEED_FAST_FORWARD = FAST_VERTICAL_SPEED_FAST_FORWARD
        VERTICAL_SPEED_INCREMENT = FAST_VERTICAL_SPEED_INCREMENT
    # more shapes
    if (option is 4) or (option is 6):
        TETRON_KINDS = MORE_SHAPES_TETRON_KINDS
    # more hard shapes
    if (option is 5) or (option is 7) or (option is 8):
        TETRON_KINDS = HARD_SHPES_TETRON_KINDS


def main():
    # set options
    choose_options()
        
    pygame.init()
    pygame.font.init()

    run = True
    is_right_down = False
    is_left_down = False
    is_right = True

    clock = pygame.time.Clock()

    global game
    game = Game()
    pause = False

    global VERTICAL_SPEED, VERTICAL_SPEED_FAST_FORWARD

    while run:
        clock.tick(FPS)

        if not pause:
            game.update_grid()

        if is_right_down or is_left_down:
            
            if is_right:
                game.move_tetron_horizontally(1)
            else:
                game.move_tetron_horizontally(-1)
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    is_right_down = True
                    is_right = True
                if event.key == pygame.K_LEFT:
                    is_left_down = True
                    is_right = False
                if event.key == pygame.K_UP:
                    game.rotate_tetron()
                if event.key == pygame.K_DOWN:
                    VERTICAL_SPEED = VERTICAL_SPEED_FAST_FORWARD
                if event.key == pygame.K_ESCAPE:
                    pause = not pause
            
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT: 
                    is_right_down = False
                if event.key == pygame.K_LEFT:
                    is_left_down = False
                if event.key == pygame.K_DOWN:
                    VERTICAL_SPEED = 1 + VERTICAL_SPEED_BONUS
       
    pygame.quit()

if __name__ == "__main__":
    main()