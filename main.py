import pygame
from pygame import draw

WINDOW_SCALE = (300, 500)
TILE_SCALE = 20
BLOCK_SCALE = 18

FPS = 60
HORIZONTAL_SPEED = 1
VERTICAL_SPEED = 1
LEN = 4

WHITE = (255,255,255)

screen = pygame.display.set_mode(WINDOW_SCALE)

class Block(pygame.sprite.Sprite):
    def __init__(self, color, ghost = False):
        self.x = 0
        self.y = 0

        self.width = BLOCK_SCALE
        self.hight = BLOCK_SCALE

        if ghost:
            self.color = WHITE
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
    
    def draw(self):
        print(self.x)
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

    def move_horizontal(self, direction):
        for block in self.all_blocks:
            block.move_horizontal(direction)
        
        self.screen_constraint()
        
        self.x += direction * TILE_SCALE
    
    def screen_constraint(self):
        for block in self.block_list:
            if block.x >= WINDOW_SCALE[0]:
                self.move_horizontal(-1)
                break
            if block.x < 0:
                self.move_horizontal(1)
                break

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
                
    def rotate(self):

        # check if rotation will clip
        for i in range(LEN):
            for j in range(LEN):
                # block is on and is out of left screen bounds
                if self.x + ((j + 1) * TILE_SCALE) <= 0 and self.represent_matrix[i][j]:
                    # return from corner
                    self.move_horizontal(1)
                    break
                # block is on and is out of right screen bounds
                if self.x + ((j + 1) * TILE_SCALE) >= WINDOW_SCALE[0] and self.represent_matrix[i][j]:
                    # return from corner
                    self.move_horizontal(-1)
                    break

        represent_matrix_temp = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
        for i in range(LEN):
            for j in range(LEN):
                represent_matrix_temp[j][i] = self.represent_matrix[LEN-i-1][j]

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
                 

class Grid:
    def __init__(self):
        self.currentTetron = Tetron_L()
        self.blocks : list[Block] = []
    
    def updateGrid(self):
        self.currentTetron.move_down()
        
        if self.currentTetron.check_vertical_collsion(self.blocks):
            self.placeTetron()
        
        update(self.currentTetron, self.blocks)

    def placeTetron(self):
        self.blocks.extend(self.currentTetron.block_list.copy())
        del self.currentTetron
        self.currentTetron = Tetron_L()


class Tetron_L(Tetron):
    def __init__(self):
        represent_matrix = [[0,0,0,0], [0,1,0,0], [0,1,1,1], [0,0,0,0]]
        color = (52,195,235)
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

    while run:
        clock.tick(FPS)
        grid.updateGrid()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    grid.currentTetron.move_horizontal(1)
                if event.key == pygame.K_LEFT:
                    grid.currentTetron.move_horizontal(-1)
                if event.key == pygame.K_DOWN:
                    grid.currentTetron.rotate()
    pygame.quit()


if __name__ == "__main__":
    main()
