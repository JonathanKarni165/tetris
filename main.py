import pygame
from pygame import draw

WINDOW_SCALE = (300, 500)
BLOCK_SCALE = (20, 20)

FPS = 60
HORIZONTAL_SPEED = 1
VERTICAL_SPEED = 1

screen = pygame.display.set_mode(WINDOW_SCALE)


class block(pygame.sprite.Sprite):
    def __init__(self, color):

        self.x = 0
        self.y = 0

        self.width = BLOCK_SCALE[0]
        self.hight = BLOCK_SCALE[1]

        self.color = color

        self.move_delay_frames = FPS
        self.move_delay_frames_timer_y = FPS
        self.move_delay_frames_timer_x = FPS

        self.rect = pygame.Rect(self.x, self.y, self.width, self.hight)
        draw.rect(screen, self.color, self.rect)

    def move_down(self):

        self.move_delay_frames_timer_y -= VERTICAL_SPEED
        if self.move_delay_frames_timer_y > 0:
            return

        self.move_delay_frames_timer_y = self.move_delay_frames
        self.y += BLOCK_SCALE[0]

    def move_horizontal(self, direction):
        self.x += direction * BLOCK_SCALE[0]

    def draw(self):
        self.rect = pygame.Rect(self.x, self.y, self.width, self.hight)
        draw.rect(screen, self.color, self.rect)


def update(b: block):
    screen.fill((0, 0, 0))
    b.move_down()
    b.draw()
    pygame.display.update()


def main():
    run = True
    clock = pygame.time.Clock()
    b = block((3, 252, 215))

    while run:
        update(b)
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    b.move_horizontal(1)
                if event.key == pygame.K_LEFT:
                    b.move_horizontal(-1)
    pygame.quit()


if __name__ == '__main__':
    main()
