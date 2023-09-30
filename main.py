import pygame
from time import sleep
from pygame import draw
from random import randint
import threading


WINDOW_SCALE = (300, 500)
TILE_SCALE = 20
BLOCK_SCALE = 18

FPS = 60
DELTA_TIME = 1 / FPS
HORIZONTAL_DELAY_FRAMES = 5
HORIZONTAL_SPEED = 1
VERTICAL_SPEED = 1.0
VERTICAL_SPEED_INCREMENT = 0.0
VERTICAL_SPEED_FAST_FORWARD = 5.0
ADD_TO_SPEED = 0.4
PLACE_TETRON_MAX_WAIT = 3
PLACE_TETRON_MIN_WAIT = 1
PLACE_TETRON_INCREMENT = 0.4
LEN = 4

WHITE = (255,255,255)
BLACK = (0,0,0)

SCORING_REWARDS = (40,100,300,1200)
score = 0

display_text_queue = []

pygame.init()
pygame.font.init()

screen = pygame.display.set_mode(WINDOW_SCALE)

class Block(pygame.sprite.Sprite):
    def __init__(self, color, ghost = False):
        self.x = 0
        self.y = 0

        self.width = BLOCK_SCALE
        self.hight = BLOCK_SCALE

        if ghost:
            self.color = BLACK
        else:
            self.color = color

        self.ghost = ghost

        self.rect = pygame.Rect(self.x, self.y, self.width, self.hight)
        draw.rect(screen, self.color, self.rect)

    def move_up(self):
        self.y -= TILE_SCALE

    def move_down(self):
        self.y += TILE_SCALE

    def move_horizontal(self, direction):
        self.x += direction * TILE_SCALE

    def draw(self):
        self.rect = pygame.Rect(self.x, self.y, self.width, self.hight)
        draw.rect(screen, self.color, self.rect)
    
    def out_of_bounds(self):
        return self.x >= WINDOW_SCALE[0] or self.x < 0 or self.y >= WINDOW_SCALE[1]
    
    def position_overlap(self, other_down):
        return self.x == other_down.x and self.y == other_down.y - TILE_SCALE


