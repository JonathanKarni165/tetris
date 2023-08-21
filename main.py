import pygame
from time import sleep
from pygame import draw
from random import randint


WINDOW_SCALE = (300, 500)
TILE_SCALE = 20
BLOCK_SCALE = 18

FPS = 60
HORIZONTAL_SPEED = 1
VERTICAL_SPEED = 2
LEN = 4

WHITE = (255,255,255)
BLACK = (0,0,0)


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

    def move_down(self):
        self.y += TILE_SCALE

    def move_horizontal(self, direction):
        self.x += direction * TILE_SCALE

    def draw(self):
        self.rect = pygame.Rect(self.x, self.y, self.width, self.hight)
        draw.rect(screen, self.color, self.rect)
    
    def position_overlap(self, other_down):
        return self.x == other_down.x and self.y == other_down.y - TILE_SCALE


class Tetron:
    def __init__(self, represent_matrix : list[list], color : tuple):
        self.represent_matrix = represent_matrix
        self.block_list : list[Block] = []
        self.ghost_list : list[Block] = []
        self.all_blocks : list[Block] = []

        self.move_delay_frames = FPS
        self.move_delay_frames_timer_y = FPS
        self.move_delay_frames_timer_x = FPS

        self.x = 7 * TILE_SCALE
        self.y = 20
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
         

    def move_down(self):
        self.move_delay_frames_timer_y -= VERTICAL_SPEED
        if self.move_delay_frames_timer_y > 0:
            return

        self.move_delay_frames_timer_y = self.move_delay_frames
        for block in self.all_blocks:
            block.move_down()
            
    
        self.y += TILE_SCALE

    def move_horizontal(self, direction, grid_blocks = None, no_check = False):
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
                self.move_horizontal(-1)
                return
            elif block.x < 0:
                self.move_horizontal(1)
                return

    # moves back tetron if collided with grid
    def grid_constraint(self, direction, grid_blocks):
        for my_block in self.block_list:
            for grid_block in grid_blocks:
                if my_block.position_overlap(grid_block):
                    self.move_horizontal(-direction, grid_blocks)
                    return
    
    # rotate back tetron if collided with grid
    def rotate_grid_constraint(self, grid_blocks):
        for my_block in self.block_list:
            for grid_block in grid_blocks:
                if my_block.position_overlap(grid_block):
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
                if my_block.y == 480:
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
          
class Block_Stack:
    def __init__(self):
        self.stack : list[list[Block]] = []
        self.rows_to_clear = []
    
    def add_block(self, block : Block):
        block_level = (WINDOW_SCALE[1] - block.y) // TILE_SCALE - 1

        while len(self.stack) < block_level + 1:
            self.stack.append([])
        self.stack[block_level].append(block)
    
    def clear_line(self):
        row_index = self.rows_to_clear.pop()
        sleep(0.3)
        
        # drop down all upper levels
        for upper_row_index in range(row_index + 1, len(self.stack)):
            for block in self.stack[upper_row_index]:
                block.move_down()
        
        self.stack.pop(row_index)
    
    # returns number of clears
    def check_for_clear(self):
        clear_count = 0
        row_len_list = []
        for level_index in range(len(self.stack)):
            row_len_list.append(len(self.stack[level_index]))
            if len(self.stack[level_index]) == WINDOW_SCALE[0] // TILE_SCALE:
                print('line clear ', level_index)
                self.rows_to_clear.append(level_index)

                for block in self.stack[level_index]:
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
        self.currentTetron = Tetron_L()
        self.block_stack : Block_Stack = Block_Stack()
        self.clear_row_call_count = 0
    
    def move_tetron_horizontally(self, direction):
        self.currentTetron.move_horizontal(direction, self.block_stack.get_block_list())

    def rotate_tetron(self):
        self.currentTetron.rotate(self.block_stack.get_block_list())

    def update_grid(self):
        update(self.currentTetron, self.block_stack.get_block_list())

        self.currentTetron.move_down()
        
        while(self.clear_row_call_count):
            self.block_stack.clear_line()
            self.clear_row_call_count -= 1

        if self.currentTetron.check_vertical_collsion(self.block_stack.get_block_list()):
            self.place_tetron()
        

    def instantiate_new_tetron(self):
        type_list = [Tetron_L, Tetron_T, Tetron_I, Tetron_O, Tetron_X, Tetron_Y]        
        self.currentTetron = type_list[randint(0,2)]()

    def place_tetron(self):
        # save last tetron as placed block
        tetron_blocks = self.currentTetron.block_list.copy()
        for block in tetron_blocks:
            self.block_stack.add_block(block)
        del self.currentTetron

        self.instantiate_new_tetron()
        self.clear_row_call_count = self.block_stack.check_for_clear()

        # increase game speed
        global VERTICAL_SPEED
        # VERTICAL_SPEED *= 1.1

class Tetron_L(Tetron):
    def __init__(self):
        represent_matrix = [[0,0,0,0], [0,1,0,0], [0,1,1,1], [0,0,0,0]]
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

class Tetron_X(Tetron):
    def __init__(self):
        represent_matrix = [[0,0,0,0], [0,1,1,0], [0,0,1,1], [0,0,0,0]]
        color = (230, 215, 55)
        super().__init__(represent_matrix, color)

class Tetron_Y(Tetron):
    def __init__(self):
        represent_matrix = [[0,0,0,0], [1,1,1,0], [0,0,1,0], [0,0,1,0]]
        color = (230, 215, 55)
        super().__init__(represent_matrix, color)
                    
def update(tetron : Tetron, blocks: list[Block]):
    screen.fill((0, 0, 0))

    tetron.move_down()
    tetron.draw()

    for block in blocks:
        block.draw()

    pygame.display.update()




def main():
    run = True

    clock = pygame.time.Clock()
    grid = Grid()
    pause = False

    while run:
        clock.tick(FPS)

        if not pause:
            grid.update_grid()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    grid.move_tetron_horizontally(1)
                if event.key == pygame.K_LEFT:
                    grid.move_tetron_horizontally(-1)
                if event.key == pygame.K_DOWN:
                    grid.rotate_tetron()
                if event.key == pygame.K_ESCAPE:
                    pause = not pause
            


    pygame.quit()


if __name__ == "__main__":
    main()
