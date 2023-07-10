import pygame
from pygame import draw

WINDOW_SCALE = (300, 500)
TILE_SCALE = 20
BLOCK_SCALE = 18

FPS = 60
HORIZONTAL_SPEED = 1
VERTICAL_SPEED = 1
LEN = 4

screen = pygame.display.set_mode(WINDOW_SCALE)

class block(pygame.sprite.Sprite):
    def __init__(self, color):
        self.x = 0
        self.y = 0

        self.width = BLOCK_SCALE
        self.hight = BLOCK_SCALE

        self.color = color

        

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

        self.move_delay_frames = FPS
        self.move_delay_frames_timer_y = FPS
        self.move_delay_frames_timer_x = FPS

        self.x = 7 * TILE_SCALE
        self.y = 20
        self.color = color

        for i in range(LEN):
            for j in range(LEN):
                if self.represent_matrix[i][j]:
                    my_block = block(color)

                    my_block.x = self.x + (i * TILE_SCALE)
                    my_block.y = self.y + (j * TILE_SCALE)

                    self.block_list.append(my_block)

        
        blocks.extend(self.block_list)
    
    def draw(self):
        for block in self.block_list:
            block.draw()

    def move_down(self):
        self.move_delay_frames_timer_y -= VERTICAL_SPEED
        if self.move_delay_frames_timer_y > 0:
            return

        self.move_delay_frames_timer_y = self.move_delay_frames
        for block in self.block_list:
            block.move_down()
    
        self.y += TILE_SCALE

    def move_horizontal(self, direction):
        for block in self.block_list:
            block.move_horizontal(direction)
        
        self.x += direction * TILE_SCALE
    
    def rotate(self):

        represent_matrix_temp = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
        for i in range(LEN):
            for j in range(LEN):
                represent_matrix_temp[j][i] = self.represent_matrix[LEN-i-1][j]

        self.represent_matrix = represent_matrix_temp.copy()
        print(self.represent_matrix)
        
        block_index = 0
        
        for i in range(LEN):
            for j in range(LEN):
                if self.represent_matrix[i][j]:
                    print(self.represent_matrix)
                    self.block_list[block_index].x = self.x + (i * TILE_SCALE)
                    self.block_list[block_index].y = self.y + (j * TILE_SCALE)
                    block_index += 1
        

        print(len(self.block_list))

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
                    print('hi')
    pygame.quit()


if __name__ == "__main__":
    main()