class Tetron:
    def __init__(self, represent_matrix : list[list], color : tuple):
        self.represent_matrix = represent_matrix
        self.block_list : list[Block] = []
        self.ghost_list : list[Block] = []
        self.all_blocks : list[Block] = []

        self.move_delay_frames_y = FPS
        self.move_delay_frames_x = HORIZONTAL_DELAY_FRAMES
        self.move_delay_frames_timer_y = FPS
        self.move_delay_frames_timer_x = HORIZONTAL_DELAY_FRAMES

        self.x = 7 * TILE_SCALE
        self.y = TILE_SCALE
        self.color = color

        for i in range(LEN):
            for j in range(LEN):

                # create a ghost block if bit is 0 (just for testing)
                is_ghost = not bool(self.represent_matrix[i][j])
                my_block = Block(color, is_ghost)

                my_block.x = self.x + (j * TILE_SCALE)
                my_block.y = self.y + (i * TILE_SCALE)

                if is_ghost:
                    self.ghost_list.append(my_block)
                else:
                    self.block_list.append(my_block)

        
        self.all_blocks.extend(self.block_list)
        self.all_blocks.extend(self.ghost_list)

        # first rotation initialization
        self.rotate()
    
    def draw(self):
        for block in self.all_blocks:
            block.draw()
    
    def move_up(self):
        for block in self.all_blocks:
            block.move_up()
        self.y -= TILE_SCALE

    def move_down(self, grid_blocks):
        self.move_delay_frames_timer_y -= VERTICAL_SPEED
        if self.move_delay_frames_timer_y > 0 or self.check_vertical_collsion(grid_blocks):
            return

        self.move_delay_frames_timer_y = self.move_delay_frames_y
        for block in self.all_blocks:
            block.move_down()
        self.y += TILE_SCALE
        
        self.screen_constraint()    

    def move_horizontal(self, direction, grid_blocks = None, no_check = False):
        global HORIZONTAL_DELAY_FRAMES
        self.move_delay_frames_timer_x -= 1
        if self.move_delay_frames_timer_x > 0 and no_check is False:
            return
        
        self.move_delay_frames_timer_x = HORIZONTAL_DELAY_FRAMES

        for block in self.all_blocks:
            block.move_horizontal(direction)
        
        self.x += direction * TILE_SCALE
        print('move', direction)
        if no_check:
            return
        
        self.screen_constraint()
        if grid_blocks is not None:
            self.grid_constraint(direction, grid_blocks)
        
    
    # moves back tetron if collided with wall
    def screen_constraint(self):
        for block in self.block_list:
            if block.x >= WINDOW_SCALE[0]:
                self.move_horizontal(-1, no_check=True)
                return
            elif block.x < 0:
                self.move_horizontal(1, no_check=True)
                return
            elif block.y >= WINDOW_SCALE[1]:
                self.move_up()
                return

    # moves back tetron if collided with grid
    def grid_constraint(self, direction, grid_blocks):
        for my_block in self.block_list:
            for grid_block in grid_blocks:
                if my_block.position_overlap(grid_block):
                    self.move_horizontal(-direction, grid_blocks, no_check=True)
                    return
    
    # rotate back tetron if collided with grid
    def rotate_grid_constraint(self, grid_blocks):
        for my_block in self.block_list:
            for grid_block in grid_blocks:
                if my_block.position_overlap(grid_block):
                    print('position overlap new rotation')
                    self.rotate(grid_blocks)
                    return
    
    # rotate back tetron if collided with screen
    def rotate_screen_constraint(self, grid_blocks = None):
        for my_block in self.block_list:
            if my_block.out_of_bounds():
                self.rotate(grid_blocks)
                return
                
    def check_vertical_collsion(self, blocks : list[Block]):

        # collision with blocks 
        for block in blocks:
            for my_block in self.block_list:
                if my_block.position_overlap(block):
                    return True
        
        # collision with screen
        for my_block in self.block_list:
                if my_block.y == WINDOW_SCALE[1] - TILE_SCALE:
                    return True
                
    def rotate(self, grid_blocks=None):
        represent_matrix_temp = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
        for i in range(LEN):
            for j in range(LEN):
                represent_matrix_temp[LEN-j-1][i] = self.represent_matrix[i][j]

        self.represent_matrix = represent_matrix_temp.copy()
        
        block_index = 0
        ghost_index = 0

        for i in range(LEN):
            for j in range(LEN):
                if self.represent_matrix[i][j]:
                    self.block_list[block_index].x = self.x + (i * TILE_SCALE)
                    self.block_list[block_index].y = self.y + (j * TILE_SCALE)
                    block_index += 1
                else:
                    self.ghost_list[ghost_index].x = self.x + (i * TILE_SCALE)
                    self.ghost_list[ghost_index].y = self.y + (j * TILE_SCALE)
                    ghost_index += 1

        self.screen_constraint()
        
        if grid_blocks is not None:
            self.rotate_grid_constraint(grid_blocks)
            self.rotate_screen_constraint(grid_blocks)
        else:
            self.rotate_screen_constraint()
          
