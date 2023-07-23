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

class block(pygame.sprite.Sprite):
    def __init__(self, color, ghost = False):
        self.x = 0
        self.y = 0

        self.width = BLOCK_SCALE
        self.hight = BLOCK_SCALE

        if ghost:
            self.color = WHITE
        else:
            self.color = color

        print(self.color)
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

class tetron:
    def __init__(self, represent_matrix : list[list], color : tuple, blocks):
        self.represent_matrix = represent_matrix
        self.block_list : list[block] = []
        self.ghost_list : list[block] = []
        self.all_blocks : list[block] = []

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
                my_block = block(color, is_ghost)

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
            if block.x == WINDOW_SCALE[0]:
                self.move_horizontal(-1)
                break
            if block.x < 0:
                self.move_horizontal(1)
                break
            
    def rotate(self):

        # check if rotation will clip
        for i in range(LEN):
            for j in range(LEN):
                # block is on and is out of left screen bounds
                if self.x + ((j + 1) * BLOCK_SCALE) <= 0 and self.represent_matrix[i][j]:
                    # return from corner
                    self.x += BLOCK_SCALE
                    print('move')
                    break
                # block is on and is out of right screen bounds
                if self.x + ((j + 1) * BLOCK_SCALE) >= WINDOW_SCALE[0] and self.represent_matrix[i][j]:
                    # return from corner
                    self.x -= BLOCK_SCALE
                    print('move')
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
         
        
        


class tetron_L(tetron):
    def __init__(self, blocks):
        represent_matrix = [[0,0,0,0], [0,1,0,0], [0,1,1,1], [0,0,0,0]]
        color = (52,195,235)
        super().__init__(represent_matrix, color, blocks)
                    

def update(tetron : tetron):
    screen.fill((0, 0, 0))

    tetron.move_down()
    tetron.draw()

    pygame.display.update()




def main():
    run = True

    clock = pygame.time.Clock()
    
    blocks : list[block] = []
    b = block((5,255,210))
    t = tetron_L(blocks)
    
    while run:
        update(t)
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    t.move_horizontal(1)
                if event.key == pygame.K_LEFT:
                    t.move_horizontal(-1)
                if event.key == pygame.K_DOWN:
                    t.rotate()
    pygame.quit()


if __name__ == "__main__":
    main()