class Block_Stack:
    def __init__(self):
        self.stack : list[list[Block]] = []
        self.rows_to_clear = []

    def __str__(self):
        return str([len(row) for row in self.stack])
    
    def add_block(self, block : Block):
        block_level = (WINDOW_SCALE[1] - block.y) // TILE_SCALE - 1

        while len(self.stack) < block_level + 1:
            self.stack.append([])
        self.stack[block_level].append(block)
        
        if len(self.stack) >= (WINDOW_SCALE[1] // TILE_SCALE) - 2:
            print('end')
            exit(0)
    
    def clear_line(self):
        row_index = self.rows_to_clear.pop()
        sleep(0.3)
        global VERTICAL_SPEED_INCREMENT
        # increase speed
        VERTICAL_SPEED_INCREMENT += 0.3

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

class Grid:
    def __init__(self):
        self.currentTetron = Tetron_L0()
        self.block_stack : Block_Stack = Block_Stack()
        self.clear_row_call_count = 0
        self.delay_to_place_tetron = PLACE_TETRON_MIN_WAIT
        self.max_delay_to_place_tetron = PLACE_TETRON_MAX_WAIT
        self.place_tetron_phase = False
    
    def move_tetron_horizontally(self, direction):
        self.currentTetron.move_horizontal(direction, self.block_stack.get_block_list())

    def rotate_tetron(self):
        if self.place_tetron_phase:
            self.delay_to_place_tetron += PLACE_TETRON_INCREMENT
        self.currentTetron.rotate(self.block_stack.get_block_list())

    def update_grid(self):
        
        update(self.currentTetron, self.block_stack.get_block_list())
        self.currentTetron.move_down(self.block_stack.get_block_list())
        
        if len(display_text_queue) > 0:
            sleep(1)
            display_text_queue.pop(0)
        
        global score

        if self.clear_row_call_count > 0 and self.clear_row_call_count < 4:
            score += SCORING_REWARDS[self.clear_row_call_count-1]
        
        # tetris
        elif self.clear_row_call_count >= 4:
            score += SCORING_REWARDS[3]
            display_text_queue.append('YAEL <3')
            display_text_queue.append('TETRIS')
            
        while self.clear_row_call_count:
            self.block_stack.clear_line()
            self.clear_row_call_count -= 1

        if self.currentTetron.check_vertical_collsion(self.block_stack.get_block_list()):
            if self.place_tetron_phase:
                self.try_to_place_tetron()
            else:
                self.place_tetron_phase = True
                self.delay_to_place_tetron = PLACE_TETRON_MIN_WAIT
                self.max_delay_to_place_tetron = PLACE_TETRON_MAX_WAIT
        else:
            self.place_tetron_phase = False


        

    def instantiate_new_tetron(self):
        type_list = [Tetron_L0, Tetron_L1, Tetron_I, Tetron_O, Tetron_T, Tetron_Z0, Tetron_Z1, Tetron_J, Tetron_X, Tetron_U]        
        self.currentTetron = type_list[randint(0,6)]()

    def try_to_place_tetron(self):

        self.delay_to_place_tetron -= DELTA_TIME
        self.max_delay_to_place_tetron -= DELTA_TIME
        if self.delay_to_place_tetron < 0 or self.max_delay_to_place_tetron < 0:
            self.place_tetron_phase = False
            self.place_tetron()

    def place_tetron(self):      
        # save last tetron as placed block
        tetron_blocks = self.currentTetron.block_list.copy()
        for block in tetron_blocks:
            self.block_stack.add_block(block)
        del self.currentTetron

        print(self.block_stack)

        self.instantiate_new_tetron()
        self.clear_row_call_count = self.block_stack.check_for_clear()


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
        color = (49, 212, 60)
        super().__init__(represent_matrix, color)

class Tetron_U(Tetron):
    def __init__(self):
        represent_matrix = [[0,0,0,0], [0,1,0,1], [0,1,1,1], [0,0,0,0]]
        color = (212, 49, 147)
        super().__init__(represent_matrix, color)

class Tetron_J(Tetron):
    def __init__(self):
        represent_matrix = [[0,0,0,0], [0,1,0,0], [0,0,1,0], [0,0,0,0]]
        color = (212, 49, 49)
        super().__init__(represent_matrix, color)
                    
def update(tetron : Tetron, blocks: list[Block]):
    screen.fill((0, 0, 0))

    tetron.draw()

    for block in blocks:
        block.draw()
    display_score()
    
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

def main():
    run = True
    is_down = False
    is_right = True
    vertical_speed_temp = 0

    clock = pygame.time.Clock()
    grid = Grid()
    pause = False

    global VERTICAL_SPEED, VERTICAL_SPEED_FAST_FORWARD

    while run:
        clock.tick(FPS)

        if not pause:
            grid.update_grid()

        if is_down:
            if is_right:
                grid.move_tetron_horizontally(1)
            else:
                grid.move_tetron_horizontally(-1)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    is_right = True
                    is_down = True
                if event.key == pygame.K_LEFT:
                    is_right = False
                    is_down = True
                if event.key == pygame.K_UP:
                    grid.rotate_tetron()
                if event.key == pygame.K_DOWN:
                    VERTICAL_SPEED = VERTICAL_SPEED_FAST_FORWARD
                if event.key == pygame.K_ESCAPE:
                    pause = not pause


            
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT or event.key == pygame.K_LEFT:
                    is_down = False
                if event.key == pygame.K_DOWN:
                    VERTICAL_SPEED = 1 + VERTICAL_SPEED_INCREMENT
       
    pygame.quit()


if __name__ == "__main__":
    main()